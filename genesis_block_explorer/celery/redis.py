import redis
from urllib.parse import urlparse

from celery.task.base import periodic_task

from . import celery, application
 
def ping_redis():
    redis_url = urlparse(application.config.get('REDIS_URL'))
    r = redis.StrictRedis(host=redis_url.hostname, port=redis_url.port, db=1, password=redis_url.password)
     
    try: 
        r.ping()
        print("Redis is connected!")
    except redis.ConnectionError:
        print("Redis connection error!")

if __name__ == '__main__':
    ping_redis()
