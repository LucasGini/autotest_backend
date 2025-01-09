from celery import shared_task
from kafka_app.consumer.kafka_consumer_base import KafkaConsumerBase


@shared_task
def start_kafka_consumer():
    consumer_service = KafkaConsumerBase()
    consumer_service.consume_messages()

