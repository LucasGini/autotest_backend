import json
import string
import re
from execute.data_model import CaseInfo


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
    matches = re_string(pattern, data)
    if matches:
        match = matches[0]
        function_name = match[0]
        parameters = match[1]
        if parameters:
            # 如果参数不为空， 则通过','分割,然后去除空格
            parameters = parameters.split(',')
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
    matches = re_string(pattern, data)
    if matches:
        return True
    else:
        return False


def function_parameters_handing(parameters: list, var: dict, dependent: dict) -> list:
    """
    函数参数处理
    :param parameters: 函数参数
    :param var: 全局接口依赖数据
    :param dependent: 当前接口依赖数据
    :return: new_parameters
    """
    new_parameters = []
    for param in parameters:
        # 如果参数前包含'$',需要先从当前接口依赖数据获取数据，再充全局接口依赖数据获取数据
        if param.startswith('$'):
            # 去除$和空格
            param = param.replace('$', '').strip()
            if param in dependent.keys():
                new_param = dependent[param]
                new_parameters.append(new_param)
            elif param in var.keys():
                new_param = var[param]
                new_parameters.append(new_param)
            else:
                raise Exception(f'测试用例中使用的自定义函数的参数:{param}，不存在')
        else:
            new_parameters.append(param)
    return new_parameters


def build_data(initial_data: dict, var: dict, functions: dict, dependent: dict) -> dict or None:
    """
    构建数据
    :param initial_data: 初始数据，需要拼接后使用
    :param var: 依赖参数
    :param functions: 依赖函数
    :param dependent: 依赖参数
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
                    # 参数处理
                    parameters = function_parameters_handing(parameters, var, dependent)
                    if functions_name in functions.keys():
                        var[field] = functions[functions_name](*parameters)
                    else:
                        raise Exception(f'{functions_name}在自定义函数中不存在')
            var.update(dependent)
            data = eval(str_template_insert(data_str, var))
            return data
        else:
            return initial_data
    return None


def build_case_data(case: CaseInfo.dict, var: dict) -> json or dict or None:
    """
    用例请求参数构建
    :param case: 用例信息
    :param var: 全局依赖参数
    :return: json or dict or None
    """
    # 初始化
    body, param, header = None, None, None
    # 获取依赖参数和自定义函数
    dependent = case.get('dependent', {})
    functions = case.get('functions', {})
    if case.get('body', None):
        body_data = build_data(case.get('body', {}), var, functions, dependent)
        body = json.dumps(body_data)
    param = build_data(case.get('param', {}), var, functions, dependent)
    header = build_data(case.get('header', {}), var, functions, dependent)
    return body, param, header


if __name__ == '__main__':
    print(match_func_name_and_parameters('token($user, $passwd)'))
