import os

BROKER_URL = 'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'.format(
    REDIS_HOST=os.environ.get('REDIS_HOST', ''),
    REDIS_PORT=os.environ.get('REDIS_PORT', 6379),
    REDIS_PASSWORD=os.environ.get('REDIS_PASSWORD', ''),
    REDIS_DB=os.environ.get('REDIS_DB', 1)
)
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYD_CONCURRENCY = 1
