from apps.users.serializers import AuthUserSerializer
from apps.users.models import AuthUser
from common.custom_model_viewset import CustomModelViewSet
from common.general_page import GeneralPage


class AuthUserViewSet(CustomModelViewSet):
    """
    用户基础信息视图
    """

    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializer
    pagination_class = GeneralPage
