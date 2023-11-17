from rest_framework.views import exception_handler


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
