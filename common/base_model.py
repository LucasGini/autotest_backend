from django.db import models


class BaseModel(models.Model):
    """
    基础模型
    """
    ENABLE_CONST = (
        (0, '失效'),
        (1, '生效')
    )
    enable_flag = models.SmallIntegerField(verbose_name='有效标识', choices=ENABLE_CONST, null=True, blank=True, default=1)
    created_by = models.CharField(verbose_name='创建人', max_length=128, null=True, blank=True)
    created_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True, blank=True)
    updated_by = models.CharField(verbose_name='更新人', max_length=128, null=True, blank=True)
    updated_date = models.DateTimeField(verbose_name='更新时间', auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True
