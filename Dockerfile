# 基础镜像，基于Python3.10.13
FROM python:3.10.13
# 维护者信息
MAINTAINER lucasGini <dongqianglucas@gmail.com>
# 创建目录
RUN mkdir -p /home/lidongqiang/autotest_backend
# 切换到工作目录
WORKDIR /home/lidongqiang/autotest_backend
# 复制项目到容器中
ADD . /home/lidongqiang/autotest_backend
# 安装依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 映射端口
EXPOSE 8000
