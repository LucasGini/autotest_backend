from common.base_model import BaseModel
from django.db import models
from apps.users.models import AuthUser


class TestCase(BaseModel):
    """
    测试用例
    """

    # 优先级
    PRIORITY_CODE = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4)
    )

    # 请求方法
    METHOD_CODE = (
        (0, 'GET'),
        (1, 'POST'),
        (2, 'PUT'),
        (3, 'PATCH'),
        (4, 'DELETE'),
        (5, 'OPTIONS'),
    )

    case_name = models.CharField(verbose_name='用例名称', max_length=128)
    project = models.ForeignKey('ProjectsInfo', on_delete=models.DO_NOTHING, verbose_name='项目')
    priority = models.SmallIntegerField(verbose_name='优先级', choices=PRIORITY_CODE)
    method = models.SmallIntegerField(verbose_name='请求方法', choices=METHOD_CODE)
    path = models.CharField(verbose_name='路径', max_length=256)
    data = models.TextField(verbose_name='请求数据')

    def __str__(self):
        return self.case_name

    class Meta:
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例'


class TestSuite(BaseModel):
    """
    测试用例集表
    """
    suite_name = models.CharField(verbose_name='用例集名称', max_length=128)
    case = models.ManyToManyField('TestCase', verbose_name='测试用例')
    remark = models.CharField(verbose_name='简要说明', max_length=256, blank=True, null=True)

    def __str__(self):
        return self.suite_name

    class Meta:
        verbose_name = '测试用例集表'
        verbose_name_plural = '测试用例集表'


class ProjectsInfo(BaseModel):
    """
    项目表
    """

    project_name = models.CharField(verbose_name='项目名称', max_length=128)
    responsible = models.ForeignKey('users.AuthUser', on_delete=models.DO_NOTHING, verbose_name='责任人')
    remark = models.CharField(verbose_name='简要说明', max_length=256, blank=True, null=True)

    def __str__(self):
        return self.project_name

    class Meta:
        verbose_name = '项目表'
        verbose_name_plural = '项目表'


class Precondition(BaseModel):
    """
    前置条件表
    """
    precondition_case = models.CharField(verbose_name='前置用例集合', max_length=512)
    case = models.ForeignKey('TestCase', on_delete=models.CASCADE, verbose_name='主用例')

    def __str__(self):
        return f'{self.case}:{self.precondition_case}'

    class Meta:
        verbose_name = '前置条件表'
        verbose_name_plural = '前置条件表'
