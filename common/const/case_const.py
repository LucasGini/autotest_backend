from enum import Enum

# 请求方法常量
METHOD_CONST = {
    0: 'GET',
    1: 'POST',
    2: 'PUT',
    3: 'PATCH',
    4: 'DELETE',
    5: 'OPTIONS'
}


class ExecuteType(Enum):
    """
    执行类型枚举
    """
    # 用例执行
    CASE = 10
    # 项目执行
    PROJECT = 20
    # 用例集执行
    SUITE = 30

if __name__ == '__main__':
    print(ExecuteType.CASE.value)
