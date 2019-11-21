from celery import Celery

app = Celery(__name__, include=['celery_tasks.tasks'])
app.config_from_object('celery_tasks.config')

# celery -A celery_tasks worker -P eventlet -l info -f celery_tasks/celery.log
