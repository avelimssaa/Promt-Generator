from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import json

import requests

import re

from config import AGENT_URL, DEFAULT_RESPONSE_EXAMPLE, ANALYSIS_TYPES


app = FastAPI(
    title="Log Analysis API",
    version="0.2.0",
    description="Принимает JSON с параметрами анализа логов, формирует промт для ИИ и возвращает JSON.",
)

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}


@app.post("/api/log-analysis")
async def log_analysis(request: Request):
    client_api_key = request.headers.get("authorization", "")

    if not client_api_key.lower().startswith("bearer "):

        return JSONResponse({"error": "Missing or invalid Authorization header (expected 'Bearer <key>')"}, status_code=401)

    try:
        body = await request.json()
    except Exception:
        body = {}
    test_id = body.get("test_id")
    start_time = body.get("start_time")
    end_time = body.get("end_time")
    services = body.get("services", [])
    analysis_type = body.get("analysis_type", "errors")

    response_example = body.get("response_example", DEFAULT_RESPONSE_EXAMPLE)

    prompt = _build_prompt(
        test_id=test_id,
        start_time=start_time,
        end_time=end_time,
        services=services,
        analysis_type=analysis_type,
        response_example=response_example,
    )

    result = _send_promt_to_model(prompt, client_api_key)

    return JSONResponse(result)


def _build_prompt(test_id, start_time, end_time, services, analysis_type, response_example=None) -> str:
    analysis_desc = ANALYSIS_TYPES.get(analysis_type, analysis_type)

    services_str = ", ".join(services) if services else "все сервисы"

    lines = [
        "Ты — инженер по нагрузочному тестированию и анализу логов.",
        "",
        f"Необходимо провести анализ логов по следующему запросу:",
        "",
        f"- ID теста: {test_id if test_id is not None else 'не указан'}",
        f"- Период анализа: {start_time or '—'} — {end_time or '—'}",
        f"- Сервисы: {services_str}",
        f"- Тип анализа: {analysis_type} — {analysis_desc}",
        "",
        "Задача:",
        f"{analysis_desc}",
        'Используй для анализа логов только инструменты elasticsearch__search, elasticsearch__list_indices и elasticsearch__esql.',
        'ЗАПРЕЩЕНО использовать elasticsearch__get_mappings — он не работает (возвращает ошибку и ставит инструмент в паузу).'
        'Чтобы узнать поля документа — возьми один документ через elasticsearch__search (size: 1) и посмотри его поля. Не вызывай get_mappings.'
    ]

    if analysis_type == "errors":
        lines.append("- Перечисли найденные ошибки и исключения с временем и сервисом.")
        lines.append("- Укажи вероятную причину и критичность каждой.")
    elif analysis_type == "latency":
        lines.append("- Укажи максимальную/среднюю задержку и в каких сервисах она высокая.")
    elif analysis_type == "traffic":
        lines.append("- Опиши объём сообщений/запросов по сервисам и пиковые нагрузки.")
    elif analysis_type == "anomalies":
        lines.append("- Опиши замеченные аномалии с временными отметками.")
    else:
        lines.append("- Дай развёрнутый ответ.")

    if response_example is not None:
        lines += [
            "",
            "Верни ответ ИСКЛЮЧИТЕЛЬНО в формате JSON, структура и поля которого соответствуют примеру ниже. Не пиши НИЧЕГО после вывода финального JSON. Можешь вообще молча думать, нужно ТОЛЬКО JSON. Оберни итоговый JSON обязательно в конструкцию ```json {...} ```",
            "Значения в примере — лишь для демонстрации формата, заполни их реальными данными из логов.",
            "Пример желаемого ответа:",
            _format_example(response_example),
        ]
    else:
        lines += [
            "",
            "Ответ оформи структурно и по делу, опираясь на логи за указанный период. Верни ответ ИСКЛЮЧИТЕЛЬНО в формате JSON. Не пиши НИЧЕГО после вывода финального JSON. Можешь вообще молча думать, нужно ТОЛЬКО JSON. Оберни итоговый JSON обязательно в конструкцию ```json {...} ```",
        ]
    return "\n".join(lines)


def _format_example(example) -> str:
    return json.dumps(example, ensure_ascii=False, indent=2)

def _send_promt_to_model(prompt, auth_token):

    if not auth_token:
        return {"error": "Missing API key"}

    resp = requests.post(
        f"{AGENT_URL}/v1/responses",
        headers={
            "Authorization": f"{auth_token}",
            "x-openclaw-agent-id": "main",
        },
        json={
            "model": "openclaw",
            "input": prompt,
        },
        timeout=600,
    )
    if resp.status_code != 200:
        return {"error": f"Gateway error {resp.status_code}", "detail": resp.text}

    payload = resp.json()
    text = _extract_agent_text(payload)
    try:
        result = _parse_json_from_text(text)
    except Exception as e:
        result = {"error": "agent returned non-JSON", "detail": str(e), "raw": text}
    return result

def _extract_agent_text(resp_payload):
    texts = []
    for item in resp_payload.get("output", []):
        if item.get("type") == "message":
            for part in item.get("content", []):
                if part.get("type") == "output_text":
                    texts.append(part.get("text", ""))
    return "\n".join(texts)

def _parse_json_from_text(text: str):

    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not m:

        start = text.find("{")
        if start != -1:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        m = re.match(r"\{.*\}", text[start:i+1], re.DOTALL)
                        break
    if not m:
        raise ValueError("No JSON found in agent output")
    return json.loads(m.group(1) if m.lastindex else m.group(0))
