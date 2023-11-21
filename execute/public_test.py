import string
import threading
import unittest
import requests
import jsonpath


class PublicTestCase:
    """
    公共测试类
    """

    case = '''
    def test_${index}(self):
        value=${data}
        header = value.get('header', None)
        url = value.get('url', None)
        param = value.get('param', None)
        method = value.get('method', None)
        verify = value.get('verify', None)
        if header and url:
            response = requests.request(method=method, url=url, params=param, headers=header)
            data_json = response.json()
            if verify:
                if isinstance(verify, list):
                    for ver in verify:
                        if isinstance(ver, dict) and len(ver) == 1:
                            for ass, d in ver.items():
                                v0, v1, v2 = None, None, None
                                if isinstance(d, dict):
                                    path = d.get('path', None)
                                    types = d.get('types', None)
                                    value = d.get('value', None)
                                    if path is not None:
                                        v0 = jsonpath.jsonpath(data_json, path)
                                    else:
                                        raise Exception('断言规则不正确')
                                    if types is not None and value is not None:
                                        v1 =  self.get_data_type(types, value)
                                    v2 = d.get('msg', None)
                                self.get_assert(ass, v0, v1, v2)
                        else:
                            raise Exception('断言规则格式不正确')
'''

    code = '''
import jsonpath
import requests

    
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

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    ${test_case}
'''

    def __init__(self, case_list):
        self.case_list = case_list

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
        for index, data in enumerate(self.case_list):
            dict_data = {'index': index, 'data': data}
            param = self.str_template(self.case, dict_data)
            params += param
        return params

    def test_class(self):
        """
        测试类拼接
        """
        test_case = {'test_case': self.test_case(), 'thread_id': threading.get_ident()}
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
            runner = unittest.TextTestRunner()
            # 执行测试套件
            runner.run(suite)


if __name__ == '__main__':
    datas1 = {
        'header': {
            "User-Agent": "Mozilla/5.0 (Windows NT 00.0; Win64; x64) AppleWebKit/527.26 (KHTML, like Gecko) Chrome/54.0.1840.99 Safari/527.26"},
        'url': "https://api.douban.com/v2/user/:name",
        'method': 'GET',
        'verify': [{'assertEqual': {'path': '$.data', 'types': 'bool', 'value': False, 'msg': '比对不正确'}},
                   {'assertEqual': {'path': '$.data', 'types': 'bool', 'value': False, 'msg': '比对不正确'}}]
    }
    datas2 = {
        'header': {
            "User-Agent": "Mozilla/5.0 (Windows NT 00.0; Win64; x64) AppleWebKit/527.26 (KHTML, like Gecko) Chrome/54.0.1840.99 Safari/527.26"},
        'url': "https://api.douban.com/v2/user/:name",
        'method': 'GET',
        'verify': [{'assertEqual': {'path': '$.data', 'types': 'bool', 'value': False, 'msg': '比对不正确'}},
                   {'assertEqual': {'path': '$.data', 'types': 'bool', 'value': 'False', 'msg': '比对不正确'}}]
    }
    datas = [datas1, datas2]
    PublicTestCase(datas).test_main()
