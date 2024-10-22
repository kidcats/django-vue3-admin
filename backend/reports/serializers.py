from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import (
    Report, EmailSendRecord, Template, ScheduledTask, TaskLog, 
    IntermediateData, EmailConfiguration, ReportType, ReportGroup, Frequency
)

# ===========================
# 报告类型模块序列化器
# ===========================

class ReportTypeSerializer(CustomModelSerializer):
    """
    报告类型序列化器
    """
    # creator = serializers.StringRelatedField()

    class Meta:
        model = ReportType
        fields = '__all__'

class ReportTypeCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新报告类型时的序列化器
    """

    class Meta:
        model = ReportType
        fields = '__all__'

# ===========================
# 报告分组模块序列化器
# ===========================

class ReportGroupSerializer(CustomModelSerializer):
    """
    报告分组序列化器
    """
    # creator = serializers.StringRelatedField()

    class Meta:
        model = ReportGroup
        fields = '__all__'

class ReportGroupCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新报告分组时的序列化器
    """

    class Meta:
        model = ReportGroup
        fields = '__all__'

# ===========================
# 频率选项模块序列化器
# ===========================

class FrequencySerializer(CustomModelSerializer):
    """
    频率选项序列化器
    """
    # creator = serializers.StringRelatedField()

    class Meta:
        model = Frequency
        fields = '__all__'

class FrequencyCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新频率选项时的序列化器
    """

    class Meta:
        model = Frequency
        fields = '__all__'

# ===========================
# 简报模块序列化器
# ===========================

class ReportSerializer(CustomModelSerializer):
    """
    简报序列化器
    """
    # creator = serializers.StringRelatedField()
    type = ReportTypeSerializer(read_only=True)
    group = ReportGroupSerializer(read_only=True)

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

class ReportSendSerializer(CustomModelSerializer):
    """
    发送简报时使用的序列化器
    """
    recipients = serializers.ListField(
        child=serializers.EmailField(),
        help_text="邮件接收人列表，多个邮箱使用数组格式提供"
    )
    
    class Meta:
        model = Report
        fields = '__all__'

# ===========================
# 邮件发送记录模块序列化器
# ===========================

class EmailSendRecordSerializer(CustomModelSerializer):
    """
    邮件发送记录序列化器
    """
    # report_id = ReportSerializer(read_only=True)
    

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
    # creator = serializers.StringRelatedField()
    template_group = ReportGroupSerializer()
    template_type = ReportTypeSerializer()

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
    template = TemplateSerializer()
    # creator = serializers.StringRelatedField()

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
    job = ScheduledTaskSerializer(read_only=True)

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
    # creator = serializers.StringRelatedField()
    report_type = ReportTypeSerializer()

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