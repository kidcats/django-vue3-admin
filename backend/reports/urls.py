# reports/urls.py

from rest_framework.routers import SimpleRouter
from django.urls import path, include

from .views import (
    EmailConfigurationViewSet,
    ReportViewSet,
    EmailSendRecordViewSet,
    TemplateViewSet,
    ScheduledTaskViewSet,
    TaskLogViewSet,
    IntermediateDataViewSet,
    ReportTypeViewSet,  # 新增
    ReportGroupViewSet,  # 新增
    FrequencyViewSet,  # 新增
)

router = SimpleRouter()

# 注册各个视图集，并将API路径以视图名称为后缀
router.register(r'api/reports', ReportViewSet, basename='report')
router.register(r'api/email-send-records', EmailSendRecordViewSet, basename='emailsendrecord')
router.register(r'api/templates', TemplateViewSet, basename='template')
router.register(r'api/scheduled-tasks', ScheduledTaskViewSet, basename='scheduledtask')
router.register(r'api/task-logs', TaskLogViewSet, basename='tasklog')
router.register(r'api/intermediate-data', IntermediateDataViewSet, basename='intermediatedata')
router.register(r'api/email-configurations', EmailConfigurationViewSet, basename='emailconfiguration')
router.register(r'api/report-type', ReportTypeViewSet, basename='reportype')  # 新增
router.register(r'api/report-group', ReportGroupViewSet, basename='reportgroup')  # 新增
router.register(r'api/frequency', FrequencyViewSet, basename='frequency')  # 新增

urlpatterns = [
    path('', include(router.urls)),
]