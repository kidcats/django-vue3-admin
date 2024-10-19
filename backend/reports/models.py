import hashlib
import os
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.conf import settings
from dvadmin.system.models import Users
from dvadmin.utils.models import CoreModel, table_prefix



def media_file_name(instance, filename):
    """
    自定义文件上传路径函数
    """
    if not instance.md5sum:
        raise ValueError("MD5校验和未生成，无法保存文件。")
    basename, ext = os.path.splitext(filename)
    return os.path.join("files", instance.md5sum[:1], instance.md5sum[1:2], instance.md5sum + ext.lower())


class ReportType(CoreModel):
    name = models.CharField(max_length=50, unique=True, verbose_name="简报类型名称")
    description = models.TextField(blank=True, verbose_name="类型描述")

    class Meta:
        db_table = table_prefix + "report_types"
        verbose_name = "简报类型"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class ReportGroup(CoreModel):
    name = models.CharField(max_length=50, unique=True, verbose_name="简报分组名称")
    description = models.TextField(blank=True, verbose_name="分组描述")

    class Meta:
        db_table = table_prefix + "report_groups"
        verbose_name = "简报分组"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Frequency(CoreModel):
    name = models.CharField(max_length=100, verbose_name="频率名称", help_text="例如：每天8点")
    cron_expression = models.CharField(
        max_length=100, 
        verbose_name="Cron 表达式",
        help_text="Cron 格式的时间表达式",
        validators=[
            RegexValidator(
                regex=r'^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$',
                message="请输入有效的 Cron 表达式",
            ),
        ]
    )
    description = models.TextField(blank=True, verbose_name="描述", help_text="频率的详细描述")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")

    class Meta:
        db_table = table_prefix + "report_frequencies"
        verbose_name = "频率选项"
        verbose_name_plural = verbose_name
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.cron_expression})"
# ===========================
# 简报管理模块模型
# ===========================


class Report(CoreModel):
    title = models.CharField(max_length=255, verbose_name="简报标题", help_text="简报标题")
    type = models.ForeignKey(
        ReportType,
        on_delete=models.PROTECT,
        related_name='reports',
        verbose_name="简报类型",
        help_text="简报类型"
    )
    summary = models.TextField(verbose_name="简报摘要", help_text="简报摘要")
    content = models.TextField(verbose_name="简报内容", help_text="简报内容")
    report_date = models.DateField(verbose_name="简报日期", help_text="简报日期")
    report_group = models.ForeignKey(
        ReportGroup,
        on_delete=models.PROTECT,
        related_name='reports',
        verbose_name="简报分组",
        help_text="简报分组"
    )
    creator = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name="创建者",
        help_text="创建者",
        db_constraint=False,
    )

    class Meta:
        db_table = table_prefix + "report_reports"
        verbose_name = "简报表"
        verbose_name_plural = verbose_name
        ordering = ("-report_date",)

    def __str__(self):
        return self.title


class EmailSendRecord(CoreModel):
    SEND_STATUS = [
        ('成功', '成功'),
        ('失败', '失败'),
    ]

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='report_email_send_records',
        verbose_name="关联简报",
        help_text="关联简报",
        db_constraint=False,
    )
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="发送时间", help_text="发送时间")
    recipients = models.TextField(
        verbose_name="接收者",
        help_text="接收者列表，使用分号分隔"
    )
    status = models.CharField(
        max_length=10, choices=SEND_STATUS, verbose_name="发送状态", help_text="发送状态"
    )

    class Meta:
        db_table = table_prefix + "report_email_send_records"
        verbose_name = "邮件发送记录表"
        verbose_name_plural = verbose_name
        ordering = ("-sent_at",)

    def __str__(self):
        return f"Email to {self.recipients} at {self.sent_at}"


# ===========================
# 模板管理模块模型
# ===========================

class Template(CoreModel):
    
    template_type = models.ForeignKey(
        ReportType,
        on_delete=models.PROTECT,
        related_name='report_templates',
        verbose_name="模板类型",
        help_text="模板类型"
    )
    template_group =  models.ForeignKey(
        ReportGroup,
        on_delete=models.PROTECT,
        related_name='report_templates',
        verbose_name="模板分组",
        help_text="模板分组"
    )
    template_name = models.CharField(max_length=255, verbose_name="模板名称", help_text="模板名称")
    content = models.TextField(verbose_name="模板内容", help_text="模板内容")
    creator = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='report_templates',
        verbose_name="创建者",
        help_text="创建者",
        db_constraint=False,
    )

    class Meta:
        db_table = table_prefix + "report_templates"
        verbose_name = "模板表"
        verbose_name_plural = verbose_name
        ordering = ("id",)

    def __str__(self):
        return self.template_name


