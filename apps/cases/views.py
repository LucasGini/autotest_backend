import copy
import types
import inspect
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import generics
from rest_framework import status
from rest_framework import views
from rest_framework.exceptions import NotFound, APIException
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from apps.cases.request.case_request_model import ExecuteRequestModel, AsyncExecuteRequestModel
from common.custom_exception import ParamException
from apps.basics.models import TestEnv
from common.utils.api_execute import case_execute, project_execute, suite_execute
from common.utils.custom_update import custom_update
from common.general_page import GeneralPage
from common.custom_response import CustomResponse
from common.custom_model_viewset import CustomModelViewSet
from common.utils.default_write import default_write
from apps.cases.serializers import (ListTestCaseSerializer, CreateTestCaseSerializer, ListProjectsInfoSerializer,
                                    CreateProjectsInfoSerializer, ListTestSuiteSerializer, CreateTestSuiteSerializer,
                                    ListDependentMethodsSerializer, CreateDependentMethodsSerializer,
                                    TestReportSerializer, UpdateProjectsInfoSerializer)
from apps.cases.models import TestCase, TestSuite, Precondition, ProjectsInfo, DependentMethods, TestReport
from execute.setattr_public_test import SetattrPublicTestCase
from apps.cases.task import run_case
from common.const.case_const import ExecuteType, EXECUTED_COUNT_REDIS_KEY, SUCCESS_COUNT_REDIS_KEY, ReportStatus
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter
from apps.cases.filters import TestProjectFilter, TestCaseFilter


