from apps.users.serializers import AuthUserSerializer
from apps.users.models import AuthUser
from common.custom_model_viewset import CustomModelViewSet
from common.general_page import GeneralPage
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter, SearchFilter


class AuthUserViewSet(CustomModelViewSet):
    """
    用户基础信息视图
    """

    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializer
    pagination_class = GeneralPage
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    search_fields = ('username', '=id')

