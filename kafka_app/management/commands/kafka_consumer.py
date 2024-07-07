from django.core.management.base import BaseCommand
from kafka_app.consumer.kafka_consumer_base import KafkaConsumerBase


class Command(BaseCommand):
    def handle(self, *args, **options):
        consumer = KafkaConsumerBase()
        consumer.consume_messages()
