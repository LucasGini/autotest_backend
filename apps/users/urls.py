from django.urls import path, include
from rest_framework import routers
from apps.users.views import AuthUserViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register('authUser', AuthUserViewSet)

urlpatterns = [
    path('', include(router.urls))
]
