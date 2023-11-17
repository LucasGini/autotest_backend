from django.urls import path
from apps.cases.views import ListCreateTestCaseView
from apps.cases.views import RetrieveUpdateDestroyTestCaseAPIView

urlpatterns = [
    path('testCase/', ListCreateTestCaseView.as_view(), name='test_case'),
    path('testCase/<int:pk>', RetrieveUpdateDestroyTestCaseAPIView.as_view(), name='test_case_detail')
]
