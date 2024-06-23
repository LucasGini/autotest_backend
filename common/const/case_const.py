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


class ReportStatus(Enum):
    """
    报告状态枚举
    """
    # 执行失败
    EXECUTED_FAILED = 0
    # 执行成功
    EXECUTED_SUCCESS = 1
    # 执行中
    EXECUTING = 2


# test_report.success_count Redis Key
SUCCESS_COUNT_REDIS_KEY = 'success_count_of_report_id_{}'

# test_report.executed_count Redis Key
EXECUTED_COUNT_REDIS_KEY = 'executed_count_of_report_id_{}'

# kafka topic
# 项目删除后触发topic
KAFKA_PROJECT_DELETED_TOPIC = 'kafka_project_deleted_topic'

if __name__ == '__main__':
    print(ExecuteType.CASE.value)
