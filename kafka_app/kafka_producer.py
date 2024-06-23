from abc import ABC, abstractmethod
from confluent_kafka import Producer
from django.conf import settings


class KafkaProducerABC(ABC):
    """
    kafka 生产者抽象类
    """

    def __init__(self):
        self._producer = Producer({
            'bootstrap.servers': settings.KAFKA_SETTINGS.get('bootstrap.servers')
        })

    def get_producer(self):
        """
        获取 Kafka 生产者实例
        """
        return self._producer

    def produce_message(self, topic, message):
        """
        生产消息到指定 Kafka 主题
        """
        producer = self.get_producer()
        producer.produce(topic, message)
        producer.flush()
        producer.poll(0)

    @abstractmethod
    def send_message(self, topic, message):
        """
        发送消息到指定 Kafka 主题
        """
        self.produce_message(topic, message)


class KafkaProducerBase(KafkaProducerABC):
    """
    生产者基础类
    """

    def send_message(self, topic, message):
        super().send_message(topic, message)
