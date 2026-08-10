from dotenv import load_dotenv
import os

load_dotenv()

AGENT_URL = os.getenv('AGENT_URL')

DEFAULT_RESPONSE_EXAMPLE = {
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
            "first_seen": "2026-08-07T10:14:12",
            "last_seen": "2026-08-07T10:58:43",
            "possible_cause": "Большое количество одновременно устанавливаемых MQTT соединений",
            "recommendation": "Проверить acceptor timeout и скорость установления соединений"
        },
        {
            "service": "iot-core",
            "level": "ERROR",
            "count": 55,
            "message": "RabbitMQ connection timeout",
            "possible_cause": "Рост времени ответа RabbitMQ",
            "recommendation": "Проверить RabbitMQ connection/channel metrics"
        }
    ]
}

ANALYSIS_TYPES = {
    "errors": "Проанализировать ошибки и исключения в логах, определить причину и критичность.",
    "latency": "Проанализировать задержки и время ответа, найти узкие места производительности.",
    "traffic": "Проанализировать объём трафика и нагрузку на сервисы.",
    "anomalies": "Найти аномалии и нештатное поведение в логах.",
    "summary": "Сформировать краткую сводку активности сервисов за указанный период.",
}
