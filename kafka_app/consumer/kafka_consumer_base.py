import threading
from confluent_kafka import KafkaException
from kafka_app.kafka_consumer import KafkaConsumerABC


def async_handle(f):
    def wrapper(*args, **kwargs):
        thr = threading.Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper

class KafkaConsumerBase(KafkaConsumerABC):
    """
    Kafka 消费者基础类
    """


    @async_handle
    def async_consume_messages(self):
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

    def consume_messages(self):
        """
        包装异步方法
        :return:
        """
        self.async_consume_messages()



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
