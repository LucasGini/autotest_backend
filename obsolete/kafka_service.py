from confluent_kafka import Consumer, KafkaException
from obsolete.registry import handler_registry


class KafkaConsumerService:
    def __init__(self, broker_url, group_id, topics):
        self.consumer = Consumer({
            'bootstrap.servers': broker_url,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.topics = topics

    def consume_messages(self):
        try:
            self.consumer.subscribe(self.topics)
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                self.process_message(msg)
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

    def process_message(self, msg):
        topic = msg.topic()
        message = msg.value().decode('utf-8')
        handler = handler_registry.get_handler(topic)
        if handler:
            handler.handle_message(message)
        else:
            print(f"No handler registered for topic: {topic}")

