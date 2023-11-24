import os
import django
from celery import Celery

# 设置默认的 Django settings 模块名称
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autotest_backend.settings')
django.setup()
celery_app = Celery('autotest_backend')

# 从 Django 的设置中加载配置
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动查找和注册所有已定义的 Celery 任务
celery_app.autodiscover_tasks()