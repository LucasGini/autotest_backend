import unittest
import jsonpath
import requests
from ddt import ddt, data, unpack

datas1 = {
    'header': {"User-Agent": "Mozilla/5.0 (Windows NT 00.0; Win64; x64) AppleWebKit/527.26 (KHTML, like Gecko) Chrome/54.0.1840.99 Safari/527.26"},
    'url': "https://api.douban.com/v2/user/:name",
    'method': 'GET',
    'verify': [{'assertEqual': {'path': '$.data', 'value': False, 'msg': '请求异常'}}]
}
datas2 = {
    'header': {"User-Agent": "Mozilla/5.0 (Windows NT 00.0; Win64; x64) AppleWebKit/527.26 (KHTML, like Gecko) Chrome/54.0.1840.99 Safari/527.26"},
    'url': "https://api.douban.com/v2/user/:name",
    'method': 'GET',
    'verify': [{'assertEqual': {'path': '$.data', 'value': 'False', 'msg': '请求异常'}}]
}


@ddt
class BaseTest(unittest.TestCase):
    """
    测试基类
    """

    def get_assert(self, ass, *args):
        """
        获取断言方法
        :param ass:  断言类型
        :return:
        """
        if ass == 'assertEqual':
            self.assertEqual(args[0], args[1], args[2])
        if ass == 'assertNotEqual':
            self.assertNotEqual(args[0], args[1], args[2])
        if ass == 'assertTrue':
            return self.assertTrue(args[0], args[1])
        if ass == 'assertFalse':
            return self.assertFalse(args[0], args[1])
        if ass == 'assertIs':
            return self.assertIs(args[0], args[1], args[2])
        if ass == 'assertIsNot':
            return self.assertIsNot(args[0], args[1], args[2])
        if ass == 'assertIsNone':
            return self.assertIsNone(args[0], args[1])
        if ass == 'assertIsNotNone':
            return self.assertIsNotNone(args[0], args[1])
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

    def setUp(self):
        pass

    @data([datas1, datas2])
    def test_base(self, values):
        for value in values:
            header = value.get('header', None)
            url = value.get('url', None)
            param = value.get('param', None)
            method = value.get('method', None)
            verify = value.get('verify', None)
            if header and url:
                response = requests.request(method=method, url=url, params=param, headers=header)
                data_json = response.json()
                print(data_json)
                if verify:
                    if isinstance(verify, list):
                        for ver in verify:
                            if isinstance(ver, dict):
                                for ass, d in ver.items():
                                    v0, v1, v2 = None, None, None
                                    if isinstance(d, dict):
                                        path = d.get('path', None)
                                        v0 = jsonpath.jsonpath(data_json, path)
                                        v1 = d.get('value', None)
                                        v2 = d.get('msg', None)
                                    self.get_assert(ass, v0, v1, v2)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
