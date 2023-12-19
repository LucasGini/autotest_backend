from obsolete.public_test import PublicTestCase


class AsyncPublicTestCase(PublicTestCase):
    """
    公共测试类
    """

    case = '''
    async def test_${index}(self):
        value=${case_info}
        header = value.get('header', None)
        url = value.get('url', None)
        param = value.get('param', None)
        method = value.get('method', None)
        body = value.get('body', None)
        verify = value.get('verify', None)
        fetch = value.get('fetch', None)
        if header and url:
            response = await self.session.request(method=method, url=url, params=param, data=body, headers=header)
            data_json = await response.json()
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
                                        v1 =  await self.get_data_type(types, value)
                                    v2 = d.get('msg', None)
                                await self.get_assert(ass, v0, v1, v2)
                        else:
                            raise Exception('断言规则格式不正确')
'''

    code = '''
import jsonpath
import requests
import aiohttp
import unittest
from apps.cases.models import Precondition


class BaseTest${thread_id}(unittest.IsolatedAsyncioTestCase):
    """
    测试基类
    """

    async def get_data_type(self, type, value):
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

    async def get_assert(self, ass, *args):
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

    async def asyncSetUp(self):
        self.session = aiohttp.ClientSession()

    async def asyncTearDown(self):
        await self.session.close()

    ${test_case}
'''
