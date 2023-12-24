import gevent
from gevent import monkey
monkey.patch_all()
import multiprocessing

preload_app = True                   # 通过预加载应用程序，可以加快服务器的启动速度
workers = 3                          # 并行工作进程数，推荐数量为”（当前的cpu个数*2）+ 1“
threads = 4                          # 每个工作者的线程数
bind = '0.0.0.0:8000'                # 监听IP地址和端口
daemon = False                       # 应用是否以daemon方式运行，默认False
worker_class = 'gevent'              # 工作模式协程，worker进程的工作方式，有sync、eventlet、gevent、tornado、gthread，默认为sync
worker_connections = 2000            # 设置最大并发量
proc_name = 'test'                   # 设置进程名
pidfile = '/Users/lidongqiang/DjangoProjects/autotest_backend/gunicorn.pid'   # 设置进程文件路径
accesslog = "/Users/lidongqiang/DjangoProjects/autotest_backend/access.log"   # 设置访问日志路径
errorlog = "/Users/lidongqiang/DjangoProjects/autotest_backend/error.log"     # 设置错误信息日志路径
loglevel = "debug"                   # 错误日志输出等级，分为debug、info、warning、error和critical
