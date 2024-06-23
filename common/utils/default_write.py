import inspect
from users.models import AuthUser


def caller_function_name():
    """
    获取上上级调用方法名
    """
    frame = inspect.currentframe().f_back.f_back
    caller_name = frame.f_code.co_name
    return caller_name


def default_write(instance: object, request: object) -> object:
    """
    自定义更新方法
    :param instance: 模型实例
    :param request: request
    :return:
    """
    # 获取上级调用方法名
    caller_name = caller_function_name()

    if request:
        user = request.user
        # 如果登录了则通过对象获取用户名
        if isinstance(user, AuthUser):
            if caller_name != 'update' or instance.created_by is None:
                instance.created_by = user.username
            instance.updated_by = user.username
        else:
            if caller_name != 'update' or instance.created_by is None:
                instance.created_by = user
            instance.updated_by = user
        instance.save()
        return instance
    else:
        return instance
