from apps.basics.models import TestEnv, SystemMenu
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


class ListSystemMenuSerializers(CustomModelSerializer):
    """
    系统菜单序列表列化器
    """

    class Meta:
        model = SystemMenu
        fields = '__all__'


class CreateSystemMenuSerializers(CustomModelSerializer):
    """
    系统菜单序创建列化器
    """

    class Meta:
        model = SystemMenu
        exclude = ('enable_flag', 'created_by', 'updated_by')
