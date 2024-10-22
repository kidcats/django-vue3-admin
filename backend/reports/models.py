import hashlib
import os
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.conf import settings
from dvadmin.system.models import Users
from dvadmin.utils.models import CoreModel, table_prefix
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json



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

class QueryConfig(models.Model):
    name = models.CharField(max_length=100)
    query = models.TextField()
    product = models.CharField(max_length=100)
    protection_type = models.JSONField()
    severity = models.JSONField()

class Task(CoreModel):
    STATUS_CHOICES = (
        ('active', '活动'),
        ('paused', '暂停'),
        ('completed', '已完成'),
        ('error', '错误'),
    )

    name = models.CharField(max_length=255, unique=True, verbose_name="任务名称")
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='task', verbose_name="关联的简报")
    template = models.ForeignKey(Template, on_delete=models.PROTECT, related_name='tasks', verbose_name="使用的模板")
    periodic_task = models.OneToOneField(PeriodicTask, 
                                         on_delete=models.CASCADE, 
                                         null=True, blank=True, verbose_name="定时任务",
                                         related_name='report_task'  # 添加这一行
                                         )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="任务状态")
    last_run = models.DateTimeField(null=True, blank=True, verbose_name="上次运行时间")
    next_run = models.DateTimeField(null=True, blank=True, verbose_name="下次运行时间")
    creator = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='report_task',
        verbose_name="创建者",
        help_text="创建者",
        db_constraint=False,
    )
    class Meta:
        db_table = table_prefix + "report_tasks"
        verbose_name = "任务"
        verbose_name_plural = verbose_name
        ordering = ("create_datetime",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new or not self.periodic_task:
            self.create_or_update_periodic_task()

    def create_or_update_periodic_task(self):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=self.report.frequency.cron_expression.split()[0],
            hour=self.report.frequency.cron_expression.split()[1],
            day_of_month=self.report.frequency.cron_expression.split()[2],
            month_of_year=self.report.frequency.cron_expression.split()[3],
            day_of_week=self.report.frequency.cron_expression.split()[4],
        )
        
        if self.periodic_task:
            self.periodic_task.crontab = schedule
            self.periodic_task.name = f'Generate and send report: {self.name}'
            self.periodic_task.task = 'your_app.tasks.generate_and_send_report'
            self.periodic_task.args = json.dumps([self.id])
            self.periodic_task.save()
        else:
            self.periodic_task = PeriodicTask.objects.create(
                crontab=schedule,
                name=f'Generate and send report: {self.name}',
                task='your_app.tasks.generate_and_send_report',
                args=json.dumps([self.id]),
            )
            self.save()

    def delete(self, *args, **kwargs):
        if self.periodic_task:
            self.periodic_task.delete()
        super().delete(*args, **kwargs)

    def pause(self):
        if self.periodic_task:
            self.periodic_task.enabled = False
            self.periodic_task.save()
        self.status = 'paused'
        self.save()

    def resume(self):
        if self.periodic_task:
            self.periodic_task.enabled = True
            self.periodic_task.save()
        self.status = 'active'
        self.save()

    def update_next_run(self):
        if self.periodic_task:
            self.next_run = self.periodic_task.schedule.next()
            self.save()


class ScheduledTask(CoreModel):
    STATUS_CHOICES = [
        ('运行中', '运行中'),
        ('暂停', '暂停'),
    ]

    name = models.CharField(max_length=255, verbose_name="任务名称", help_text="任务名称")
    cron_expression = models.CharField(max_length=255, verbose_name="运行频率", help_text="运行频率")
    # query_config = models.ForeignKey(QueryConfig, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    last_run = models.DateTimeField(null=True, blank=True)
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