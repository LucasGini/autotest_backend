from apps.users.serializers import AuthUserSerializer
from apps.users.models import AuthUser
from rest_framework import viewsets


class AuthUserViewSet(viewsets.ModelViewSet):
    """
    用户基础信息视图
    """

    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializer
