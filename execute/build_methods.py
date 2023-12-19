import types


def create_dynamic_module(method_str: str) -> types.ModuleType:
    """
    创建动态模块,并将字符串中的函数放入其中
    :param method_str: 包含函数的字符串
    :return: module
    """
    module = types.ModuleType("dynamic_module")
    exec(method_str, module.__dict__)
    return module


def get_all_function_from_module(module: types.ModuleType) -> dict:
    """
    获取模块里面的所有函数
    :param module: 模块
    :return: dict
    """
    function_dict = {}
    for member in dir(module):
        member = getattr(module, member)
        if callable(member):
            function_dict[member.__name__] = member
    return function_dict


if __name__ == '__main__':
    method_str1 = """
def print_hello_word():
    print('hello word!')
"""
    mod = create_dynamic_module(method_str1)
    a = get_all_function_from_module(mod)
    print(a)

