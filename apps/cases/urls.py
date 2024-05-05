from django.urls import path, include
from apps.cases.views import (ListCreateTestCaseView, AsyncExecuteView, ExecuteView,
                              RetrieveUpdateDestroyTestCaseAPIView, TestReportModelViewSet,
                              ProjectsInfoModelViewSet, TestSuiteModelViewSet, DependentMethodsViewSet,
                              DownloadReportView)
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register('project', ProjectsInfoModelViewSet, basename='project')
router.register('suite', TestSuiteModelViewSet, basename='test_suite')
router.register('dependent', DependentMethodsViewSet, basename='dependent_methods')
router.register('report', TestReportModelViewSet, basename='test_report')

urlpatterns = [
    path('testCase', ListCreateTestCaseView.as_view(), name='test_case'),
    path('testCase/<int:pk>', RetrieveUpdateDestroyTestCaseAPIView.as_view(), name='test_case_detail'),
    path('asyncExecute', AsyncExecuteView.as_view(), name='async_execute'),
    path('downloadReport', DownloadReportView.as_view(), name='download_report'),
    path('execute', ExecuteView.as_view(), name='execute'),
    path('', include(router.urls))
]
