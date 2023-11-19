import unittest

from execute.base_test import BaseTest

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


if __name__ == '__main__':
    datas = [datas1, datas2]
    bt = BaseTest
    bt.datas = datas
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(bt)

    # 创建测试运行器
    runner = unittest.TextTestRunner()

    # 执行测试套件
    runner.run(suite)
