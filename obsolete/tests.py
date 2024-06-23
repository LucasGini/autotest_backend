import time
from abc import ABC, abstractmethod
from confluent_kafka import Consumer, Producer, KafkaError


class KafkaServiceABC(ABC):

    @abstractmethod
    def get_topics(self):
        """
        抽象方法，子类需实现以返回主题列表
        """
        pass

    def get_subclasses(self, kafka_class):
        """
        获取指定类的所有子类（包括孙子类）
        """
        subclasses = set()
        for subclass in kafka_class.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(self.get_subclasses(subclass))
        return subclasses

    def get_producer(self):
        """
        获取 Kafka 生产者实例
        """
        producer = Producer({
            'bootstrap.servers': '127.0.0.1:9092'
        })
        return producer

    def get_consumer(self, topics):
        """
        获取 Kafka 消费者实例，并订阅指定主题
        """
        consumer = Consumer({
            'bootstrap.servers': '127.0.0.1:9092',
            'group.id': 'autotest',
            'auto.offset.reset': 'earliest'
        })
        consumer.subscribe(topics)
        return consumer

    def produce_message(self, topic, message):
        """
        生产消息到指定 Kafka 主题
        """
        producer = self.get_producer()
        producer.produce(topic, message)
        producer.flush()
        producer.poll(0)



    def send_message(self, topic, message):
        """
        发送消息到指定 Kafka 主题
        """
        self.produce_message(topic, message)

    def consume_messages(self):
        """
        消费订阅主题的消息，需由子类实现具体逻辑
        """
        consumer = self.get_consumer(self.get_topics())
        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(msg.error())
                        break
                print(f"接收到消息: {msg.value().decode('utf-8')}")
                # 处理消息逻辑，可根据业务需求自定义
                time.sleep(1)  # 模拟处理时间
        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()

    def run_consumers(self):
        """
        启动所有子类的消费者，消费订阅的主题消息
        """
        pass



# 示例子类 MyKafkaService，继承 KafkaServiceABC
class MyKafkaService(KafkaServiceABC):

    def get_topics(self):
        """
        实现获取主题列表的方法
        """
        return ['topic1']  # 修改为你的实际主题

    def consume_messages(self):
        """
        自定义消息处理逻辑
        """
        super().consume_messages()  # 可选：调用父类的 consume_messages 实现
        # 实现自定义的消息处理逻辑
        pass


if __name__ == '__main__':
    kafka_service = MyKafkaService()
    kafka_service.send_message('topic1', 'message1')
