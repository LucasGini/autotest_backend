import time

from rest_framework.exceptions import NotFound
from common.custom_response import CustomResponse
from rest_framework import status
from rest_framework.viewsets import ModelViewSet


class CustomModelViewSet(ModelViewSet):
    """
    重写ModelViewSet类
    """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(serializer.data, code=200, msg='OK', status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # 获取新增成功的的实例，重新进行序列化
        after_serializer = self.get_serializer(serializer.instance)
        return CustomResponse(after_serializer.data, code=201, msg='OK', status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception as e:
            raise NotFound(e)
        serializer = self.get_serializer(instance)
        return CustomResponse(serializer.data, code=200, msg='OK', status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid()
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return CustomResponse(serializer.data, code=200, msg='OK', status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse(data=[], code=204, msg='OK', status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.enable_flag = 0
        instance.save()

