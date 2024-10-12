# backend/vulnerability_report/views.py

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    Report,
    EmailSendRecord,
    Template,
    ScheduledTask,
    TaskLog,
    IntermediateData,
    EmailConfiguration
)
from .serializers import (
    ReportSerializer,
    ReportCreateUpdateSerializer,
    ReportSendSerializer,
    EmailSendRecordSerializer,
    EmailSendRecordCreateUpdateSerializer,
    TemplateSerializer,
    TemplateCreateUpdateSerializer,
    ScheduledTaskSerializer,
    ScheduledTaskCreateUpdateSerializer,
    TaskLogSerializer,
    TaskLogCreateUpdateSerializer,
    IntermediateDataSerializer,
    IntermediateDataCreateUpdateSerializer,
    EmailConfigurationSerializer,
    EmailConfigurationCreateUpdateSerializer
)
from dvadmin.utils.viewset import CustomModelViewSet
from django.core.mail import send_mail
from django.conf import settings
import json


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
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    create_serializer_class = ReportCreateUpdateSerializer
    update_serializer_class = ReportCreateUpdateSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'type', 'summary', 'content']
    ordering_fields = ['report_date', 'create_datetime', 'update_datetime']

    @action(detail=True, methods=['post'], serializer_class=ReportSendSerializer, url_path='send')
    def send_email(self, request, pk=None):
        """
        发送简报邮件
        """
        report = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipients = serializer.validated_data.get('recipients', [])

        if not recipients:
            return Response({"detail": "接收者列表不能为空。"}, status=status.HTTP_400_BAD_REQUEST)

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
                html_message=report.content  # 如果 content 是 HTML，可以使用 html_message
            )
            status_send = '成功'
        except Exception as e:
            status_send = '失败'

        # 记录邮件发送记录
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

    @action(detail=True, methods=['get'], url_path='email-history')
    def email_history(self, request, pk=None):
        """
        获取简报的邮件发送历史
        """
        report = self.get_object()
        email_records = report.email_send_records.all().order_by('-sent_at')
        serializer = EmailSendRecordSerializer(email_records, many=True)
        return Response({
            "report_id": report.id,
            "email_history": serializer.data
        }, status=status.HTTP_200_OK)


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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['report__title', 'recipients', 'status']
    ordering_fields = ['sent_at', 'create_datetime', 'update_datetime']


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
    """
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    create_serializer_class = TemplateCreateUpdateSerializer
    update_serializer_class = TemplateCreateUpdateSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['template_name', 'template_type', 'content']
    ordering_fields = ['id', 'create_datetime', 'update_datetime']


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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'frequency', 'status']
    ordering_fields = ['id', 'create_datetime', 'update_datetime']

    @action(detail=True, methods=['patch'], url_path='pause')
    def pause_task(self, request, pk=None):
        """
        暂停定时任务
        """
        task = self.get_object()
        if task.status == '暂停':
            return Response({"detail": "任务已处于暂停状态。"}, status=status.HTTP_400_BAD_REQUEST)
        task.status = '暂停'
        task.save()
        return Response({"detail": "任务已暂停。"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='resume')
    def resume_task(self, request, pk=None):
        """
        恢复定时任务
        """
        task = self.get_object()
        if task.status == '运行中':
            return Response({"detail": "任务已处于运行中状态。"}, status=status.HTTP_400_BAD_REQUEST)
        task.status = '运行中'
        task.save()
        return Response({"detail": "任务已恢复运行。"}, status=status.HTTP_200_OK)


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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['job_id', 'task_name', 'result']
    ordering_fields = ['start_time', 'create_datetime', 'update_datetime']


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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
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
    """
    queryset = EmailConfiguration.objects.all()
    serializer_class = EmailConfigurationSerializer
    create_serializer_class = EmailConfigurationCreateUpdateSerializer
    update_serializer_class = EmailConfigurationCreateUpdateSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['report_type', 'recipients']
    ordering_fields = ['create_datetime', 'update_datetime']