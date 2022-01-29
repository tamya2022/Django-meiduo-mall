# 1.导包
from celery import Celery

# 可能需要加载django项目的包
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

# 2. 实例化
app = Celery('celery_tasks')
# 3.加载配置文件
app.config_from_object('celery_tasks.config')

# 4. 自动加载任务
app.autodiscover_tasks(['celery_tasks.sms'])

# celery -A celery_tasks.main worker -l info -P eventlet