# ===========================
# 任务管理模块模型
# ===========================

class ScheduledTask(CoreModel):
    STATUS_CHOICES = [
        ('运行中', '运行中'),
        ('暂停', '暂停'),
    ]

    name = models.CharField(max_length=255, verbose_name="任务名称", help_text="任务名称")
    frequency = models.ForeignKey(
        Frequency,
        on_delete=models.PROTECT,
        related_name='report_scheduled_tasks',
        verbose_name="频率",
        help_text="选择执行频率",
        db_constraint=False,
    )
    template = models.ForeignKey(
        Template,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='report_scheduled_tasks',
        verbose_name="关联模板",
        help_text="关联模板",
        db_constraint=False,
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='运行中', verbose_name="任务状态", help_text="任务状态"
    )
    creator = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='report_scheduled_tasks',
        verbose_name="创建者",
        help_text="创建者",
        db_constraint=False,
    )

    class Meta:
        db_table = table_prefix + "report_scheduled_tasks"
        verbose_name = "定时任务表"
        verbose_name_plural = verbose_name
        ordering = ("id",)

    def __str__(self):
        return self.name


class TaskLog(CoreModel):
    RESULT_CHOICES = [
        ('成功', '成功'),
        ('失败', '失败'),
        ('执行中', '执行中'),
    ]

    job_id = models.CharField(max_length=100, verbose_name="任务ID", help_text="任务ID")
    task_name = models.CharField(max_length=255, verbose_name="任务名称", help_text="任务名称")
    start_time = models.DateTimeField(verbose_name="开始时间", help_text="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间", help_text="结束时间")
    result = models.CharField(
        max_length=10, choices=RESULT_CHOICES, default='执行中', verbose_name="执行结果", help_text="执行结果"
    )
    parameters = models.JSONField(verbose_name="运行参数", help_text="运行参数", default=dict)
    error_info = models.CharField(max_length=255, verbose_name="错误信息", help_text="错误信息",default="无")
    

    class Meta:
        db_table = table_prefix + "report_task_logs"
        verbose_name = "任务日志表"
        verbose_name_plural = verbose_name
        ordering = ("-start_time",)

    def __str__(self):
        return f"{self.task_name} - {self.result}"


class IntermediateData(CoreModel):
    date = models.DateField(verbose_name="日期", help_text="日期")
    internal_attacks = models.IntegerField(
        default=0, verbose_name="内网攻击数", help_text="内网攻击数"
    )
    external_attacks = models.IntegerField(
        default=0, verbose_name="外网攻击数", help_text="外网攻击数"
    )
    other_metrics = models.JSONField(
        default=dict, verbose_name="其他相关指标", help_text="其他相关指标"
    )
    job = models.ForeignKey(
        ScheduledTask,
        on_delete=models.CASCADE,
        related_name='report_intermediate_datas',
        verbose_name="关联任务",
        help_text="关联任务",
        db_constraint=False,
    )

    class Meta:
        db_table = table_prefix + "report_intermediate_datas"
        verbose_name = "中间数据表"
        verbose_name_plural = verbose_name
        ordering = ("-date",)

    def __str__(self):
        return f"{self.date} - 内网: {self.internal_attacks}, 外网: {self.external_attacks}"


# ===========================
# 系统管理模块-邮件管理子模块模型
# ===========================

class EmailConfiguration(CoreModel):

    report_type = models.ForeignKey(
        ReportType,
        on_delete=models.PROTECT,
        related_name='email_config',
        verbose_name="简报类型",
        help_text="简报类型"
    )
    recipients = models.TextField(
        verbose_name="接收者列表",
        help_text="邮件接收人列表，多个邮箱用分号分隔"
    )
    status = models.BooleanField(
        default=True,
        verbose_name="启用状态",
        help_text="启用状态"
    )
    creator = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='report_email_configurations',
        verbose_name="创建者",
        help_text="创建者",
        db_constraint=False,
    )

    class Meta:
        db_table = table_prefix + "report_email_configurations"
        verbose_name = "邮件配置表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

    def __str__(self):
        return f"{self.report_type} - {'启用' if self.status else '禁用'}"