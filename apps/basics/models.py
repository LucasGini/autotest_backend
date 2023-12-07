from common.base_model import BaseModel
from django.db import models


class TestEnv(BaseModel):
    """
    测试环境表
    """

    AGREEMENT_CODE = (
        (0, 'http'),
        (1, 'https')
    )

    env_name = models.CharField(verbose_name='环境名称', max_length=256)
    agreement = models.SmallIntegerField(verbose_name='协议', choices=AGREEMENT_CODE)
    hosts = models.CharField(verbose_name='域名或ip', max_length=256)
    port = models.CharField(verbose_name='端口号', max_length=64)
    remark = models.CharField(verbose_name='简要说明', max_length=256, blank=True, null=True)

    def __str__(self):
        return self.env_name

    class Meta:
        verbose_name = '测试环境表'
        verbose_name_plural = '测试环境表'
        db_table = 'test_env'
