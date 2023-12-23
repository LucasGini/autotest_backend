from rest_framework import status
from django.utils.translation import gettext_lazy as _
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException


def custom_exception_handler(exc, context):
    """
    自定义异常类
    """
    response = exception_handler(exc, context)
    if response is not None:
        response.data.clear()
        # 组装code、 msg 和data
        response.data['data'] = []
        response.data['code'] = response.status_code
        response.data['msg'] = exc.detail
        response.data['path'] = context['request'].path
    return response


class ParamException(APIException):
    """
    参数异常类
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('bad request.')
    default_code = 'bad_request'
