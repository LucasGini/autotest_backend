from celery import shared_task
from execute.setattr_public_test import SetattrPublicTestCase


@shared_task
def run_case(cases, env, report_name, execute_type):
    SetattrPublicTestCase(cases, env, report_name, execute_type).test_main()
