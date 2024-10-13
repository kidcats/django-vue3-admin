import hashlib
import os
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
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


REPORT_TYPES = [
    ('日报', '日报'),
    ('周报', '周报'),
    ('月报', '月报'),
    ('季报', '季报'),
    ('年报', '年报'),
    ('其它', '其它'),
]

# ===========================
# 简报管理模块模型
# ===========================

class Report(CoreModel):


    title = models.CharField(max_length=255, verbose_name="简报标题", help_text="简报标题")
    type = models.CharField(
        max_length=10, choices=REPORT_TYPES, verbose_name="简报类型", help_text="简报类型"
    )
    summary = models.TextField(verbose_name="简报摘要", help_text="简报摘要")
    content = models.TextField(verbose_name="简报内容", help_text="简报内容")
    report_date = models.DateField(verbose_name="简报日期", help_text="简报日期")
    creator = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='report_reports',
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
    TEMPLATE_TYPES = [
        ('日报', '日报'),
        ('周报', '周报'),
        ('月报', '月报'),
        ('季报', '季报'),
        ('年报', '年报'),
    ]

    template_type = models.CharField(
        max_length=10, choices=TEMPLATE_TYPES, verbose_name="模板类型", help_text="模板类型"
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
    FREQUENCY_CHOICES = [
        ('0 8 * * *', '每天8点'),
        ('0 9 * * *', '每天9点'),
        ('0 10 * * *', '每天10点'),
        ('0 10 * * 1', '每周一10点'),
        ('0 9 1 * *', '每月1号9点'),
        # 根据需要添加更多的频率选项
    ]
    STATUS_CHOICES = [
        ('运行中', '运行中'),
        ('暂停', '暂停'),
    ]

    name = models.CharField(max_length=255, verbose_name="任务名称", help_text="任务名称")
    frequency = models.CharField(
        max_length=20, choices=FREQUENCY_CHOICES, verbose_name="执行频率", help_text="执行频率（Cron表达式）"
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
    details = models.JSONField(verbose_name="详细信息", help_text="详细信息")

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

    report_type = models.CharField(
        max_length=10,
        choices=REPORT_TYPES,
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