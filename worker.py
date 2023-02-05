from celery import Celery
from sisly import Sisly
import os

app = Celery('sisly', broker=os.environ.get("rabbitmq_uri"))

@app.task
def spawn_sisly(url):
    sisly = Sisly(url)
    sisly.run()