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
    port = models.CharField(verbose_name='端口号', max_length=64, blank=True, null=True)
    remark = models.CharField(verbose_name='简要说明', max_length=256, blank=True, null=True)

    def __str__(self):
        return self.env_name

    class Meta:
        verbose_name = '测试环境表'
        verbose_name_plural = '测试环境表'
        db_table = 'test_env'


class SystemMenu(BaseModel):
    """
    系统菜单表
    """

    name = models.CharField(verbose_name='菜单名称', max_length=64)
    path = models.CharField(verbose_name='菜单路径', max_length=128)
    component = models.CharField(verbose_name='组件', max_length=128)
    icon = models.CharField(verbose_name='菜单icon', max_length=256)
    parent_id = models.BigIntegerField(verbose_name='父菜单id', blank=True, null=True)
    order_num = models.IntegerField(verbose_name='菜单排序', default=0)
    is_hidden = models.SmallIntegerField(verbose_name='是否隐藏', choices=BaseModel.ENABLE_CONST, default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '系统菜单表'
        verbose_name_plural = '系统菜单表'
        db_table = 'system_menu'


class CategoryConfig(BaseModel):
    """
    参数配置表
    """
    category_group = models.CharField(verbose_name='类别组', max_length=256)
    category_name = models.CharField(verbose_name='类别名', max_length=256)
    category_code = models.CharField(verbose_name='类别code', max_length=256, null=True, blank=True)
    category_description = models.CharField(verbose_name='描述', max_length=2048, null=True, blank=True)
    category_parent_id = models.BigIntegerField(verbose_name='父id', default=0)
    sort_number = models.SmallIntegerField(verbose_name='排序', default=0)
    readonly = models.BooleanField(verbose_name='是否只读', default=False)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = '类型配置表'
        verbose_name_plural = '类型配置表'
        db_table = 'category_config'
