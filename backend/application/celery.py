import functools
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')

from django.conf import settings
from celery import platforms

# 租户模式
if "django_tenants" in settings.INSTALLED_APPS:
    from tenant_schemas_celery.app import CeleryApp as TenantAwareCeleryApp

    app = TenantAwareCeleryApp()
else:
    from celery import Celery

    app = Celery(f"application")
app.config_from_object('django.conf:settings')
# 添加定时任务配置
# # 终端1：启动worker
# celery -A application worker -l info

# 终端2：启动beat
# celery -A application beat -l info
# 
app.conf.beat_schedule = {
    'update-every-second': {
        'task': 'reports.tasks.update_celery_beat_schedule',  # 任务的路径
        'schedule': 1.0,  # 每1秒执行一次
    },
}
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
platforms.C_FORCE_ROOT = True
# 从所有已注册的django app中加载任务模块

app.autodiscover_tasks()



def retry_base_task_error():
    """
    celery 失败重试装饰器
    :return:
    """

    def wraps(func):
        @app.task(bind=True, retry_delay=180, max_retries=3)
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                raise self.retry(exc=exc)

        return wrapper

    return wraps
