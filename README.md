Инструмент, который можно использовать как прослойку между ИИ-агентом и человеком.

Требования:

1. Развернутый ИИ-агент.

2. Настроенный MCP-сервер в инструментах ИИ-агента.

Запросы идут по адресу и порту, указанным при запуске контейнера или uvicorn. 

В запросе обязательно добавлять заголовок авторизации Bearer Token. В качестве токена вставлять токен из файла ~/.openclaw/openclaw.json в блоке gateway.auth.token.

Содержание запроса:

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

Эндпоинт запроса:

POST /api/log-analysis

{
    "status": "...",
    "summary": "...",
    "severity": "...",
    "statistics": {
        "errors": ...,
        "warnings": ...
    },
    "issues": [
        {
            "service": "...",
            "level": "...",
            "count": ...,
            "message": "...",
            "first_seen": "...",
            "last_seen": "...",
            "possible_cause": "...",
            "recommendation": "..."
        },
        ...
    ]
}
