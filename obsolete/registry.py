from common.const.case_const import KAFKA_PROJECT_DELETED_TOPIC
from obsolete.handlers import UserCreatedHandler, OrderCreatedHandler


class HandlerRegistry:
    def __init__(self):
        self.handlers = {}

    def register_handler(self, topic, handler):
        self.handlers[topic] = handler

    def get_handler(self, topic):
        return self.handlers.get(topic)

    def get_all_topics(self):
        return list(self.handlers.keys())


handler_registry = HandlerRegistry()

handler_registry.register_handler(KAFKA_PROJECT_DELETED_TOPIC, UserCreatedHandler())
handler_registry.register_handler('order_created', OrderCreatedHandler())


