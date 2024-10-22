# backend/vulnerability_report/views.py

from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from dvadmin.utils.filters import DataLevelPermissionsFilter
from reports.filter import ReportsCoreModelFilterBankend
from dvadmin.utils.json_response import DetailResponse, ErrorResponse, SuccessResponse
from .models import (
    Report, EmailSendRecord, Template, ScheduledTask, TaskLog,
    IntermediateData, EmailConfiguration, ReportType, ReportGroup, Frequency
)
from .serializers import (
    ReportSerializer, ReportCreateUpdateSerializer, ReportSendSerializer,
    EmailSendRecordSerializer, EmailSendRecordCreateUpdateSerializer,
    TemplateSerializer, TemplateCreateUpdateSerializer,
    ScheduledTaskSerializer, ScheduledTaskCreateUpdateSerializer,
    TaskLogSerializer, TaskLogCreateUpdateSerializer,
    IntermediateDataSerializer, IntermediateDataCreateUpdateSerializer,
    EmailConfigurationSerializer, EmailConfigurationCreateUpdateSerializer,
    ReportTypeSerializer, ReportTypeCreateUpdateSerializer,
    ReportGroupSerializer, ReportGroupCreateUpdateSerializer,
    FrequencySerializer, FrequencyCreateUpdateSerializer
)
from dvadmin.utils.viewset import CustomModelViewSet
from django.core.mail import send_mail
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)
# ===========================
# 报告类型模块视图集
# ===========================

class ReportTypeViewSet(CustomModelViewSet):
    """
    list: 查询报告类型
    create: 新增报告类型
    update: 修改报告类型
    retrieve: 获取单个报告类型
    destroy: 删除报告类型
    """
    queryset = ReportType.objects.all()
    serializer_class = ReportTypeSerializer
    create_serializer_class = ReportTypeCreateUpdateSerializer
    update_serializer_class = ReportTypeCreateUpdateSerializer
    search_fields = ['name']
    ordering_fields = ['id', 'create_datetime', 'update_datetime']

# ===========================
# 报告分组模块视图集
# ===========================

class ReportGroupViewSet(CustomModelViewSet):
    """
    list: 查询报告分组
    create: 新增报告分组
    update: 修改报告分组
    retrieve: 获取单个报告分组
    destroy: 删除报告分组
    """
    queryset = ReportGroup.objects.all()
    serializer_class = ReportGroupSerializer
    create_serializer_class = ReportGroupCreateUpdateSerializer
    update_serializer_class = ReportGroupCreateUpdateSerializer
    search_fields = ['name']
    ordering_fields = ['id', 'create_datetime', 'update_datetime']

# ===========================
# 频率选项模块视图集
# ===========================

class FrequencyViewSet(CustomModelViewSet):
    """
    list: 查询频率选项
    create: 新增频率选项
    update: 修改频率选项
    retrieve: 获取单个频率选项
    destroy: 删除频率选项
    """
    queryset = Frequency.objects.all()
    serializer_class = FrequencySerializer
    create_serializer_class = FrequencyCreateUpdateSerializer
    update_serializer_class = FrequencyCreateUpdateSerializer
    search_fields = ['name']
    ordering_fields = ['id', 'create_datetime', 'update_datetime']

# ===========================
# 简报管理模块视图集
# ===========================

