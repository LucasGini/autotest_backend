from django.db import transaction
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import NotFound, APIException
from common.general_page import GeneralPage
from common.custom_response import CustomResponse
from common.custom_model_viewset import CustomModelViewSet
from common.utils.default_write import default_write
from apps.cases.serializers import ListTestCaseSerializer
from apps.cases.serializers import CreateTestCaseSerializer
from apps.cases.serializers import ListProjectsInfoSerializer
from apps.cases.serializers import CreateProjectsInfoSerializer
from apps.cases.serializers import ListTestSuiteSerializer
from apps.cases.serializers import CreateTestSuiteSerializer
from apps.cases.models import TestCase
from apps.cases.models import TestSuite
from apps.cases.models import Precondition
from apps.cases.models import ProjectsInfo


class ListCreateTestCaseView(generics.ListCreateAPIView):
    """
    测试用例列表创建视图类
    """

    queryset = TestCase.objects.filter(enable_flag=1)
    pagination_class = GeneralPage
    serializer_class = ListTestCaseSerializer

    def get_serializer_class(self):
        """
        重写get_serializer_class()方法
        """
        if self.request.method == 'GET':
            return ListTestCaseSerializer
        if self.request.method == 'POST':
            return CreateTestCaseSerializer
        else:
            return ListTestCaseSerializer

    def list(self, request, *args, **kwargs):
        """
        查询列表
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data, code=200, msg='OK', status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        创建测试用例
        """
        data = request.data
        try:
            ProjectsInfo.objects.get(id=data['project'])
        except Exception:
            raise NotFound('项目不存在，新增失败')
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid()
        self.perform_create(serializer)
        header = self.get_success_headers(serializer.data)
        return CustomResponse(data=serializer.data, code=201, msg='OK', status=status.HTTP_201_CREATED, headers=header)


class RetrieveUpdateDestroyTestCaseAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    测试用例详情更新删除视图类
    """

    queryset = TestCase.objects.filter(enable_flag=1)
    pagination_class = GeneralPage
    serializer_class = ListTestCaseSerializer

    def get_serializer_class(self):
        """
        重写get_serializer_class()方法
        """
        if self.request.method == 'GET':
            return ListTestCaseSerializer
        if self.request.method == 'PUT':
            return CreateTestCaseSerializer
        else:
            return ListTestCaseSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        查询用例明细
        """
        try:
            instance = self.get_queryset().get(id=kwargs.get('pk'))
        except Exception:
            raise NotFound('查询数据不存在')
        serializer = self.get_serializer(instance)
        return CustomResponse(data=serializer.data, code=200, msg='OK', status=status.HTTP_200_OK)

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        """
        更新测试用例
        """
        partial = kwargs.pop('partial', True)
        data = request.data
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial, context={'request': request})
        # 开启事务
        save_id = transaction.savepoint()
        try:
            if serializer.is_valid():
                self.perform_update(serializer)
            # 修改前置条件
            precondition_data = request.data.pop('precondition', None)
            # 如果precondition_data为空，则直接提交事务
            if precondition_data is None:
                transaction.savepoint_commit(save_id)
                return CustomResponse(data=serializer.data, code=200, msg='OK', status=status.HTTP_200_OK)
            try:
                # 查询是否存在前置条件对象，不存在则新增，存在则修改
                precondition = Precondition.objects.get(case=instance.id)
                if isinstance(precondition_data, dict):
                    for attr, value in precondition_data.items():
                        setattr(precondition, attr, value)
            except Precondition.DoesNotExist:
                precondition = Precondition()
                precondition.precondition_case = precondition_data.get('precondition_case', None)
                precondition.case = instance
            # 保存并提交事务
            default_write(precondition, request)
            default_write(instance, request)
            transaction.savepoint_commit(save_id)
        except Exception as e:
            # 出现异常，回滚事务
            transaction.savepoint_rollback(save_id)
            raise APIException(e)

        return CustomResponse(data=serializer.data, code=200, msg='OK', status=status.HTTP_200_OK)

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        """
        逻辑删除测试用例
        """
        # 开启事务
        save_id = transaction.savepoint()
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            precondition = None
            try:
                precondition = Precondition.objects.get(case=instance.id)
            except Precondition.DoesNotExist:
                pass
            if precondition:
                self.perform_destroy(precondition)
            # 提交事务
            transaction.savepoint_commit(save_id)
        except Exception as e:
            # 事务回滚
            transaction.savepoint_rollback(save_id)
            raise APIException(e)
        return CustomResponse(data=[], code=204, msg='OK', status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.enable_flag = 0
        instance.save()


class ProjectsInfoModelViewSet(CustomModelViewSet):
    """
    项目视图集
    """
    queryset = ProjectsInfo.objects.filter(enable_flag=1)
    pagination_class = GeneralPage
    serializer_class = ListProjectsInfoSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        if self.action == 'create' or self.action == 'update':
            return CreateProjectsInfoSerializer
        else:
            return self.serializer_class


class TestSuiteModelViewSet(CustomModelViewSet):
    """
    测试套件视图集
    """
    queryset = TestSuite.objects.filter(enable_flag=1)
    pagination_class = GeneralPage
    serializer_class = ListTestSuiteSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        if self.action == 'create' or self.action == 'update':
            return CreateTestSuiteSerializer
        else:
            return self.serializer_class