class ListCreateTestCaseView(generics.ListCreateAPIView):
    """
    测试用例列表创建视图类
    """

    queryset = TestCase.objects.filter(enable_flag=1)
    pagination_class = GeneralPage
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter, SearchFilter)
    serializer_class = ListTestCaseSerializer
    filterset_class = TestCaseFilter

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
        try:
            if serializer.is_valid():
                self.perform_update(serializer)
            # 修改前置条件
            precondition_data = request.data.pop('precondition', None)
            # 如果precondition_data为空，则直接提交事务
            if precondition_data is None:
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
            default_write(precondition, request)
            default_write(instance, request)
        except Exception as e:
            raise APIException(e)

        return CustomResponse(data=serializer.data, code=200, msg='OK', status=status.HTTP_200_OK)

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        """
        逻辑删除测试用例
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            try:
                precondition = Precondition.objects.get(case=instance.id)
            except Precondition.DoesNotExist:
                return CustomResponse(data=[], code=204, msg='OK', status=status.HTTP_200_OK)
            self.perform_destroy(precondition)
        except Exception as e:
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
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter, SearchFilter)
    serializer_class = ListProjectsInfoSerializer
    filterset_class = TestProjectFilter
    search_fields = ('project_name', )

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        if self.action == 'create':
            return CreateProjectsInfoSerializer
        if self.action == 'update':
            return UpdateProjectsInfoSerializer
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

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        # 重写以适配部分修改情况
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer(instance, data=data, partial=True, context={'request': request})
        suite_name = data.get('suite_name', None)
        case = data.get('case', None)
        serializer.is_valid()
        # 用例集名称或用例为空的情况，不走序列化保存
        if suite_name and case:
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


class DependentMethodsViewSet(CustomModelViewSet):
    """
    依赖方法视图集
    """

    queryset = DependentMethods.objects.filter(enable_flag=1)
    pagination_class = GeneralPage
    serializer_class = ListDependentMethodsSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        if self.action == 'create' or self.action == 'update':
            return CreateDependentMethodsSerializer
        else:
            return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception as e:
            raise NotFound(e)
        serializer = self.get_serializer(instance)
        data = serializer.data
        dependent_method = data.get('dependent_method', None)
        func_list = []
        if dependent_method:
            func_detail = {}
            module = types.ModuleType('dynamic_module')
            exec(dependent_method, module.__dict__)
            for func_name in dir(module):
                # 判断函数是否存在module,且是否可调用
                if callable(getattr(module, func_name)):
                    func = module.__dict__[func_name]
                    func_detail['func_name'] = func_name
                    func_detail['func_doc'] = func.__doc__
                    # 获取函数的参数列表（包含默认值）
                    full_args = inspect.getfullargspec(func).args
                    func_detail['func_args'] = full_args
                    # 深度copy
                    func_list.append(copy.deepcopy(func_detail))
        data['func_list'] = func_list
        return CustomResponse(data, code=200, msg='OK', status=status.HTTP_200_OK)


class TestReportModelViewSet(CustomModelViewSet):
    """
    测试报告视图集
    """
    queryset = TestReport.objects.all().filter(enable_flag=1)
    serializer_class = TestReportSerializer
    pagination_class = GeneralPage
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['repost_name', 'execute_type', 'start_at', 'status', 'result', 'success_count', 'case_count']
    search_fields = ['repost_name', 'execute_type', 'start_at', 'status', 'result', 'success_count', 'case_count']

    @staticmethod
    def get_redis_count(data, redis):
        """
        获取redis的executed_count和success_count值
        :param data: serializer.data
        :param redis: redis实例
        :return:
        """

        for i in data:
            executed_count_redis_key = EXECUTED_COUNT_REDIS_KEY.format(i['id'])
            success_count_redis_key = SUCCESS_COUNT_REDIS_KEY.format(i['id'])
            executed_count = redis.get(executed_count_redis_key)
            success_count = redis.get(success_count_redis_key)
            if executed_count:
                i['executed_count'] = int(executed_count)
            if success_count:
                i['success_count'] = int(success_count)
        return data

    def list(self, request, *args, **kwargs):
        redis_conn = get_redis_connection()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_redis_count(serializer.data, redis=redis_conn)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = self.get_redis_count(serializer.data, redis=redis_conn)
        return CustomResponse(data, code=200, msg='OK', status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        重写create方法，禁止新增
        :return:
        """
        return CustomResponse(data=[], code=405, msg='禁止新增', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        """
        重写update方法，禁止修改
        :return:
        """
        return CustomResponse(data=[], code=405, msg='禁止修改', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        """
        重写partial_update方法，禁止部分修改
        :return:
        """
        return CustomResponse(data=[], code=405, msg='禁止部分修改', status=status.HTTP_405_METHOD_NOT_ALLOWED)


class DownloadReportView(views.APIView):
    """
    下载报告
    """
    @staticmethod
    def get_report_status_message(status):
        """
        根据状态返回对应的提示
        :param status:
        :return:
        """
        if status == ReportStatus.EXECUTED_SUCCESS.value:
            return '报告下载'
        elif status == ReportStatus.EXECUTING.value:
            return '任务执行中'
        else:
            return '任务执行失败'

    @staticmethod
    def get_report_name(extension='html'):
        """
        生成测试报告名称
        :param extension: 文件扩展名，默认为html
        :return
        """
        formatted_datetime = timezone.localtime().strftime('%Y_%m_%d_%H_%M_%S')
        return 'testReport_{}.{}'.format(formatted_datetime, extension)

    def get(self, request, *args, **kwargs):
        report_id = request.query_params.get('reportId', None)
        if report_id is None:
            raise ParamException('reportId参数不能为空')
        try:
            report = TestReport.objects.get(id=report_id, enable_flag=1)
        except Exception:
            return CustomResponse(data=[], code=404, msg='报告不存在', status=status.HTTP_404_NOT_FOUND)
        status_message = self.get_report_status_message(report.status)
        if report.status == ReportStatus.EXECUTED_SUCCESS.value:
            response = HttpResponse(report.report, content_type='text/html')
            response['Content-Disposition'] = 'attachment; filename={}'.format(self.get_report_name())
            return response
        else:
            return CustomResponse(data=[], code=404, msg=status_message, status=status.HTTP_404_NOT_FOUND)


class AsyncExecuteView(views.APIView):
    """
    异步执行接口
    param : {
        "executeType": 10,
        "envId": 1,
        "projectId": 1,
        "suiteId": 1,
        "caseId": 2
        }
    """

    def post(self, request, *args, **kwargs):
        request_data = AsyncExecuteRequestModel(**request.data)
        if request_data.executeType is None:
            raise ParamException('executeType参数不能为空')
        if request_data.envId is None:
            raise ParamException('envId参数不能为空')
        try:
            env = TestEnv.objects.get(id=request_data.envId, enable_flag=1)
        except Exception:
            return CustomResponse(data=[], code=404, msg='环境不存在', status=status.HTTP_404_NOT_FOUND)
        # 用例执行类型
        if request_data.executeType == ExecuteType.CASE.value:
            cases, report_name = case_execute(request)
        elif request_data.executeType == ExecuteType.PROJECT.value:
            cases, report_name = project_execute(request)
        elif request_data.executeType == ExecuteType.SUITE.value:
            cases, report_name = suite_execute(request)
        else:
            return CustomResponse(data=[], code=404, msg='执行类型不存在', status=status.HTTP_404_NOT_FOUND)
        run_case.delay(cases, env, report_name, request_data.executeType)
        return CustomResponse(data=[], code=200, msg='OK', status=status.HTTP_200_OK)


class ExecuteView(views.APIView):
    """
    同步执行接口
    """

    def post(self, request, *args, **kwargs):
        request_data = ExecuteRequestModel(**request.data)
        if request_data.executeType is None:
            raise ParamException('executeType参数不能为空')
        if request_data.envId is None:
            raise ParamException('envId参数不能为空')
        try:
            env = TestEnv.objects.get(id=request_data.envId, enable_flag=1)
        except TestEnv.DoesNotExist:
            return CustomResponse(data=[], code=404, msg='环境不存在', status=status.HTTP_404_NOT_FOUND)
        # 用例执行类型
        if request_data.executeType == ExecuteType.CASE.value:
            cases, report_name = case_execute(request)
        elif request_data.executeType == ExecuteType.PROJECT.value:
            cases, report_name = project_execute(request)
        elif request_data.executeType == ExecuteType.SUITE.value:
            cases, report_name = suite_execute(request)
        else:
            return CustomResponse(data=[], code=404, msg='执行类型不存在', status=status.HTTP_404_NOT_FOUND)
        SetattrPublicTestCase(cases, env, report_name, request_data.executeType).test_main()
        return CustomResponse(data=[], code=200, msg='OK', status=status.HTTP_200_OK)
