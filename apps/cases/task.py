from celery import shared_task
from execute.setattr_public_test import SetattrPublicTestCase


@shared_task
def run_case(cases, env):
    SetattrPublicTestCase(cases, env).test_main()
