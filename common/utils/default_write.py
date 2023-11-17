from apps.users.models import AuthUser


def default_write(obj, request):
    """
    创建时间等字段默认填写
    """
    if request:
        user = request.user
        # 如果登录了则通过对象获取用户名
        if isinstance(user, AuthUser):
            obj.created_by = user.username
            obj.updated_by = user.username
        else:
            obj.created_by = user
            obj.updated_by = user
        obj.save()
        return obj
    else:
        return obj
