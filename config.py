from dotenv import load_dotenv
import os

load_dotenv()

AGENT_URL = os.getenv('AGENT_URL')

DEFAULT_RESPONSE_EXAMPLE = {
    "test_id": 1234,
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

ANALYSIS_TYPES = {
    "errors": "Проанализировать ошибки и исключения в логах, определить причину и критичность.",
    "latency": "Проанализировать задержки и время ответа, найти узкие места производительности.",
    "traffic": "Проанализировать объём трафика и нагрузку на сервисы.",
    "anomalies": "Найти аномалии и нештатное поведение в логах.",
    "summary": "Сформировать краткую сводку активности сервисов за указанный период.",
}
