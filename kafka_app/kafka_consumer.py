import importlib
import pkgutil
from abc import ABC, abstractmethod
from confluent_kafka import Consumer
from django.conf import settings


class KafkaConsumerABC(ABC):
    """
    Kafka Consumer ABC
    """

    servers: str = None
    group_id: str = None
    auto_offset_reset: str = None

    def __init__(self):
        self._consumer = Consumer({
            'bootstrap.servers': self.servers or settings.KAFKA_SETTINGS.get('bootstrap.servers'),
            'group.id': self.group_id or settings.KAFKA_SETTINGS.get('group.id'),
            'auto.offset.reset': self.auto_offset_reset or settings.KAFKA_SETTINGS.get('auto.offset.reset'),
        })
        self.consumer_objects = {}

    def get_subclasses(self, kafka_class):
        """
        # 获取指定类的所有子类（包括孙子类）
        :param kafka_class:
        :return:
        """
        # 导入kafka_app/consumer目录下的所有模块
        self.import_submodules('kafka_app.consumer')
        subclasses = set()
        for subclass in kafka_class.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(self.get_subclasses(subclass))
        return subclasses

    def import_submodules(self, package_name):
        """
        递归动态导入目录下的所有模块
        :param package_name:
        :return:
        """
        package = importlib.import_module(package_name)
        for _, modname, ispkg in pkgutil.iter_modules(package.__path__):
            full_modname = f"{package_name}.{modname}"
            importlib.import_module(full_modname)
            if ispkg:
                self.import_submodules(full_modname)

    def register_consumer(self):
        """
        注册消费者对象实例
        :return:
        """
        for cls in self.get_subclasses(KafkaConsumerABC):
            if cls.__name__ == 'KafkaConsumerABC':
                continue
            instance = cls()
            topics = instance.topic_type()
            if not topics:
                continue
            for topic in topics:
                self.consumer_objects[topic] = instance

    def get_handler(self, topic):
        """
        通过topic获取消费者实例
        :param topic:
        :return:
        """
        self.register_consumer()
        return self.consumer_objects.get(topic)

    def get_topics(self):
        self.register_consumer()
        topics = self.consumer_objects.keys()
        return list(topics)

    def get_consumer(self):
        """
        获取 Kafka 消费者实例，并订阅指定主题
        """
        consumer = self._consumer
        consumer.subscribe(self.get_topics())
        return consumer

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
