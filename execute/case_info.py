from typing import Dict, List, Text
from pydantic import BaseModel, HttpUrl


Verify = List[Dict[Text, Dict[Text, Text]]]
Fetch = List[Dict[Text, Text]]


class CaseInfo(BaseModel):
    """
    用例字段定义
    """
    preconditions: List = []
    method: Text = None
    url: HttpUrl = None
    header: Dict = {}
    param: Dict = {}
    body: Dict = {}
    verify: Verify = []
    fetch: Fetch = []


if __name__ == '__main__':
    print(CaseInfo().dict())
