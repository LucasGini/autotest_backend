import unittest
from execute.public_test import PublicTestCase

datas1 = {
        'header': {
            "User-Agent": "Mozilla/5.0 (Windows NT 00.0; Win64; x64) AppleWebKit/527.26 (KHTML, like Gecko) Chrome/54.0.1840.99 Safari/527.26"},
        'url': "https://api.douban.com/v2/user/:name",
        'method': 'GET',
        'verify': [{'assertEqual': {'path': '$.data', 'value': False, 'msg': '比对不正确'}},
                   {'assertEqual': {'path': '$.data', 'value': False, 'msg': '比对不正确'}}]
    }
datas2 = {
        'header': {
            "User-Agent": "Mozilla/5.0 (Windows NT 00.0; Win64; x64) AppleWebKit/527.26 (KHTML, like Gecko) Chrome/54.0.1840.99 Safari/527.26"},
        'url': "https://api.douban.com/v2/user/:name",
        'method': 'GET',
        'verify': [{'assertEqual': {'path': '$.data', 'value': False, 'msg': '比对不正确'}},
                   {'assertEqual': {'path': '$.data', 'value': 'False', 'msg': '比对不正确'}}]
    }


if __name__ == '__main__':
    import threading
    import gc
    datas = [datas1, datas2]
    bt = PublicTestCase(datas)
    exec(bt.test_main())
    BaseTest = type
    print("Thread ID:", threading.get_ident())
    class_name = 'BaseTest' + str(threading.get_ident())

    # 收集当前内存中的类对象
    classes = []
    for obj in gc.get_objects():
        if isinstance(obj, type):
            classes.append(obj)

    # 判断内存所有类，取出对应的测试类
    for cls in classes:
        print(cls)
        if cls.__name__ == class_name:
            BaseTest = cls
    # 创建测试套件
    # unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(BaseTest)

    # 创建测试运行器
    runner = unittest.TextTestRunner()

    # 执行测试套件
    runner.run(suite)
