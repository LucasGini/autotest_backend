from django.urls import path, include
from apps.cases.views import ListCreateTestCaseView
from apps.cases.views import RetrieveUpdateDestroyTestCaseAPIView
from apps.cases.views import ProjectsInfoModelViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('project', ProjectsInfoModelViewSet, basename='project')


urlpatterns = [
    path('testcase/', ListCreateTestCaseView.as_view(), name='test_case'),
    path('testcase/<int:pk>', RetrieveUpdateDestroyTestCaseAPIView.as_view(), name='test_case_detail'),
    path('', include(router.urls))
]
