"""
优化HTMLReport的Result以适配celery
"""
import logging
import os
import threading
import time
from unittest import TestResult
from HTMLReport.src.tools.log.handler_factory import HandlerFactory
from HTMLReport.src.tools import save_images
from HTMLReport.src.tools.result import Result
from HTMLReport.src.tools.retry_on_exception import retry_lists, no_retry_lists
from HTMLReport.src.tools.template import ResultStatus
from common.const.case_const import EXECUTED_COUNT_REDIS_KEY, SUCCESS_COUNT_REDIS_KEY


class ResultNew(Result):

    def __init__(self, lang, tries, delay, back_off, max_delay, retry, thread_start_wait, failed_image,
                 thread_count: int = 1, test_report: object = None, redis_conn: object = None):
        super().__init__(lang, tries, delay, back_off, max_delay, retry, thread_start_wait, failed_image)
        self.thread_count = thread_count
        self.test_output = ''
        self.test_report = test_report or None
        self.redis_conn = redis_conn
        if test_report:
            self.executed_count_key = EXECUTED_COUNT_REDIS_KEY.format(test_report.id)
            self.success_count_key = SUCCESS_COUNT_REDIS_KEY.format(test_report.id)

    def startTest(self, test):
        self.test_output = ''
        if self.thread_start_wait:
            logging.info(
                (self.LANG == "cn" and "测试延迟启动：{}s" or "Test delayed start: {}s").format(self.thread_start_wait)
            )
            time.sleep(self.thread_start_wait)
        logging.info((self.LANG == "cn" and "开始测试： {}" or "Start Test: {}").format(test))
        self.test_output += (self.LANG == "cn" and "开始测试： {}\n" or "Start Test: {}\n").format(test)
        current_id = str(threading.current_thread().ident)
        if current_id in self.result_tmp:
            self.result_tmp[current_id]["tries"] += 1
        else:
            self.result_tmp[current_id] = dict(
                result_code=ResultStatus.PASS,
                testCase_object=test,
                test_output={},
                image_paths={},
                tries=0,
                retry=True,
                style={},
                local_delay=self.delay,
                duration=0
            )

        self.time[str(threading.current_thread().ident)] = time.time()
        TestResult.startTest(self, test)

    def stopTest(self, test):
        end_time = time.time()
        duration = end_time - self.time[str(threading.current_thread().ident)]
        logging.info((self.LANG == "cn" and "测试结束： {}" or "Stop Test: {}").format(test))
        logging.info((self.LANG == "cn" and "耗时： {}" or "Duration: {}").format(duration))
        self.test_output += (self.LANG == "cn" and "测试结束： {}\n" or "Stop Test: {}\n").format(test)
        self.test_output += (self.LANG == "cn" and "耗时： {}\n" or "Duration: {}\n").format(duration)
        current_id = str(threading.current_thread().ident)
        self.result_tmp[current_id]["duration"] += duration
        tries = self.result_tmp[current_id]["tries"]
        if current_id in save_images.image_list:
            tmp = save_images.image_list.pop(current_id)
            if self.failed_image and self.result_tmp[current_id]["result_code"] == ResultStatus.PASS:
                for image_file in map(lambda _: _[-1], tmp):
                    try:
                        os.remove(image_file)
                    except Exception as e:
                        logging.error(f"清理图片文件失败：{e}")
            else:
                self.result_tmp[current_id]["image_paths"][tries] = list(map(lambda _: _[:-1], tmp))
        tmp = HandlerFactory.get_stream_value()
        if tmp:
            self.result_tmp[current_id]["test_output"][tries] = tmp
        else:
            self.result_tmp[current_id]["test_output"][tries] = self.test_output

        # 停止重试
        test_name = test.__class__.__name__ + "." + test.__getattribute__("_testMethodName")
        if (not self.retry and test_name not in retry_lists) or (
                self.retry and test_name in no_retry_lists
        ) or self.tries <= tries or self.result_tmp[current_id]["result_code"] in (
                ResultStatus.PASS, ResultStatus.SKIP
        ):
            self.result_tmp[current_id]["retry"] = False

        if self.result_tmp[current_id]["retry"]:
            # 重试
            if self.result_tmp[current_id]["local_delay"] > self.max_delay:
                self.result_tmp[current_id]["local_delay"] = self.max_delay
            logging.info(
                (self.LANG == "cn" and "等待 {} 秒后重试" or "Retrying in {} seconds...").format(
                    self.result_tmp[current_id]["local_delay"]
                )
            )
            time.sleep(self.result_tmp[current_id]["local_delay"])
            self.result_tmp[current_id]["local_delay"] *= self.back_off
            test(self)
        else:
            # 最后清理
            if current_id in self.success_set:
                self.success_set.remove(current_id)
            if current_id in self.failure_set:
                self.failure_set.remove(current_id)
            if current_id in self.skip_set:
                self.skip_set.remove(current_id)
            if current_id in self.error_set:
                self.error_set.remove(current_id)
            if "retry" in self.result_tmp[current_id]:
                del self.result_tmp[current_id]["retry"]
            if "local_delay" in self.result_tmp[current_id]:
                del self.result_tmp[current_id]["local_delay"]
            # 产生结果
            if self.test_report and self.redis_conn:
                self.redis_conn.set(self.executed_count_key, self.testsRun)
            self.result.append(self.result_tmp.pop(current_id))

    def addSkip(self, test, reason):
        TestResult.addSkip(self, test, reason)

        self._steams_write_doc("Skip", test)

        logging.info((self.LANG == "cn" and "跳过测试： {}\n{}" or "Skip Test: {}\n{}").format(test, reason))
        self.test_output += (self.LANG == "cn" and "跳过测试： {}\n{}\n" or "Skip Test: {}\n{}\n").format(test, reason)
        current_id = str(threading.current_thread().ident)
        self.result_tmp[current_id]["result_code"] = ResultStatus.SKIP
        self.result_tmp[current_id]["style"][self.result_tmp[current_id]["tries"]] = ResultStatus.SKIP
        if self.thread_count <= 1:
            tries = self.result_tmp[current_id]["tries"]
            self.result_tmp[current_id]["test_output"][tries] = 'Skip'
        if current_id not in self.skip_set:
            self.skip_count += 1
            self.skip_set.add(current_id)

    def addSuccess(self, test):
        TestResult.addSuccess(self, test)

        self._steams_write_doc("Pass", test)

        logging.info((self.LANG == "cn" and "测试执行通过： {}" or "Pass Test: {}").format(test))
        self.test_output += (self.LANG == "cn" and "测试执行通过： {}\n" or "Pass Test: {}\n").format(test)
        current_id = str(threading.current_thread().ident)
        self.result_tmp[current_id]["result_code"] = ResultStatus.PASS
        self.result_tmp[current_id]["style"][self.result_tmp[current_id]["tries"]] = ResultStatus.PASS
        if current_id not in self.success_set:
            self.success_count += 1
            if self.test_report and self.redis_conn:
                self.redis_conn.set(self.success_count_key, self.success_count)
            self.success_set.add(current_id)
        if current_id in self.failure_set:
            self.failure_count -= 1
        if current_id in self.error_set:
            self.error_count -= 1

    def addError(self, test, err):
        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]

        self._steams_write_doc("Error", test)

        logging.error((self.LANG == "cn" and "测试产生错误： {}\n{}\n" or "Error Test: {}\n{}\n").format(test, _exc_str))
        self.test_output += (self.LANG == "cn" and "测试产生错误： {}\n{}\n" or "Error Test: {}\n{}\n").format(test, _exc_str)
        current_id = str(threading.current_thread().ident)
        self.result_tmp[current_id]["result_code"] = ResultStatus.ERROR
        self.result_tmp[current_id]["style"][self.result_tmp[current_id]["tries"]] = ResultStatus.ERROR
        if current_id not in self.error_set:
            self.error_count += 1
            self.error_set.add(current_id)

    def addFailure(self, test, err):
        TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]

        self._steams_write_doc("FAIL", test)

        logging.warning((self.LANG == "cn" and "测试未通过： {}\n{}\n" or "Failure: {}\n{}\n").format(test, _exc_str))
        self.test_output += (self.LANG == "cn" and "测试未通过： {}\n{}\n" or "Failure: {}\n{}\n").format(test, _exc_str)
        current_id = str(threading.current_thread().ident)
        self.result_tmp[current_id]["result_code"] = ResultStatus.FAIL
        self.result_tmp[current_id]["style"][self.result_tmp[current_id]["tries"]] = ResultStatus.FAIL
        if current_id not in self.failure_set:
            self.failure_count += 1
            self.failure_set.add(current_id)


