FROM tiangolo/uwsgi-nginx-flask:python3.8

# 使用 HTTPS 协议访问容器云调用证书安装
RUN apk add ca-certificates

# 安装依赖包，如需其他依赖包，请到alpine依赖包管理(https://pkgs.alpinelinux.org/packages?name=php8*imagick*&branch=v3.13)查找。
# 选用国内镜像源以提高下载速度
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tencent.com/g' /etc/apk/repositories \
    # 安装python3
    && apk add --update --no-cache python3 py3-pip \
    && rm -rf /var/cache/apk/*

COPY ./app /app

# 设定当前的工作目录
WORKDIR /app

# 安装依赖到指定的/install文件夹
# 选用国内镜像源以提高下载速度
RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple \
    && pip config set global.trusted-host mirrors.cloud.tencent.com \
    && pip install --upgrade pip \
    # pip install scipy 等数学包失败，可使用 apk add py3-scipy 进行， 参考安装 https://pkgs.alpinelinux.org/packages?name=py3-scipy&branch=v3.13
    && pip install --user -r requirements.txt

