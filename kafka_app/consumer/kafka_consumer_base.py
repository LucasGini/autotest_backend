import importlib
import pkgutil

from confluent_kafka import KafkaException, Consumer
from kafka_app.kafka_consumer import KafkaConsumerABC


class KafkaConsumerBase(KafkaConsumerABC):
    """
    Kafka 消费者基础类
    """

    def __init__(self):
        self._consumer = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'autotest',
            'auto.offset.reset': 'earliest',
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
        consumer = self.get_consumer()
        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                topic = msg.topic()
                msg = msg.value().decode('utf-8')
                instance = self.consumer_objects.get(topic)
                if instance is None:
                    continue
                instance.handler_message(msg)
        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()

    def handler_message(self, msg):
        pass

    def topic_type(self):
        pass


if __name__ == '__main__':
    import os
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "autotest_backend.settings")
    django.setup()

    kafka_consumer_base = KafkaConsumerBase()
    kafka_consumer_base.consume_messages()
