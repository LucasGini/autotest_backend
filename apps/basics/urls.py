from django.urls import path, include
from apps.basics.views import TestEnvModelViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('testenv', TestEnvModelViewSet, basename='test_env')

urlpatterns = [
    path('', include(router.urls))
]
