from celery import Celery

from .config import CeleryConfig

app = Celery('toutiao')
app.config_from_object(CeleryConfig)
app.config_from_envvar('TOUTIAO_CELERY_SETTINGS', silent=True)

app.autodiscover_tasks(['celery_tasks.sms'])