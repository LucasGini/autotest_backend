from rest_framework import serializers
from apps.users.models import AuthUser


class AuthUserSerializer(serializers.ModelSerializer):
    """
    用户基础模型序列器
    """
    class Meta:
        model = AuthUser  # 关联模型类
        fields = ("id", "username", "email", "phone", "sex", "created_date", "updated_date")  # 显示的字段
