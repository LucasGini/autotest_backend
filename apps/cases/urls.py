from django.urls import path, include
from apps.cases.views import (ListCreateTestCaseView, ExecuteView, RetrieveUpdateDestroyTestCaseAPIView,
                              ProjectsInfoModelViewSet, TestSuiteModelViewSet, DependentMethodsViewSet)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('project', ProjectsInfoModelViewSet, basename='project')
router.register('testsuite', TestSuiteModelViewSet, basename='test_suite')
router.register('dependent', DependentMethodsViewSet, basename='dependent_methods')


urlpatterns = [
    path('testcase/', ListCreateTestCaseView.as_view(), name='test_case'),
    path('testcase/<int:pk>', RetrieveUpdateDestroyTestCaseAPIView.as_view(), name='test_case_detail'),
    path('execute/', ExecuteView.as_view(), name='execute'),
    path('', include(router.urls))
]
