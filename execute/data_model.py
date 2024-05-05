from typing import Dict, List, Text
from pydantic import BaseModel, HttpUrl


Assertion = List[Dict[Text, Dict[Text, Text]]]
Fetch = List[Dict[Text, Text]]


class CaseInfo(BaseModel):
    """
    用例字段定义
    """
    # 用例ID
    id: int = None
    # 用例名称
    name: Text = ''
    # 前置用例
    preconditions: List = []
    # 请求方法
    method: Text = ''
    # URL
    url: HttpUrl = None
    # 请求头
    header: Dict = {}
    # 请求参数
    param: Dict = {}
    # 请求数据
    body: Dict = {}
    # 断言规则
    assertion: Assertion = []
    # 取值逻辑
    fetch: Fetch = []
    # 自定义函数
    functions: Dict = {}
    # 依赖参数
    dependent: Dict = {}
