import json
from cases.models import TestCase
from kafka_app.kafka_consumer import KafkaConsumerABC
from common.const.case_const import KAFKA_PROJECT_DELETED_TOPIC


class ProjectsDeletedConsumer(KafkaConsumerABC):
    """
    项目删除后kafka消费者
    """

    def handler_message(self, msg):
        msg = json.loads(msg)
        project_id = msg.get('projectId')
        print(project_id)
        if project_id:
            queryset = TestCase.objects.filter(project_id=project_id)
            if queryset.exists():
                queryset.update(enable_flag=0)

    def topic_type(self):
        return [KAFKA_PROJECT_DELETED_TOPIC]
