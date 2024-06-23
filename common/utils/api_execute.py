from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from cases.models import TestCase, TestSuite
from common.custom_exception import ParamException


def case_execute(request: Request):
    """
    用例执行方法
    :param request: 请求参数
    :return: CustomResponse
    """

    case_id = request.data.get('caseId', [])
    if not case_id:
        raise ParamException('caseId参数不能为空')
    query = Q(id=case_id) & Q(enable_flag=1)
    queryset = TestCase.objects.all().filter(query)
    if not queryset:
        raise NotFound('用例不存在')
    cases = list(queryset)
    report_name = cases[0].case_name
    return cases, report_name


def suite_execute(request: Request):
    """
    用例集执行方法
    :param request: 请求参数
    :return: CustomResponse
    """

    suite_id = request.data.get('suiteId', None)
    if suite_id is None:
        raise ParamException('suiteId参数不能为空')
    try:
        test_suite = TestSuite.objects.get(id=suite_id, enable_flag=1)
    except Exception:
        raise NotFound('用例集不存在')
    report_name = test_suite.suite_name
    test_cases = test_suite.case.all().filter(enable_flag=1)
    if not test_cases.exists():
        raise NotFound('用例集不存在用例')
    cases = list(test_cases)
    return cases, report_name


def project_execute(request: Request):
    """
    项目执行方法
    :param request: 请求参数
    :return: CustomResponse
    """

    project_id = request.data.get('projectId', None)
    if project_id is None:
        raise ParamException('projectId参数不能为空')
    query = Q(project_id=project_id) & Q(enable_flag=1)
    queryset = TestCase.objects.all().filter(query)
    if not queryset.exists():
        raise NotFound('该项目id用例不存在')
    cases = list(queryset)
    report_name = cases[0].project.project_name
    return cases, report_name
