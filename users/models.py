from django.contrib.auth.models import AbstractUser
from django.db import models


class AuthUser(AbstractUser):
    """
    用户基础表
    """
    SEX_CODE = (
        (0, '男'),
        (1, '女')
    )
    phone = models.CharField(verbose_name='手机号', max_length=256)
    sex = models.SmallIntegerField(choices=SEX_CODE, verbose_name='性别', default=0)
    created_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_date = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self):
        return f'{self.username},{self.email}'

    class Meta:
        verbose_name = '用户基础表'
        verbose_name_plural = '用户基础表'
