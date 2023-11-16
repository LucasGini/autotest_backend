from common.general_page import GeneralPage
from common.custom_response import CustomResponse
from apps.cases.serializers import ListTestCaseSerializer
from apps.cases.serializers import CreateTestCaseSerializer
from rest_framework import generics
from rest_framework import status
from apps.cases.models import TestCase


class TestCaseView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    """
    测试用例视图类
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
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data, code=200, msg='OK', status=status.HTTP_200_OK)


