from django.urls import path, include
from apps.cases.views import (ListCreateTestCaseView, AsyncExecuteView, ExecuteView,
                              RetrieveUpdateDestroyTestCaseAPIView, TestReportModelViewSet,
                              ProjectsInfoModelViewSet, TestSuiteModelViewSet, DependentMethodsViewSet)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('project', ProjectsInfoModelViewSet, basename='project')
router.register('suite', TestSuiteModelViewSet, basename='test_suite')
router.register('dependent', DependentMethodsViewSet, basename='dependent_methods')
router.register('report', TestReportModelViewSet, basename='test_report')

urlpatterns = [
    path('testcase/', ListCreateTestCaseView.as_view(), name='test_case'),
    path('testcase/<int:pk>', RetrieveUpdateDestroyTestCaseAPIView.as_view(), name='test_case_detail'),
    path('asyncexecute/', AsyncExecuteView.as_view(), name='async_execute'),
    path('execute/', ExecuteView.as_view(), name='execute'),
    path('', include(router.urls))
]
