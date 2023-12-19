"""
优化HTMLReport模块，适配celery
"""
import datetime
import logging
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Manager
from unittest.suite import TestSuite
from HTMLReport import TestRunner
from common.HTMLReport.ResultNew import ResultNew


def _isnotsuite(test):
    """A crude way to tell apart testcases and suites with duck-typing

    :param test:
    :return:
    """
    try:
        iter(test)
    except TypeError:
        return True
    return False


class HTMLReportNew(TestRunner):
    """测试执行器"""

    def __init__(self, report_file_name: str = None, log_file_name: str = None, output_path: str = None,
                 title: str = None, description: str = None, tries: int = 0, delay: float = 1, back_off: float = 1,
                 max_delay: float = 120, retry: bool = True, thread_count: int = 1, thread_start_wait: float = 0,
                 sequential_execution: bool = False, lang: str = "cn", image: bool = True, failed_image: bool = False):
        """测试执行器

        :param report_file_name: 报告文件名，如果未赋值，将采用“test+时间戳”
        :param log_file_name: 日志文件名，如果未赋值，将采用报告文件名，如果报告文件名也没有，将采用“test+时间戳”
        :param output_path: 报告保存文件夹名，默认“report”
        :param title: 报告标题，默认“测试报告”
        :param description: 报告描述，默认“无测试描述”
        :param tries: 重试次数
        :param delay: 重试延迟间隔，单位为 秒
        :param back_off: 扩展每次重试等待时间的乘数
        :param max_delay: 最大重试等待时间长度，单位为 秒
        :param retry: 如果为 True 表示所有用例遵循重试规则，False 只针对添加了 @retry 用例有效
        :param thread_count: 并发线程数量（无序执行测试），默认数量 1
        :param thread_start_wait: 各线程启动延迟，默认 0 s
        :param sequential_execution: 是否按照套件添加(addTests)顺序执行， 会等待一个addTests执行完成，再执行下一个，默认 False。
                如果用例中存在 tearDownClass ，建议设置为True，否则 tearDownClass 将会在所有用例线程执行完后才会执行。
        :param lang: ("cn", "en") 支持中文与英文报告输出，默认采用中文
        :param image: 默认支持添加图片，False 放弃所有图片添加
        :param failed_image: true 只有失败才添加图片，成功用例添加的图片会被删除
        """
        super().__init__(report_file_name, log_file_name, output_path, title, description, tries, delay, back_off,
                         max_delay, retry, thread_count, thread_start_wait, sequential_execution, lang, image,
                         failed_image)
        self.tc_dict = Manager().dict() if thread_count > 1 else {}

    def _thread_pool_executor_test_case(self, tmp_list, result):
        """重写多线程运行方法,如果线程数为1，则不使用多线程"""
        if self.thread_count > 1:
            t_list = []
            with ThreadPoolExecutor(self.thread_count) as pool:
                for test_case in tmp_list:
                    if _isnotsuite(test_case):
                        self._tearDownPreviousClass(test_case, result)
                        self._handleModuleFixture(test_case, result)
                        self._handleClassSetUp(test_case, result)
                        result._previousTestClass = test_case.__class__

                        if (getattr(test_case.__class__, "_classSetupFailed", False) or
                                getattr(result, "_moduleSetUpFailed", False)):
                            continue
                    while len(t_list) == self.thread_count:
                        [t_list.remove(t) for t in t_list if t.done()]
                    t_list.append(pool.submit(test_case, result))

                    self.tc_dict[test_case.__class__] -= 1
                    if self.tc_dict[test_case.__class__] == 0:
                        self._tearDownPreviousClass(None, result)
        else:
            for test_case in tmp_list:
                if _isnotsuite(test_case):
                    self._tearDownPreviousClass(test_case, result)
                    self._handleModuleFixture(test_case, result)
                    self._handleClassSetUp(test_case, result)
                    result._previousTestClass = test_case.__class__

                    if (getattr(test_case.__class__, "_classSetupFailed", False) or
                            getattr(result, "_moduleSetUpFailed", False)):
                        continue
                    test_case(result)
                    self._tearDownPreviousClass(None, result)
        self._handleModuleTearDown(result)

    def run(self, test: TestSuite, debug: bool = False, threadSuite=0):
        """
        重写run方法
        :param test:
        :param debug:
        :param threadSuite:
        :return:
        """

        if debug:
            logging.getLogger().setLevel(logging.DEBUG)

        result = ResultNew(self.LANG, self.tries, self.delay, self.back_off, self.max_delay, self.retry,
                           self.thread_start_wait, self.failed_image, self.thread_count)
        if self.LANG == "cn":
            logging.info(f"预计并发线程数：{str(self.thread_count)}")
        else:
            logging.info(f"The number of concurrent threads is expected to be {str(self.thread_count)}")

        for test_case in test:
            tmp_class_name = test_case.__class__
            if tmp_class_name not in self.tc_dict:
                self.tc_dict[tmp_class_name] = 0
            else:
                self.tc_dict[tmp_class_name] += 1

        if self.sequential_execution:
            # 执行套件添加顺序
            test_case_queue = queue.Queue()
            test_case_arr = []
            tmp_key = None
            for test_case in test:
                tmp_class_name = test_case.__class__
                if tmp_key == tmp_class_name:
                    test_case_arr.append(test_case)
                else:
                    tmp_key = tmp_class_name
                    if len(test_case_arr) != 0:
                        test_case_queue.put(test_case_arr.copy())
                        test_case_arr.clear()
                    test_case_arr.append(test_case)
            if len(test_case_arr) != 0:
                test_case_queue.put(test_case_arr.copy())
            while not test_case_queue.empty():
                tmp_list = test_case_queue.get()
                self._thread_pool_executor_test_case(tmp_list, result)
        else:
            if threadSuite and self.thread_count > 1:
                # edit by Joffrey
                # 按用例组多线程执行
                self.result_list = []
                with ThreadPoolExecutor(max_workers=threadSuite) as ts:
                    for suite in test:
                        __result = ResultNew(self.LANG, self.tries, self.delay, self.back_off, self.max_delay,
                                             self.retry, self.thread_start_wait, self.failed_image, self.thread_count)
                        self.result_list.append(__result)
                        ts.submit(suite.run, result=__result)
                        time.sleep(1)
                result = self.merge_result()
            else:
                # 无序执行
                self._thread_pool_executor_test_case(test, result)

        self.stopTime = datetime.datetime.now()
        if result.stdout_steams.getvalue().strip():
            logging.info(result.stdout_steams.getvalue())
        if result.stderr_steams.getvalue().strip():
            logging.error(result.stderr_steams.getvalue())

        if self.LANG == "cn":
            s = "\n测试结束！\n运行时间: {time}\n共计执行用例数量：{count}\n执行成功用例数量：{Pass}" \
                "\n执行失败用例数量：{fail}\n跳过执行用例数量：{skip}\n产生异常用例数量：{error}\n"
        else:
            s = "\nEOT！\nRan {count} tests in {time}\n\nPASS：{Pass}" \
                "\nFailures：{fail}\nSkipped：{skip}\nErrors：{error}\n"
        count = result.success_count + result.failure_count + result.error_count + result.skip_count
        s = s.format(
            time=self.stopTime - self.startTime,
            count=count,
            Pass=result.success_count,
            fail=result.failure_count,
            skip=result.skip_count,
            error=result.error_count
        )
        self._generate_report(result)
        logging.info(s)

        return result
