import datetime
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from reports.models import QueryConfig, Report, Task
from Tools import YanHuang
from Tools.Mail import send_mail as custom_send_mail

TIMEZONE = "Asia/Shanghai"
QUERY_TIME_RANGE = (22, 15, 22, 45)

class QueryExecutor:
    @staticmethod
    def create_query_request(query, earliest_time, latest_time):
        return {
            "query": query,
            "earliestTime": earliest_time,
            "latestTime": latest_time,
            "timezone": TIMEZONE,
            "autoSort": False,
            "autoTruncate": True,
            "enableFieldsSummary": False,
            "enableTimeline": False,
            "enableSourceTrack": False,
            "forceUpdateSearch": False
        }

    @staticmethod
    def execute_query(request_body):
        reply = YanHuang.Search.commands(self=YanHuang.Search(), searchCommands=request_body)
        return reply['events']

class TimeHelper:
    @staticmethod
    def get_timestamp_range(date):
        start = int(date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000000)
        end = int(date.replace(hour=23, minute=59, second=59, microsecond=999).timestamp() * 1000000)
        return start, end

    @staticmethod
    def get_query_time_range(date):
        start = int(date.replace(hour=QUERY_TIME_RANGE[0], minute=QUERY_TIME_RANGE[1], second=0, microsecond=0).timestamp() * 1000000)
        end = int(date.replace(hour=QUERY_TIME_RANGE[2], minute=QUERY_TIME_RANGE[3], second=0, microsecond=0).timestamp() * 1000000)
        return start, end

class ReportGenerator:
    def __init__(self):
        self.query_executor = QueryExecutor()
        self.time_helper = TimeHelper()

    def calculate_change_ratio(self, current, previous):
        if previous == 0:
            return 0, "无法计算（前值为0）"
        ratio = round((current - previous) / previous * 100, 2)
        if ratio > 0:
            description = f"上升{ratio}%"
        elif ratio < 0:
            description = f"下降{abs(ratio)}%"
        else:
            description = "持平"
        return ratio, description

    def generate_attack_report(self):
        # 实现攻击报告生成逻辑
        pass

    def generate_high_risk_report(self):
        # 实现高危行为报告生成逻辑
        pass

    def generate_user_issue_report(self):
        # 实现用户问题报告生成逻辑
        pass

    def generate_daily_report(self):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        title = f"【{current_date}】信息安全简报（实业交通）"

        attack_report = self.generate_attack_report()
        high_risk_report = self.generate_high_risk_report()
        user_issue_report = self.generate_user_issue_report()

        content = f"{attack_report}\n\n{high_risk_report}\n\n{user_issue_report}"

        return title, content

@shared_task
def generate_and_send_report(scheduled_task_id):
    try:
        scheduled_task = ScheduledTask.objects.get(id=scheduled_task_id)
        query_config = scheduled_task.query_config

        # 生成报告
        report_generator = ReportGenerator()
        title, content = report_generator.generate_daily_report(query_config)

        # 保存报告
        report = Report.objects.create(title=title, content=content)

        # 发送邮件
        custom_send_mail(title, content)

        # 更新任务状态
        scheduled_task.last_run = datetime.datetime.now()
        scheduled_task.save()

        return f"Report generated and sent successfully: {title}"
    except Exception as e:
        # 错误处理
        return f"Error generating and sending report: {str(e)}"



@shared_task
def update_celery_beat_schedule():
    from django_celery_beat.models import PeriodicTask, CrontabSchedule
    
    # 获取所有活跃的计划任务
    active_tasks = ScheduledTask.objects.filter(is_active=True)
    
    for task in active_tasks:
        # 解析 cron 表达式
        minute, hour, day, month, day_of_week = task.cron_expression.split()
        
        # 创建或更新 CrontabSchedule
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_month=day,
            month_of_year=month,
            day_of_week=day_of_week
        )
        
        # 创建或更新 PeriodicTask
        PeriodicTask.objects.update_or_create(
            name=f"generate_report_{task.id}",
            defaults={
                'task': 'your_app.tasks.generate_and_send_report',
                'crontab': schedule,
                'args': [task.id],
                'enabled': False,
            }
        )
    
    # 删除不再活跃的任务
    # PeriodicTask.objects.exclude(
    #     name__in=[f"generate_report_{task.id}" for task in active_tasks]
    # ).delete()