class ReportViewSet(CustomModelViewSet):
    """
    list: 查询简报
    create: 新增简报
    update: 修改简报
    retrieve: 获取单个简报
    destroy: 删除简报
    send: 发送简报邮件
    email_history: 获取简报的邮件发送历史
    report_types: 获取简报的所有类型
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    search_fields = ['title', 'type__name', 'group__name', 'summary', 'content', 'create_datetime']
    extra_filter_class = [ReportsCoreModelFilterBankend, DataLevelPermissionsFilter]
    ordering_fields = ['report_date', 'create_datetime', 'update_datetime']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReportCreateUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'], serializer_class=ReportSendSerializer)
    def send(self, request, pk=None):
        """
        发送简报邮件
        """
        report = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipients = serializer.validated_data.get('recipients', [])

        if not recipients:
            return ErrorResponse(msg="收件人列表不能为空")

        subject = report.title
        message = report.content
        from_email = settings.DEFAULT_FROM_EMAIL

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipients,
                fail_silently=False,
                html_message=report.content
            )
            status_send = '成功'
        except Exception as e:
            status_send = '失败'

        email_record = EmailSendRecord.objects.create(
            report=report,
            recipients=';'.join(recipients),
            status=status_send
        )

        return Response({
            "report_id": report.id,
            "sent_at": email_record.create_datetime,
            "recipients": recipients,
            "status": status_send
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def email_history(self, request, pk=None):
        """
        获取简报的邮件发送历史
        """
        report = self.get_object()
        email_records = report.email_send_records.all().order_by('-create_datetime')
        serializer = EmailSendRecordSerializer(email_records, many=True)
        return SuccessResponse(data=serializer.data, msg="成功获取简报邮件发送历史")


# ===========================
# 邮件发送记录模块视图集
# ===========================

class EmailSendRecordViewSet(CustomModelViewSet):
    """
    list: 查询邮件发送记录
    create: 新增邮件发送记录
    update: 修改邮件发送记录
    retrieve: 获取单个邮件发送记录
    destroy: 删除邮件发送记录
    """
    queryset = EmailSendRecord.objects.all()
    serializer_class = EmailSendRecordSerializer
    create_serializer_class = EmailSendRecordCreateUpdateSerializer
    update_serializer_class = EmailSendRecordCreateUpdateSerializer
    search_fields = ['report__title', 'recipients', 'status']
    ordering_fields = ['sent_at', 'create_datetime', 'update_datetime']
    
    
    @action(detail=False, methods=['get'])
    def report_history(self, request):
        """
        获取特定报告的邮件发送历史
        """
        report = request.query_params.get('id')
        if not report:
            return ErrorResponse(data=None, msg="报告ID是必需的")

        queryset = self.queryset.filter(report=report)
        # queryset = self.filter_queryset(queryset)
        
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="返回报告的邮件发送历史")

# ===========================
# 模板管理模块视图集
# ===========================

class TemplateViewSet(CustomModelViewSet):
    """
    list: 查询模板
    create: 新增模板
    update: 修改模板
    retrieve: 获取单个模板
    destroy: 删除模板
    template_group_type: 获取模板的所有分组类型
    """
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    create_serializer_class = TemplateCreateUpdateSerializer
    update_serializer_class = TemplateCreateUpdateSerializer
    search_fields = ['template_name', 'template_type', 'content', 'template_group']
    ordering_fields = ['id', 'create_datetime', 'update_datetime']
    
    def create(self, request, *args, **kwargs):
        logger.info(f"Create method - Request data: {request.data}")
        form_data = request.data.get('form', {})
        serializer = self.get_serializer(data=form_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return SuccessResponse(serializer.data,headers=headers)
    
    @action(detail=False, methods=['get'])
    def template_group_type(self, request):
        """
        获取模板的所有分组类型
        """
        field = Template._meta.get_field('template_group')
        choices = field.choices
        types = [{'value': choice[0], 'label': choice[1]} for choice in choices]
        return DetailResponse(data=types, msg="返回模板所有分组类型")

# ===========================
# 任务管理模块视图集
# ===========================

class ScheduledTaskViewSet(CustomModelViewSet):
    """
    list: 查询定时任务
    create: 新增定时任务
    update: 修改定时任务
    retrieve: 获取单个定时任务
    destroy: 删除定时任务
    pause: 暂停定时任务
    resume: 恢复定时任务
    """
    queryset = ScheduledTask.objects.all()
    serializer_class = ScheduledTaskSerializer
    create_serializer_class = ScheduledTaskCreateUpdateSerializer
    update_serializer_class = ScheduledTaskCreateUpdateSerializer
    search_fields = ['name', 'cron_expression', 'status']
    ordering_fields = ['id', 'create_datetime', 'update_datetime']
    
    def create(self, request, *args, **kwargs):
        logger.info(f"Create method - Request data: {request.data}")
        form_data = request.data.get('form', {})
        serializer = self.get_serializer(data=form_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return SuccessResponse(serializer.data,headers=headers)

    @action(detail=True, methods=['patch'])
    def pause(self, request, pk=None):
        """
        暂停定时任务
        """
        task = self.get_object()
        if not task.is_active:
            return ErrorResponse({"detail": "任务已处于暂停状态。"})
        task.is_active  =  False
        task.save()
        return SuccessResponse({"detail": "任务已暂停。"})

    @action(detail=True, methods=['patch'])
    def resume(self, request, pk=None):
        """
        恢复定时任务
        """
        task = self.get_object()
        if task.is_active:
            return ErrorResponse({"detail": "任务已处于运行中状态。"})
        task.is_active = True
        task.save()
        return SuccessResponse({"detail": "任务已恢复运行。"})

# ===========================
# 任务日志模块视图集
# ===========================

class TaskLogViewSet(CustomModelViewSet):
    """
    list: 查询任务日志
    create: 新增任务日志
    update: 修改任务日志
    retrieve: 获取单个任务日志
    destroy: 删除任务日志
    """
    queryset = TaskLog.objects.all()
    serializer_class = TaskLogSerializer
    create_serializer_class = TaskLogCreateUpdateSerializer
    update_serializer_class = TaskLogCreateUpdateSerializer
    search_fields = ['job_id', 'task_name', 'result']
    ordering_fields = ['start_time', 'create_datetime', 'update_datetime']
    
    @action(detail=True, methods=['patch'])
    def pause(self, request, pk=None):
        """
        暂停定时任务
        """
        tasklog = self.get_object()
        if tasklog.result == '暂停':
            return ErrorResponse({"detail": "任务已处于暂停状态。"})
        tasklog.status = '暂停'
        tasklog.save()
        return SuccessResponse({"detail": "任务已暂停。"})

    @action(detail=True, methods=['patch'])
    def resume(self, request, pk=None):
        """
        恢复定时任务
        """
        tasklog = self.get_object()
        if tasklog.result == '运行中':
            return ErrorResponse({"detail": "任务已处于运行中状态。"})
        tasklog.result = '运行中'
        tasklog.save()
        return SuccessResponse({"detail": "任务已恢复运行。"})

# ===========================
# 中间数据模块视图集
# ===========================

class IntermediateDataViewSet(CustomModelViewSet):
    """
    list: 查询中间数据
    create: 新增中间数据
    update: 修改中间数据
    retrieve: 获取单个中间数据
    destroy: 删除中间数据
    """
    queryset = IntermediateData.objects.all()
    serializer_class = IntermediateDataSerializer
    create_serializer_class = IntermediateDataCreateUpdateSerializer
    update_serializer_class = IntermediateDataCreateUpdateSerializer
    search_fields = ['date', 'job__name']
    ordering_fields = ['date', 'create_datetime', 'update_datetime']

# ===========================
# 系统管理模块-邮件管理子模块视图集
# ===========================

class EmailConfigurationViewSet(CustomModelViewSet):
    """
    list: 查询邮件配置
    create: 新增邮件配置
    update: 修改邮件配置
    retrieve: 获取单个邮件配置
    destroy: 删除邮件配置
    status: 修改邮件配置状态
    """
    queryset = EmailConfiguration.objects.all()
    serializer_class = EmailConfigurationSerializer
    create_serializer_class = EmailConfigurationCreateUpdateSerializer
    update_serializer_class = EmailConfigurationCreateUpdateSerializer
    search_fields = ['report_type__name', 'recipients']
    ordering_fields = ['create_datetime', 'update_datetime']
    
    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        email_config = self.get_object()
        email_config.status = request.data.get('status', email_config.status)
        email_config.save()
        return SuccessResponse(data={'status': email_config.status}, msg="成功修改配置的状态")