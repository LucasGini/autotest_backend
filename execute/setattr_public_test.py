import copy
import jsonpath
import requests
import unittest
import typing
from apps.cases.models import Precondition, TestCase, DependentMethods
from common.const.basic_const import AGREEMENT_CONST
from common.const.case_const import METHOD_CONST
from execute.build_methods import create_dynamic_module, get_all_function_from_module
from execute.data_model import CaseInfo
from execute.data_handling import build_case_data
from execute.HTMLReport.HTMLReportNew import TestRunner


class TestBase(unittest.TestCase):
    """
    测试基类
    """

    def fetch_data(self, fetch, response_json):
        """
        取值
        :param response_json: 接口返回值
        :param fetch:  取值规则
        :return:
        """

        if isinstance(fetch, list) is False:
            raise Exception('取值规则不为list类型')
        for f in fetch:
            for key, f_path in f.items():
                self.var[key] = jsonpath.jsonpath(response_json, f_path)

    def assert_verify(self, rules, response_json):
        """
        断言校验
        :param response_json: 接口返回值
        :param rules:  断言规则
        :return:
        """

        if isinstance(rules, list) is False:
            raise Exception('断言规则不为list类型')
            # 遍历所有断言规则
        for rule in rules:
            if isinstance(rule, dict) is False:
                raise Exception('断言子规则不为dict类型')
            ass, v0, v1, v2 = 'assertEqual', None, None, None
            for ass, d in rule.items():
                if isinstance(d, dict) is False:
                    raise Exception('断言规则定义不为dict类型')
                path = d.get('path', None)
                types = d.get('types', None)
                value = d.get('value', None)
                if path is not None:
                    v0 = jsonpath.jsonpath(response_json, path)
                if types is not None and value is not None:
                    v1 = self.get_data_type(types, value)
                v2 = d.get('msg', None)
            self.get_assert(ass, v0, v1, v2)

    @staticmethod
    def get_data_type(data_type: str, value: typing.Any) -> typing.Any:
        """
        将数据转换为对应类型
        :param data_type: 数据类型
        :param value: 需要转换的数据
        :return: 转换后的数据
        """

        if data_type == 'int':
            return int(value)
        if data_type == 'float':
            return float(value)
        if data_type == 'bool':
            return bool(value)
        if data_type == 'str':
            return str(value)
        if data_type == 'list':
            return list(value)
        if data_type == 'tuple':
            return tuple(value)
        if data_type == 'set':
            return set(value)
        if data_type == 'dict':
            return dict(value)
        raise Exception('不存在该种数据类型')

    def get_assert(self, ass, *args):
        """
        获取断言方法
        :param ass:  断言类型
        :return:
        """
        if ass == 'assertEqual':
            return self.assertEqual(args[0], args[1], args[2])
        if ass == 'assertNotEqual':
            return self.assertNotEqual(args[0], args[1], args[2])
        if ass == 'assertTrue':
            return self.assertTrue(args[0], args[2])
        if ass == 'assertFalse':
            return self.assertFalse(args[0], args[2])
        if ass == 'assertIs':
            return self.assertIs(args[0], args[1], args[2])
        if ass == 'assertIsNot':
            return self.assertIsNot(args[0], args[1], args[2])
        if ass == 'assertIsNone':
            return self.assertIsNone(args[0], args[2])
        if ass == 'assertIsNotNone':
            return self.assertIsNotNone(args[0], args[2])
        if ass == 'assertIn':
            return self.assertIn(args[0], args[1], args[2])
        if ass == 'assertNotIn':
            return self.assertNotIn(args[0], args[1], args[2])
        if ass == 'assertIsInstance':
            return self.assertIsInstance(args[0], args[1], args[2])
        if ass == 'assertNotIsInstance':
            return self.assertNotIsInstance(args[0], args[1], args[2])
        if ass == 'assertAlmostEqual':
            return self.assertAlmostEqual(args[0], args[1], args[2])
        if ass == 'assertNotAlmostEqual':
            return self.assertNotAlmostEqual(args[0], args[1], args[2])
        if ass == 'assertGreater':
            return self.assertGreater(args[0], args[1], args[2])
        if ass == 'assertGreaterEqual':
            return self.assertGreaterEqual(args[0], args[1], args[2])
        if ass == 'assertLess':
            return self.assertLess(args[0], args[1], args[2])
        if ass == 'assertLessEqual':
            return self.assertLessEqual(args[0], args[1], args[2])
        if ass == 'assertRegex':
            return self.assertRegex(args[0], args[1], args[2])
        if ass == 'assertNotRegex':
            return self.assertNotRegex(args[0], args[1], args[2])
        raise Exception('不存在该种断言类型')

    def setUp(self):
        self.var = {}

    def tearDown(self):
        self.var = {}


