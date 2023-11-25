from celery import shared_task
from execute.public_test import PublicTestCase


@shared_task
def run_case(cases, env):
    PublicTestCase(cases, env).test_main()
