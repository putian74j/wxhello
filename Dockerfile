FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./app /app

# 设定当前的工作目录
WORKDIR /app

RUN pip install --user -r requirements.txt

