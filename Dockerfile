FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./app /app

# RUN pip install --no-cache-dir akshare

RUN pip install --user -r requirements.txt