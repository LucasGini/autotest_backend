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


def match_brace(data: str) -> list or None:
    """
    匹配所有${}并返回其包含的内容
    :param data: 被匹配字符串
    :return: list or None
    """
    pattern = r'\${(.*?)}'
    match_fields = re_string(pattern, data)
    return match_fields


def match_func_name_and_parameters(data: str) -> str and list or None:
    """
    从token(param1,...)格式字符串中提取参数和函数名
    :param data: 被匹配字符串
    :return: str , list or None
    """
    pattern = r'(\w+)\(([^)]*)\)'
    matches = re.match(pattern, data)

    if matches:
        function_name = matches.group(1)
        parameters = matches.group(2).split(',')
        parameters = [param.strip() for param in parameters]
        return function_name, parameters
    raise Exception('函数占位格式不正确')


def is_valid_function(data: str) -> bool:
    """
    校验字符串是否为函数(取出大括号里面的占位字符串后，判断是否存在()，如果存在则为函数)
    :param data: 被匹配字符串
    :return:
    """
    pattern = r'\(.*\)'  # 匹配括号内的任意字符和文本
    matches = re.search(pattern, data)
    if matches:
        return True
    else:
        return False


def build_data(initial_data: dict, var: dict, functions: dict) -> dict or None:
    """
    构建数据
    :param initial_data: 初始数据，需要拼接后使用
    :param var: 依赖参数
    :param functions: 依赖函数
    :return: dict or None
    """
    if initial_data:
        # 将入参转换为字符串
        data_str = str(initial_data)
        match_brace_fields = match_brace(data_str)
        # 存在需要匹配的字段body才需要拼接依赖参数
        if match_brace_fields:
            for field in match_brace_fields:
                # 校验是否为函数
                if is_valid_function(field):
                    functions_name, parameters = match_func_name_and_parameters(field)
                    if '$' in parameters:
                        pass
                    else:
                        var[field] = functions[functions_name](*parameters)
            data = eval(str_template_insert(data_str, var))
            return data
        else:
            return initial_data
    return None


def build_case_data(case: dict, var: dict) -> json or dict or None:
    """
    用例请求参数构建
    :param case: 用例信息
    :param var: 依赖参数
    :return: json or dict or None
    """
    # 初始化
    body, param, header = None, None, None
    # 获取依赖函数
    functions = case.get('functions', {})
    if case.get('body', None):
        body_data = build_data(case.get('body', {}), var, functions)
        body = json.dumps(body_data)
    param = build_data(case.get('param', {}), var, functions)
    header = build_data(case.get('header', {}), var, functions)
    return body, param, header

