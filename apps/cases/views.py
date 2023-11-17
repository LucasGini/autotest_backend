from common.general_page import GeneralPage
from common.custom_response import CustomResponse
from apps.cases.serializers import ListTestCaseSerializer
from apps.cases.serializers import CreateTestCaseSerializer
from rest_framework import generics
from rest_framework import status
from apps.cases.models import TestCase, ProjectsInfo
from rest_framework.exceptions import APIException, NotFound


class ListCreateTestCaseView(generics.ListCreateAPIView):
    """
    测试用例列表创建视图类
    """

    queryset = TestCase.objects.all()
    pagination_class = GeneralPage
    serializer_class = ListTestCaseSerializer

    def get_serializer_class(self):
        """
        重写get_serializer_class()方法
        """
        if self.request.method == 'GET':
            return ListTestCaseSerializer
        if self.request.method == 'POST' or self.request.method == 'PUT':
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
        serializer = self.get_serializer(data=data,  context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        header = self.get_success_headers(serializer.data)
        return CustomResponse(data=serializer.data, code=201, msg='OK', status=status.HTTP_201_CREATED, headers=header)


class RetrieveUpdateDestroyTestCaseAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    测试用例详情更新删除视图类
    """

    queryset = TestCase.objects.all()
    pagination_class = GeneralPage
    serializer_class = ListTestCaseSerializer

    def get_serializer_class(self):
        """
        重写get_serializer_class()方法
        """
        if self.request.method == 'GET':
            return ListTestCaseSerializer
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return CreateTestCaseSerializer
        else:
            return ListTestCaseSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_queryset().get(id=kwargs.get('pk'))
        except Exception:
            raise NotFound('查询数据不存在')
        serializer = self.get_serializer(instance)
        return CustomResponse(data=serializer.data, code=200, msg='OK', status=status.HTTP_200_OK)




