import string
import threading
import unittest
from apps.cases.models import Precondition
from common.const.basic_const import AGREEMENT_CONST
from common.const.case_const import METHOD_CONST


class PublicTestCase:
    """
    公共测试类
    """

    case = '''
    def test_${index}(self):
        value=${case_info}
        header = value.get('header', None)
        url = value.get('url', None)
        param = value.get('param', None)
        method = value.get('method', None)
        body = value.get('body', None)
        if body:
            body = json.dumps(body)
        verify = value.get('verify', None)
        fetch = value.get('fetch', None)
        # 请求头、url、请求方法不为空才发起请求
        if header and url and method:
            raise Exception('请求头、url或者请求方法为空')
        response = requests.request(method=method, url=url, params=param, data=body, headers=header)
        data_json = response.json()
        # 断言规则不为空，则进行断言
        if verify: 
            if isinstance(verify, list) is False:
                raise Exception('断言规则不为list类型')
            # 遍历所有断言规则
            for ver in verify:
                if isinstance(ver, dict) is False:
                    raise Exception('断言子规则不为dict类型')
                for ass, d in ver.items():
                    v0, v1, v2 = None, None, None
                    if isinstance(d, dict) is false:
                        raise Exception('断言规则定义不为dict类型')
                    path = d.get('path', None)
                    types = d.get('types', None)
                    value = d.get('value', None)
                    if path is not None:
                        v0 = jsonpath.jsonpath(data_json, path)
                    if types is not None and value is not None:
                        v1 = self.get_data_type(types, value)
                    v2 = d.get('msg', None)
                self.get_assert(ass, v0, v1, v2)
        # 取值规则不为空，则进行取值
        if fetch: 
            if isinstance(verify, list) is False:
                raise Exception('取值规则不为list类型')
'''

    code = '''
import jsonpath
import requests
import aiohttp
import unittest
from apps.cases.models import Precondition


class BaseTest${thread_id}(unittest.TestCase):
    """
    测试基类
    """

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

    def SetUp(self):
        pass

    def TearDown(self):
        pass

    ${test_case}
'''

    def __init__(self, case_list, test_env):
        self.case_list = case_list
        self.test_env = test_env

    def build_case_info(self, instance):
        """
        构建用例信息
        :param instance: case实例
        :return: case_info
        """
        case_info = {}
        try:
            precondition_obj = Precondition.objects.get(case=instance.id, enable_flag=1)
            precondition = precondition_obj.precondition_case
        except Precondition.DoesNotExist:
            precondition = None
        case_info['precondition'] = precondition
        case_info['method'] = METHOD_CONST[instance.method]
        case_info['url'] = self.build_test_url(instance)
        data = eval(instance.data)
        if isinstance(data, dict):
            case_info['header'] = data.get('header', None)
            case_info['param'] = data.get('param', None)
            case_info['body'] = data.get('body', None)
            case_info['verify'] = data.get('verify', None)
            case_info['fetch'] = data.get('fetch', None)
        else:
            raise Exception('用例数据格式不正确')
        return case_info

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

    @staticmethod
    def str_template(body: str, var: dict) -> any:
        """
        字符串模板插入并返回相应对象
        param: body 字符串
        param: var 插入值（字典，key需要与body中标记的key一致）
        """
        # 初始化
        false, true, null = False, True, ''
        # 字符串模板插入
        data = string.Template(body).safe_substitute(var)
        return data

    def test_case(self):
        """
        测试用例拼接
        """
        params = """"""
        for index, instance in enumerate(self.case_list):
            case_info = self.build_case_info(instance)
            dict_data = {'index': index, 'case_info': case_info}
            param = self.str_template(self.case, dict_data)
            params += param
        return params

    def test_class(self):
        """
        测试类拼接
        """
        test_case = {
            'test_case': self.test_case(),
            'thread_id': threading.get_ident()
        }
        # thread_id避免类冲突
        return self.str_template(self.code, test_case)

    def test_main(self):
        """
        测试主方法
        """
        import threading
        import gc
        test_class = self.test_class()
        # 将动态代码加载到内存
        exec(test_class)
        print("Thread ID:", threading.get_ident())
        class_name = 'BaseTest' + str(threading.get_ident())
        base_test = unittest.TestCase
        # 从内存中获取测试类对象
        for obj in gc.get_objects():
            if isinstance(obj, type):
                if obj.__name__ == class_name:
                    base_test = obj
                    break
        # 创建测试套件
        # unittest.main()
        print(base_test)
        if base_test:
            suite = unittest.TestLoader().loadTestsFromTestCase(base_test)
            # 创建测试运行器
            runner = unittest.TextTestRunner(verbosity=2)
            # 执行测试套件
            runner.run(suite)


if __name__ == '__main__':
    from apps.cases.models import TestCase
    from apps.basics.models import TestEnv

    env = TestEnv.objects.get(id=1, enable_flag=1)
    queryset = TestCase.objects.all().filter(enable_flag=1)
    datas = []
    for i in queryset:
        datas.append(i)
    PublicTestCase(datas, env).test_main()
