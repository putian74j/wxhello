FROM python:3.9-slim-buster

WORKDIR /app

COPY . /app

RUN pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple

RUN pip install --no-cache-dir Flask==2.0.2

#CMD ["python", "main.py"]