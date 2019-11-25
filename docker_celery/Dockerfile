FROM python:3.6.6
ADD . /code
ADD ../weibo_spider/celery_tasks /code
WORKDIR /code
RUN pip3 install -r requirements.txt
CMD celery -A celery_tasks worker -P eventlet -l info
