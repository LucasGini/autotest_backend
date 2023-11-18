import inspect
from apps.users.models import AuthUser


def caller_function_name():
    """
    获取上上级调用方法名
    """
    frame = inspect.currentframe().f_back.f_back
    caller_name = frame.f_code.co_name
    return caller_name


def default_write(obj, request):
    """
    创建时间等字段默认填写
    """
    # 获取上级调用方法名
    caller_name = caller_function_name()

    if request:
        user = request.user
        # 如果登录了则通过对象获取用户名
        if isinstance(user, AuthUser):
            if caller_name != 'update' or obj.created_by is None:
                obj.created_by = user.username
            obj.updated_by = user.username
        else:
            if caller_name != 'update' or obj.created_by is None:
                obj.created_by = user
            obj.updated_by = user
        obj.save()
        return obj
    else:
        return obj
