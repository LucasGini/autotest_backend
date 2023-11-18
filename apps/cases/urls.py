from django.urls import path, include
from apps.cases.views import ListCreateTestCaseView
from apps.cases.views import RetrieveUpdateDestroyTestCaseAPIView
from apps.cases.views import ProjectsInfoModelViewSet
from apps.cases.views import TestSuiteModelViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('project', ProjectsInfoModelViewSet, basename='project')
router.register('testsuite', TestSuiteModelViewSet, basename='test_suite')


urlpatterns = [
    path('testcase/', ListCreateTestCaseView.as_view(), name='test_case'),
    path('testcase/<int:pk>', RetrieveUpdateDestroyTestCaseAPIView.as_view(), name='test_case_detail'),
    path('', include(router.urls))
]
