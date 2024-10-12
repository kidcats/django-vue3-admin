# backend/vulnerability_report/serializers.py

from rest_framework import serializers
from .models import (
    Report,
    EmailSendRecord,
    Template,
    ScheduledTask,
    TaskLog,
    IntermediateData,
    EmailConfiguration
)
from dvadmin.utils.serializers import CustomModelSerializer


# ===========================
# 简报管理模块序列化器
# ===========================

class ReportSerializer(CustomModelSerializer):
    """
    简报序列化器
    """
    creator = serializers.StringRelatedField()

    class Meta:
        model = Report
        fields = '__all__'


class ReportCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新简报时的序列化器
    """

    class Meta:
        model = Report
        fields = '__all__'


class ReportSendSerializer(serializers.Serializer):
    """
    发送简报时使用的序列化器
    """
    recipients = serializers.ListField(
        child=serializers.EmailField(),
        help_text="邮件接收人列表，多个邮箱使用数组格式提供"
    )


# ===========================
# 邮件发送记录模块序列化器
# ===========================

class EmailSendRecordSerializer(CustomModelSerializer):
    """
    邮件发送记录序列化器
    """
    report = serializers.StringRelatedField()

    class Meta:
        model = EmailSendRecord
        fields = '__all__'


class EmailSendRecordCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新邮件发送记录时的序列化器
    """

    class Meta:
        model = EmailSendRecord
        fields = '__all__'


# ===========================
# 模板管理模块序列化器
# ===========================

class TemplateSerializer(CustomModelSerializer):
    """
    模板序列化器
    """
    creator = serializers.StringRelatedField()

    class Meta:
        model = Template
        fields = '__all__'


class TemplateCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新模板时的序列化器
    """

    class Meta:
        model = Template
        fields = '__all__'


# ===========================
# 任务管理模块序列化器
# ===========================

class ScheduledTaskSerializer(CustomModelSerializer):
    """
    定时任务序列化器
    """
    template = serializers.StringRelatedField()
    creator = serializers.StringRelatedField()

    class Meta:
        model = ScheduledTask
        fields = '__all__'


class ScheduledTaskCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新定时任务时的序列化器
    """

    class Meta:
        model = ScheduledTask
        fields = '__all__'


# ===========================
# 任务日志模块序列化器
# ===========================

class TaskLogSerializer(CustomModelSerializer):
    """
    任务日志序列化器
    """

    class Meta:
        model = TaskLog
        fields = '__all__'


class TaskLogCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新任务日志时的序列化器
    """

    class Meta:
        model = TaskLog
        fields = '__all__'


# ===========================
# 中间数据模块序列化器
# ===========================

class IntermediateDataSerializer(CustomModelSerializer):
    """
    中间数据序列化器
    """
    job = serializers.StringRelatedField()

    class Meta:
        model = IntermediateData
        fields = '__all__'


class IntermediateDataCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新中间数据时的序列化器
    """

    class Meta:
        model = IntermediateData
        fields = '__all__'


# ===========================
# 系统管理模块-邮件管理子模块序列化器
# ===========================

class EmailConfigurationSerializer(CustomModelSerializer):
    """
    邮件配置序列化器
    """
    creator = serializers.StringRelatedField()

    class Meta:
        model = EmailConfiguration
        fields = '__all__'


class EmailConfigurationCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新邮件配置时的序列化器
    """

    class Meta:
        model = EmailConfiguration
        fields = '__all__'