from django.urls import path, include
from apps.basics.views import TestEnvModelViewSet, SystemMenuModelViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('testEnv', TestEnvModelViewSet, basename='test_env')
router.register('systemMenu', SystemMenuModelViewSet, basename='system_menu')

urlpatterns = [
    path('', include(router.urls))
]
