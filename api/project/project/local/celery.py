
import os
from celery import Celery


configurationKey = os.environ.get('GENIE_CONFIGURATION_KEY')
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'project.' + configurationKey + '.settings')


app = Celery('project')
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Kolkata')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request:{self.request!r}")
