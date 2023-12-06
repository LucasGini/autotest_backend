import json
import string
import re


def str_template_insert(template: str, var: dict) -> any:
    """
    字符串模板插入
    param: template 模板
    param: var 插入值（字典，key需要与body中标记的key一致）
    """
    # 初始化
    false, true, null = False, True, ''
    # 字符串模板插入
    data = string.Template(template).safe_substitute(var)
    return data


def re_string(pattern: str, text: str) -> list or bool:
    """
    通过正则表达式匹配字符串内的数据
    :param pattern: 正则表达式
    :param text:  字符串
    :return: list or bool
    """
    match = re.findall(pattern, text)
    if match:
        return match
    else:
        return False


def build_data(initial_data: dict, var: dict) -> dict or None:
    """
    构建数据
    :param initial_data: 初始数据，需要拼接后使用
    :param var: 依赖参数
    :return: dict or None
    """
    if initial_data:
        # 将入参转换为字符串
        data_str = str(initial_data)
        # 正则表达式，获取到 ${} 之间的字段
        pattern = r'\${(.*?)}'
        match_fields = re_string(pattern, data_str)
        # 存在需要匹配的字段body才需要拼接依赖参数
        if match_fields:
            data = eval(str_template_insert(data_str, var))
            return data
        else:
            return initial_data
    return initial_data


def build_case_data(case: dict, var: dict) -> json or dict or None:
    """
    用例请求参数构建
    :param case: 用例信息
    :param var: 依赖参数
    :return: json or dict or None
    """
    body, param, header = None, None, None
    if case.get('body', None):
        body_data = build_data(case.get('body', None), var)
        body = json.dumps(body_data)
    if case.get('param', None):
        param = build_data(case.get('param', None), var)
    if case.get('header', None):
        header = build_data(case.get('header', None), var)
    return body, param, header

