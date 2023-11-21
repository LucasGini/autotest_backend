from apps.cases.models import Precondition


def build_case_info(instance):
    """
    构建用例信息
    :param instance: 用例实例
    :return:
    """
    case_info = {}
    try:
        precondition_obj = Precondition.objects.get(case=instance.id)
        precondition = precondition_obj.precondition_case
    except Precondition.DoesNotExist:
        precondition = None
    setattr(case_info, 'precondition',  precondition)
    setattr(case_info, 'path', instance.path)
    setattr(case_info, 'method', instance.method)
    data = instance.data
    if instance(data, dict):
        header = data.get('header', None)

