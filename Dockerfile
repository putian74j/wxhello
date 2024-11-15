FROM tiangolo/uwsgi-nginx-flask:python3.8

# COPY ./app /app

# WORKDIR /app
# # RUN pip install --no-cache-dir akshare

# RUN pip install -r requirements.txt



COPY . /app

# 设定当前的工作目录
WORKDIR /app

# 安装依赖到指定的/install文件夹
# 选用国内镜像源以提高下载速度
RUN pip install --user -r requirements.txt

