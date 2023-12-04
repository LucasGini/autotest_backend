import json
import jsonpath
import requests
import unittest
from execute.public_test import PublicTestCase


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
            for ass, d in rule.items():
                v0, v1, v2 = None, None, None
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

    def precondition_case_execute(self, value):
        """
        前置用例执行方法
        :param value: 测试用例
        :return:
        """
        header = value.get('header', None)
        url = value.get('url', None)
        param = value.get('param', None)
        method = value.get('method', None)
        body = value.get('body', None)
        preconditions = value.get('preconditions', None)
        # 判断是否存在前置用例，如果存在前置用例，则递归执行所有前置用例，获取依赖值
        if preconditions and isinstance(preconditions, list):
            for p in preconditions:
                self.precondition_case_execute(p)
        if body:
            body = json.dumps(body)
        # 请求头、url、请求方法不为空才发起请求
        if header is None or url is None or method is None:
            raise Exception('请求头、url或者请求方法为空')
        response = requests.request(method=method, url=url, params=param, data=body, headers=header)
        data_json = response.json()
        verify = value.get('verify', None)
        # 断言规则不为空，则进行断言
        if verify:
            self.assert_verify(verify, data_json)
        fetch = value.get('fetch', None)
        # 取值规则不为空，则进行取值
        if fetch:
            self.fetch_data(fetch, data_json)

    def get_data_type(self, type, value):
        """
        将数据转换为对应类型
        :param type: 数据类型
        :param value: 需要转换的数据
        :return: 转换后的数据
        """

        if type == 'int':
            return int(value)
        if type == 'float':
            return float(value)
        if type == 'bool':
            return bool(value)
        if type == 'str':
            return str(value)
        if type == 'list':
            return list(value)
        if type == 'tuple':
            return tuple(value)
        if type == 'set':
            return set(value)
        if type == 'dict':
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


class SetattrPublicTestCase(PublicTestCase):
    """
    公共测试类
    """

    def load_test_case(self):
        """
        测试用例加载
        """
        for index, instance in enumerate(self.case_list):
            case_info = self.build_case_info(instance)

            def test_case(self, case=case_info):
                preconditions = case.get('preconditions', None)
                # 判断是否存在前置用例，如果存在前置用例，则递归执行所有前置用例，获取依赖值
                if preconditions and isinstance(preconditions, list):
                    for p in preconditions:
                        self.precondition_case_execute(p)
                body = case.get('body', None)
                if body:
                    body = json.dumps(body)
                param = case.get('param', None)
                header = case.get('header', None)
                url = case.get('url', None)
                method = case.get('method', None)
                # 请求头、url、请求方法不为空才发起请求
                if header is None or url is None or method is None:
                    raise Exception('请求头、url或者请求方法为空')
                response = requests.request(method=method, url=url, params=param, data=body, headers=header)
                data_json = response.json()
                verify = case.get('verify', None)
                # 断言规则不为空，则进行断言
                if verify:
                    self.assert_verify(verify, data_json)
                fetch = case.get('fetch', None)
                # 取值规则不为空，则进行取值
                if fetch:
                    self.fetch_data(fetch, data_json)
                print(self.var)
            # 修改方法描述文档
            test_case.__doc__ = case_info.get('name', None)
            # 使用setattr函数动态创建测试方法，并将方法名设置为即可用例的名称
            setattr(TestBase, f'test_case_{index}', test_case)

    def test_main(self):
        """
        测试主方法
        """
        self.load_test_case()
        # 创建测试套件
        # unittest.main()
        suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
        # 创建测试运行器
        runner = unittest.TextTestRunner(verbosity=2)
        # 执行测试套件
        runner.run(suite)



