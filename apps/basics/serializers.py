from apps.basics.models import TestEnv
from common.custom_model_serializer import CustomModelSerializer


class ListTestEnvSerializers(CustomModelSerializer):
    """
    测试环境序列表列化器
    """

    class Meta:
        model = TestEnv
        fields = '__all__'


class CreateTestEnvSerializers(CustomModelSerializer):
    """
    测试环境序创建列化器
    """

    class Meta:
        model = TestEnv
        exclude = ('enable_flag', 'created_by', 'updated_by')

