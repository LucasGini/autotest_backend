import importlib
import pkgutil
from abc import ABC, abstractmethod
from confluent_kafka import Consumer


class KafkaConsumerABC(ABC):
    """
    Kafka Consumer ABC
    """

    def consume_messages(self):
        """
        消费消息
        :return:
        """
        pass

    @abstractmethod
    def handler_message(self, msg):
        """
        处理消息
        :param msg:
        :return:
        """
        pass

    @abstractmethod
    def topic_type(self):
        pass
