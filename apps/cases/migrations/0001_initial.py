# Generated by Django 4.1 on 2023-11-15 15:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectsInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=128, verbose_name='项目名称')),
                ('remark', models.CharField(blank=True, max_length=256, null=True, verbose_name='简要说明')),
                ('responsible',models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='责任人')),
                ('enable_flag', models.SmallIntegerField(blank=True, choices=[(0, '失效'), (1, '生效')], null=True, verbose_name='有效标识')),
                ('created_by', models.CharField(blank=True, max_length=128, null=True, verbose_name='创建人')),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('updated_by', models.CharField(blank=True, max_length=128, null=True, verbose_name='更新人')),
                ('updated_date', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '项目表',
                'verbose_name_plural': '项目表',
            },
        ),
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('case_name', models.CharField(max_length=128, verbose_name='用例名称')),
                ('priority', models.SmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)], verbose_name='优先级')),
                ('method', models.SmallIntegerField(choices=[(0, 'GET'), (1, 'POST'), (2, 'PUT'), (3, 'PATCH'), (4, 'DELETE'), (5, 'OPTIONS')], verbose_name='请求方法')),
                ('path', models.CharField(max_length=256, verbose_name='路径')),
                ('data', models.TextField(verbose_name='请求数据')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cases.projectsinfo', verbose_name='项目')),
                ('enable_flag', models.SmallIntegerField(blank=True, choices=[(0, '失效'), (1, '生效')], null=True, verbose_name='有效标识')),
                ('created_by', models.CharField(blank=True, max_length=128, null=True, verbose_name='创建人')),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('updated_by', models.CharField(blank=True, max_length=128, null=True, verbose_name='更新人')),
                ('updated_date', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '测试用例',
                'verbose_name_plural': '测试用例',
            },
        ),
        migrations.CreateModel(
            name='TestSuite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suite_name', models.CharField(max_length=128, verbose_name='用例集名称')),
                ('case', models.ManyToManyField(to='cases.testcase', verbose_name='测试用例')),
                ('remark', models.CharField(blank=True, max_length=256, null=True, verbose_name='简要说明')),
                ('enable_flag', models.SmallIntegerField(blank=True, choices=[(0, '失效'), (1, '生效')], null=True, verbose_name='有效标识')),
                ('created_by', models.CharField(blank=True, max_length=128, null=True, verbose_name='创建人')),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('updated_by', models.CharField(blank=True, max_length=128, null=True, verbose_name='更新人')),
                ('updated_date', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '测试用例集表',
                'verbose_name_plural': '测试用例集表',
            },
        ),
        migrations.CreateModel(
            name='Precondition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('precondition_case', models.CharField(max_length=512, verbose_name='前置用例集合')),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cases.testcase', verbose_name='主用例')),
                ('enable_flag', models.SmallIntegerField(blank=True, choices=[(0, '失效'), (1, '生效')], null=True, verbose_name='有效标识')),
                ('created_by', models.CharField(blank=True, max_length=128, null=True, verbose_name='创建人')),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('updated_by', models.CharField(blank=True, max_length=128, null=True, verbose_name='更新人')),
                ('updated_date', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '前置条件表',
                'verbose_name_plural': '前置条件表',
            },
        ),
    ]