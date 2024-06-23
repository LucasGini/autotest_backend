from celery import shared_task
from kafka_app.consumer.kafka_consumer_base import KafkaConsumerBase
from obsolete.kafka_consumer import KafkaConsumerService
from common.const.case_const import KAFKA_PROJECT_DELETED_TOPIC


@shared_task
def start_kafka_consumer():
    consumer_service = KafkaConsumerBase()
    consumer_service.consume_messages()


# @shared_task
# def start_kafka_consumer_1():
#     consumer_service = KafkaConsumerService(
#         broker_url='localhost:9092',
#         group_id='autotest',
#         topics=[KAFKA_PROJECT_DELETED_TOPIC]
#     )
#     consumer_service.consume_messages()
