FROM python:3.9-slim-buster

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir Flask==2.0.2

CMD ["python", "main.py"]