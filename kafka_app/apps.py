from django.apps import AppConfig
from kafka_app.tasks import start_kafka_consumer


class KafkaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kafka_app'

    def ready(self):
        start_kafka_consumer.delay()

