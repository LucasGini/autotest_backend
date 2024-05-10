from django.urls import path, include
from apps.basics.views import TestEnvModelViewSet, SystemMenuModelViewSet, CategoryConfigModelViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register('testEnv', TestEnvModelViewSet, basename='test_env')
router.register('systemMenu', SystemMenuModelViewSet, basename='system_menu')
router.register('categoryConfig', CategoryConfigModelViewSet, basename='category_config')

urlpatterns = [
    path('', include(router.urls))
]
