from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import APIException
from apps.basics.filters import TestEnvFilter, CategoryConfigFilter
from apps.basics.models import TestEnv, SystemMenu, CategoryConfig
from apps.basics.serializers import ListTestEnvSerializers, CreateTestEnvSerializers, ListSystemMenuSerializers, \
    CreateSystemMenuSerializers, SearchCategoryConfigSerializers, CreateCategoryConfigSerializers
from common.custom_model_viewset import CustomModelViewSet
from common.custom_response import CustomResponse
from common.utils.custom_update import custom_update
from common.general_page import GeneralPage
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters import rest_framework as filters
from collections import OrderedDict


class TestEnvModelViewSet(CustomModelViewSet):
    """
    测试环境视图集
    """

    queryset = TestEnv.objects.filter(enable_flag=1)
    pagination_class = GeneralPage
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    serializer_class = ListTestEnvSerializers
    # 自定义过滤
    filterset_class = TestEnvFilter

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


class SystemMenuModelViewSet(CustomModelViewSet):
    """
    系统菜单视图集
    """

    queryset = SystemMenu.objects.filter(enable_flag=1)
    serializer_class = ListSystemMenuSerializers

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        elif self.action == 'create' or self.action == 'update':
            return CreateSystemMenuSerializers
        else:
            return self.serializer_class

    def _recursive_menu_tree(self, menu_list, parent_id=None):
        """
        递归生成菜单树
        :param menu_list:
        :param parent_id:
        :return:
        """
        tree = []
        for menu in menu_list:
            if menu.parent_id == parent_id:
                children = self._recursive_menu_tree(menu_list, menu.id)
                menu_dict = {
                    'id': menu.id,
                    'name': menu.name,
                    'path': menu.path,
                    'is_hidden': menu.is_hidden,
                    'component': menu.component,
                    'icon': menu.icon,
                    'order_num': menu.order_num,
                    'parent_id': menu.parent_id,
                    'children': children if children else [],
                }
                tree.append(menu_dict)
        return tree

    def list(self, request, *args, **kwargs):
        """
        获取菜单树
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            menus = self.get_queryset().order_by('order_num')
        except Exception as e:
            raise APIException(f'查询系统菜单失败：{e}')
        menu_tree = self._recursive_menu_tree(menus)
        return CustomResponse(menu_tree, code=200, msg='OK', status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        删除菜单
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            # 查询是否有子菜单,有则删除菜单
            child_menus = SystemMenu.objects.filter(parent_id=instance.id, enable_flag=1)
            if child_menus:
                for child_menu in child_menus:
                    self.perform_destroy(child_menu)
        except Exception as e:
            raise APIException(f'删除菜单失败：{e}')
        return CustomResponse(code=204, msg='OK', status=status.HTTP_204_NO_CONTENT)


class CategoryConfigModelViewSet(CustomModelViewSet):
    """
    类型配置表视图集
    """

    queryset = CategoryConfig.objects.filter(enable_flag=1)
    serializer_class = SearchCategoryConfigSerializers
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_class = CategoryConfigFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        elif self.action == 'create' or self.action == 'update':
            return CreateCategoryConfigSerializers
        else:
            return self.serializer_class

    def recursive_configuration_tree(self, configurations, parent_id=0):
        """
        递归生成配置树
        :param configurations: serializer.data
        :param parent_id:
        :return:
        """
        config_tree = []
        for configuration in configurations:
            if configuration.get('category_parent_id') == parent_id:
                children = self.recursive_configuration_tree(configurations, configuration.get('id'))
                config_od = OrderedDict([
                    ('id', configuration.get('id')),
                    ('category_group', configuration.get('category_group')),
                    ('category_name', configuration.get('category_name')),
                    ('category_code', configuration.get('category_code')),
                    ('category_description', configuration.get('category_description')),
                    ('category_parent_id', configuration.get('category_parent_id')),
                    ('sort_number', configuration.get('sort_number')),
                    ('readonly', configuration.get('readonly')),
                    ('children', children),
                    ('enable_flag', configuration.get('enable_flag')),
                    ('created_by', configuration.get('created_by')),
                    ('created_date', configuration.get('created_date')),
                    ('updated_by', configuration.get('updated_by')),
                    ('updated_date', configuration.get('updated_date')),
                ])
                config_tree.append(config_od)
        return config_tree

    def list(self, request, *args, **kwargs):
        """
        查询类型配置列表或树
        searchType=tree 查询树, 不传获取传其他查询列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        params = request.query_params
        search_type = params.get('searchType', None)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None and search_type.lower() != 'tree':
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        if search_type and search_type.lower() == 'tree':
            if isinstance(serializer.data, list):
                data = self.recursive_configuration_tree(serializer.data)
            else:
                data = serializer.data
        else:
            data = serializer.data
        print(data)
        return CustomResponse(data, code=200, msg='OK', status=status.HTTP_200_OK)
