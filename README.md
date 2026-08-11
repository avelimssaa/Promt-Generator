# Log Analysis Service

Инструмент, который можно использовать как прослойку между ИИ-агентом и человеком.

## Требования

1. Развернутый ИИ-агент.

2. Настроенный MCP-сервер в инструментах ИИ-агента.

## Создание контейнера

Можно создать контейнер командами:

```bash
docker build -t log-analysis-service .
docker run -d --name log-analysis --network host -e AGENT_URL=http://127.0.0.1:XXXX log-analysis-service
```

Для запуска не из контейнера:

```bash
uvicorn server:app --reload --port XXXX
```

## Детали

Запросы идут по адресу и порту, указанным при запуске контейнера или uvicorn. 

В запросе обязательно добавлять заголовок авторизации Bearer Token. В качестве токена вставлять токен из файла ~/.openclaw/openclaw.json в блоке gateway.auth.token.

Каждый запрос создает новый чат с ИИ-агентом.

## Содержание запроса:

```json
{
  "test_id": ...,
  "start_time": "-",
  "end_time": "-",
  "services": [
    "iot-core",
    "mqtt-broker",
    "notification",
    "authorization",
    ....
  ],
  "analysis_type": ... 
}
```

Эндпоинт запроса:

POST /api/log-analysis

Примерный ответ агента:

```json
{
    "test_id": ...,
    "start_time": "2026-08-05T04:07:55",
    "end_time": "2026-08-05T21:22:51",
    "status": "issues_found",
    "summary": "Обнаружено 3 типа ошибок",
    "severity": "high",
    "statistics": {
        "errors": 142,
        "warnings": 58
    },
    "issues": [
        {
            "service": "mqtt-broker",
            "level": "ERROR",
            "count": 87,
            "message": "Timeout during MQTT protocol handshake",
            "possible_cause": "Большое количество одновременно устанавливаемых MQTT соединений",
            "recommendation": "Проверить acceptor timeout и скорость установления соединений",
            "KQL-query": 'service_name:"swarm_iot_broker" AND level:"ERROR" AND log:"MQTT handshake timeout"'
        },
        {
            "service": "iot-core",
            "level": "ERROR",
            "count": 55,
            "message": "RabbitMQ connection timeout",
            "possible_cause": "Рост времени ответа RabbitMQ",
            "recommendation": "Проверить RabbitMQ connection/channel metrics",
            "KQL-query": 'service_name:"swarm_iot_core" AND level:"ERROR" AND log:"RabbitMQ" AND log:"timeout"'
        }
    ]
}
```

## Установка ИИ-агента

Установка ИИ агента:

Установить OpenClaw командой

curl -fsSL https://openclaw.ai/install.sh | bash

После установки ввод команд для OpenClaw должен открываться командой openclaw. Если не открывается, попробовать перезапустить терминал.

Когда будет приглашение ввести команду, ввести

setup

yes

yes


Когда появится выбор модели, выбрать Custom Provider

Ввести выданный URL с /v1 в конце, нажать Enter.

Выбрать Paste API Key

В Endpoint Compability выбрать Unknown

Ввести название модели в Model ID

Желательно ограничить возможности ИИ и настроить его на то, чтобы он спрашивал разрешение перед каждым действием командой

openclaw exec-policy set --host gateway --security allowlist --ask always --ask-fallback deny

## Установка MCP-сервера

1) Создать контейнер с MCP-сервером:
```bash
docker run -d --name mcp-iot \
-e ES_URL=http://IP:Port \
-e ES_USERNAME=... \
-e ES_PASSWORD=... \
-p 8080:8080 \
docker.elastic.co/mcp/elasticsearch \
http
```

Можно также передавать API-key:

```bash
docker run -d --name mcp-iot \
-e ES_URL=http://IP:Port \
-e ES_API_KEY="..." \
-p 8080:8080 \
docker.elastic.co/mcp/elasticsearch \
http
```

2) Добавить в инструменты ИИ-агента mcp-сервер. В файл ~/.openclaw/openclaw.json следующий блок:

```json
"mcp": {
"servers": {
"elasticsearch": {
"url": "http://localhost:8080/mcp",
"transport": "streamable-http",
"connectTimeout": 10,
"timeout": 30
}
}
}
```

