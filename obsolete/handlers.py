import json
from logging import getLogger
# from cases.models import TestCase

logger = getLogger(__name__)


class UserCreatedHandler:
    def handle_message(self, msg):
        msg = json.loads(msg)
        project_id = msg.get('projectId')
        print(project_id)
        # if project_id:
        #     queryset = TestCase.objects.filter(project_id=project_id)
        #     if queryset.exists():
        #         queryset.update(enable_flag=0)


class OrderCreatedHandler:
    def handle_message(self, message):
        print(f"Handling order created message: {message}")