class SetattrPublicTestCase:
    """
    公共测试类
    """

    def __init__(self, case_list, test_env):
        self.case_list = case_list
        self.test_env = test_env
        self.dependent_method = {}

    def build_case_info(self, instance, level=0, max_depth=3) -> CaseInfo.dict:
        """
        构建用例信息
        :param max_depth: 设置最大递归深度,默认3
        :param level: 递归深度
        :param instance: case实例
        :return: CaseInfo.dict
        """
        if level > max_depth:
            raise Exception('已超过最大递归深度, 请检查前置用例是否嵌套超过4次或者循环依赖了')
        # 获取用例信息定义
        case_info = CaseInfo()
        case_info.name = instance.case_name
        case_info.id = instance.id
        # 构建依赖函数
        case_info.functions = copy.deepcopy(self.build_dependent_methods(instance.project_id))  # 深度copy，防止后续操作影响
        try:
            precondition_obj = Precondition.objects.get(case_id=instance.id, enable_flag=1)
            precondition_case_ids = eval(precondition_obj.precondition_case)
        except Precondition.DoesNotExist:
            precondition_case_ids = []
        precondition_cases = []
        if precondition_case_ids and isinstance(precondition_case_ids, list):
            for case_id in precondition_case_ids:
                try:
                    case_obj = TestCase.objects.get(id=case_id)
                    # 递归获取构建前置用例
                    precondition_cases.append(self.build_case_info(case_obj, level + 1))
                except Exception:
                    continue
        case_info.preconditions = precondition_cases
        case_info.method = METHOD_CONST[instance.method]
        case_info.url = self.build_test_url(instance)
        data = eval(instance.data)
        if isinstance(data, dict):
            case_info.header = data.get('header', {})
            case_info.param = data.get('param', {})
            case_info.body = data.get('body', {})
            case_info.verify = data.get('verify', [])
            case_info.fetch = data.get('fetch', [])
            case_info.dependent = data.get('dependent', {})
        else:
            raise Exception('用例数据格式不正确')
        return case_info.dict()

    def build_test_url(self, case):
        """
        构建测试url
        :param case: 用例实例
        :return: url
        """
        agreement = AGREEMENT_CONST[self.test_env.agreement]
        hosts = str(self.test_env.hosts)
        port = str(self.test_env.port)
        path = str(case.path)
        if port:
            url = agreement + '://' + hosts + ':' + port + path
        else:
            url = agreement + '://' + hosts + path

        return url

    def build_dependent_methods(self, project_id) -> dict:
        """
        构建依赖函数
        :param project_id: 项目ID
        :return: {}
        """
        try:
            dependent_obj = DependentMethods.objects.get(project_id=project_id)
        except Exception:
            return {}
        function_str = dependent_obj.dependent_method
        if function_str:
            module = create_dynamic_module(function_str)
            function_dict = get_all_function_from_module(module)
            # 如果project_id存在dependent_method中，则返回对应的值，否则插入一个新的键值对，并返回function_dict
            return self.dependent_method.setdefault(project_id, function_dict)
        return {}

    def load_test_case(self):
        """
        测试用例加载
        """
        for instance in self.case_list:
            case_info = self.build_case_info(instance)

            def test_case(self, case=case_info):
                preconditions = case.get('preconditions', None)
                # 判断是否存在前置用例
                if preconditions and isinstance(preconditions, list):
                    # 获取测试用例执行方法，递归执行前置用例，获取依赖值
                    case_execute = getattr(self, 'case_execute')
                    for p in preconditions:
                        case_execute(p)
                # 构建请求数据
                body, param, header = build_case_data(case, self.var)
                url = case.get('url', None)
                method = case.get('method', None)
                # 请求头、url、请求方法不为空才发起请求
                if header is None or url is None or method is None:
                    raise Exception('请求头、url或者请求方法为空')
                response = requests.request(method=method, url=url, params=param, data=body, headers=header)
                response_json = response.json()
                verify = case.get('verify', None)
                # 断言规则不为空，则进行断言
                if verify:
                    self.assert_verify(verify, response_json)
                fetch = case.get('fetch', None)
                # 取值规则不为空，则进行取值
                if fetch:
                    self.fetch_data(fetch, response_json)

            if getattr(TestBase, 'case_execute', None) is None:
                # 将case_execute动态加载到TestBase类，方便递归调用
                setattr(TestBase, 'case_execute', test_case)
            # 修改方法描述文档
            test_case.__doc__ = case_info.get('name', None)
            # 使用setattr函数动态创建测试方法
            setattr(TestBase, f'test_case_id_is_{instance.id}', test_case)

    def test_main(self):
        """
        测试主方法
        """
        self.load_test_case()
        # 创建测试套件
        # unittest.main()
        suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
        # 测试用例执行器
        runner = TestRunner(report_file_name='test',  # 报告文件名，如果未赋值，将采用“test+时间戳”
                            output_path='report',  # 保存文件夹名，默认“report”
                            title='测试报告',  # 报告标题，默认“测试报告”
                            description='无测试描述',  # 报告描述，默认“测试描述”
                            lang='cn'  # 支持中文与英文，默认中文
                            )
        # 执行测试用例套件
        result = runner.run(suite)
        dir_result = dir(result.result[0]['testCase_object'])
        print(dir_result)
