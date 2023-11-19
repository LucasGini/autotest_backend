from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import APIException
from apps.basics.models import TestEnv
from apps.basics.serializers import ListTestEnvSerializers, CreateTestEnvSerializers
from common.custom_model_viewset import CustomModelViewSet
from common.custom_response import CustomResponse
from common.utils.custom_update import custom_update
from common.general_page import GeneralPage


class TestEnvModelViewSet(CustomModelViewSet):
    """
    测试环境视图集
    """

    queryset = TestEnv.objects.filter(enable_flag=1)
    pagination_class = GeneralPage
    serializer_class = ListTestEnvSerializers

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        elif self.action == 'create' or self.action == 'update':
            return CreateTestEnvSerializers
        else:
            return self.serializer_class

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        # 重写以适配部分修改情况
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer(instance, data=data, partial=True, context={'request': request})
        env_name = data.get('env_name', None)
        agreement = data.get('agreement', None)
        hosts = data.get('hosts', None)
        port = data.get('port', None)
        serializer.is_valid()
        # 必填字段为空的情况，不走序列化保存
        if env_name and agreement and hosts and port:
            self.perform_update(serializer)
        else:
            try:
                custom_update(instance, request)
            except Exception as e:
                raise APIException(e)
        # 更新数据后，如果存在缓存则清除缓存
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return CustomResponse(serializer.data, code=200, msg='OK', status=status.HTTP_200_OK)





