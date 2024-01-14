# 基础镜像，基于redis6.2.5版本
FROM redis:6.2.5
MAINTAINER lucasgini <dongqianglucas@gmail.com>
# 设置工作目录
WORKDIR /data
# 创建目录
RUN mkdir -p /etc/redis && touch /etc/redis/redis.conf
# 复制配置文件
COPY redis.conf /etc/redis/redis.conf
# 映射端口
EXPOSE 6379
# 启动redis服务
CMD ["redis-server", "/etc/redis/redis.conf", "--appendonly yes", "--bind 0.0.0.0", "--requirepass 123456"]
