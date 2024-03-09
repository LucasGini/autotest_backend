from pydantic import BaseModel


class ExecuteRequestModel(BaseModel):
    """
    同步执行请求参数定义
    """
    # 执行类型
    executeType: int = None
    # 环境id
    envId: int = None
    # 项目id
    projectId: int = None
    # 用例集id
    suiteId: int = None
    # 用例id
    caseId: int = None


class AsyncExecuteRequestModel(BaseModel):
    """
    异步执行请求参数定义
    """
    # 执行类型
    executeType: int = None
    # 环境id
    envId: int = None
    # 项目id
    projectId: int = None
    # 用例集id
    suiteId: int = None
    # 用例id
    caseId: int = None


