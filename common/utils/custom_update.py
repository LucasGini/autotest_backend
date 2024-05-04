from rest_framework.utils import model_meta
from common.utils.default_write import default_write


def custom_update(instance: object, request: object) -> object:
    """
    自定义更新方法
    :param instance: 模型实例
    :param request: request
    :return:
    """

    info = model_meta.get_field_info(instance)

    m2m_fields = []
    for attr, value in request.data.items():
        # 判断字段是否存在外键关系，且是否为多对多
        if attr in info.relations and info.relations[attr].to_many:
            m2m_fields.append((attr, value))
        else:
            setattr(instance, attr, value)
    for attr, value in m2m_fields:
        # 关联多对多关系表，更新数据
        field = getattr(instance, attr)
        field.set(value)
    default_write(instance, request)
    return instance
