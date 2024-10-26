from datetime import datetime, timedelta, date, time
from celery import shared_task
from django.core.mail import send_mail
from reports.models import ScheduledTask,Template
from django.conf import settings
from reports.models import QueryConfig, Report, Task,TaskLog
from Tools import YanHuang
from Tools.Mail.send_mail import EmailSender
import logging
from typing import Dict,Any,List
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

logger = logging.getLogger(__name__)
TIMEZONE = "Asia/Shanghai"
QUERY_TIME_RANGE = (22, 15, 22, 45)

ATTACK_QUERY_CONFIG = QueryConfig(
    query="WITH base AS (SELECT * FROM firewall_checkpoint WHERE product = '{product}' and protection_type in ({protection_type})) SELECT COUNT(*) AS \"数量\", severity FROM base GROUP BY severity",
    product="SmartDefense",
    protection_type=["'IPS'", "'anomaly'"],
    severity=["'4'"]
)

HIGH_RISK_QUERY_CONFIG = QueryConfig(
    query="WITH base AS (SELECT * FROM firewall_checkpoint WHERE product in ({product}) and protection_type in ({protection_type}) and severity in ({severity})) SELECT COUNT(*) AS \"数量\", severity FROM base GROUP BY severity",
    product="'New Anti Virus', 'Anti Malware'",
    protection_type=["'URL reputation'", "'DNS Trap'", "'protection'"],
    severity=["'3'", "'4'"]
)

USER_ISSUE_QUERY_CONFIG = {
    "online": "SELECT * FROM nac_online_after_22clock_view",
    "proline": "SELECT * FROM nac_IPConline_after_22clock_view"
}


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
    def __init__(self, template: Template):
        self.template = template
        self.query_executor = QueryExecutor()
        self.time_helper = TimeHelper()
        
    def generate(self, date: datetime = None) -> str:
        """生成最终报告"""
        if date is None:
            date = datetime.now() - timedelta(days=1)
            
        # 获取所有数据
        data = self._generate_all_data(date)
        logger.info("获取所有数据")
        logger.info(data)
        # 解析并渲染模板
        return self._parse_template(self.template.content, data)
        
    def _generate_all_data(self, date: datetime) -> Dict[str, Any]:
        """生成所有可能用到的报告数据"""
        # report1_events
        # report2_events
        # report3_query
        # report1_todayattack_number = 511
        # report1_yestodayattack_number = 511
        # report1_todayhighattack_attack_number = 46
        data = {}
        previous_date = date - timedelta(days=1)
        
        # 生成所有类型的数据
        # data.update(self._generate_attack_data(date, previous_date))
        # data.update(self._generate_high_risk_data(date, previous_date))
        # data.update(self._generate_user_issue_data(date, previous_date))
        data = {
            "attack_number": 100,
            "attack_change": 100 - 80,
            "attack_change_ratio": 0.2,
            "high_attack_number": 120,
            "high_attack_ratio": 0.3,
            "attack_events": "current_events",
            "attack_distribution": {},
            "high_risk_number": 20,
            "high_risk_change": 20,
            "high_risk_change_ratio": 0.3,
            "behavior_type_distribution": "1",
            "top_behavior_types": ["1","2"],
            "high_risk_events": "current_events",
            "issue_number": 20,
            "issue_change": 30,
            "issue_change_ratio": 0.7,
            "issue_type_distribution": "issue_types",
            "top_issue_types": ["3","2"],
            "issue_events": "nothing"
        }
        
        
        # 添加通用数据
        data.update({
            "report_date": date.strftime("%Y-%m-%d"),
            "time_range": f"{QUERY_TIME_RANGE[0]}:00-{QUERY_TIME_RANGE[1]}:00"
        })
            
        return data

    def _generate_attack_data(self, date: datetime, previous_date: datetime) -> Dict[str, Any]:
        """生成攻击报告相关数据"""
        current_query = ATTACK_QUERY_CONFIG.query.format(
            product=ATTACK_QUERY_CONFIG.product,
            protection_type=', '.join(ATTACK_QUERY_CONFIG.protection_type)
        )
        
        current_events = self._execute_date_query(current_query, date)
        previous_events = self._execute_date_query(current_query, previous_date)
        
        current_total = len(current_events)
        previous_total = len(previous_events)
        high_risk_events = [e for e in current_events if self._is_high_risk_attack(e)]
        high_risk_total = len(high_risk_events)
        
        return {
            "attack_number": current_total,
            "attack_change": current_total - previous_total,
            "attack_change_ratio": self._format_change_ratio(current_total, previous_total),
            "high_attack_number": high_risk_total,
            "high_attack_ratio": self._calculate_ratio(high_risk_total, current_total),
            "attack_events": current_events,
            "attack_distribution": self._analyze_event_distribution(current_events, 'attack_type')
        }

    def _generate_high_risk_data(self, date: datetime, previous_date: datetime) -> Dict[str, Any]:
        """生成高危行为报告相关数据"""
        query = HIGH_RISK_QUERY_CONFIG.query.format(
            risk_level=HIGH_RISK_QUERY_CONFIG.risk_level
        )
        
        current_events = self._execute_date_query(query, date)
        previous_events = self._execute_date_query(query, previous_date)
        
        behavior_types = self._analyze_event_distribution(current_events, 'behavior_type')
        
        return {
            "high_risk_number": len(current_events),
            "high_risk_change": len(current_events) - len(previous_events),
            "high_risk_change_ratio": self._format_change_ratio(len(current_events), len(previous_events)),
            "behavior_type_distribution": behavior_types,
            "top_behavior_types": sorted(behavior_types.items(), key=lambda x: x[1], reverse=True)[:5],
            "high_risk_events": current_events
        }

    def _generate_user_issue_data(self, date: datetime, previous_date: datetime) -> Dict[str, Any]:
        """生成用户问题报告相关数据"""
        query = USER_ISSUE_QUERY_CONFIG.query
        
        current_issues = self._execute_date_query(query, date)
        previous_issues = self._execute_date_query(query, previous_date)
        
        issue_types = self._analyze_event_distribution(current_issues, 'issue_type')
        
        return {
            "issue_number": len(current_issues),
            "issue_change": len(current_issues) - len(previous_issues),
            "issue_change_ratio": self._format_change_ratio(len(current_issues), len(previous_issues)),
            "issue_type_distribution": issue_types,
            "top_issue_types": sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:5],
            "issue_events": current_issues
        }

    def _execute_date_query(self, query: str, date: datetime) -> List[Any]:
        """执行指定日期的查询"""
        start_time, end_time = self.time_helper.get_query_time_range(date)
        query_request = self.query_executor.create_query_request(query, start_time, end_time)
        return self.query_executor.execute_query(query_request)

    def _parse_template(self, template_content: str, data: Dict[str, Any]) -> str:
        """解析模板内容并替换变量"""
        # 替换变量
        content = template_content
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        
        # 处理条件语句
        return self._process_conditional_content(content, data)

    def _process_conditional_content(self, content: str, data: Dict[str, Any]) -> str:
        """处理条件语句"""
        lines = content.split('\n')
        result_lines = []
        skip_until_endif = False
        
        for line in lines:
            if line.strip().startswith('{%if'):
                condition = self._evaluate_condition(line, data)
                skip_until_endif = not condition
                continue
            
            if line.strip() in ['{%else%}', '{%endif%}']:
                skip_until_endif = not skip_until_endif
                continue
            
            if not skip_until_endif:
                result_lines.append(line)
        
        return '\n'.join(result_lines)

    def _evaluate_condition(self, condition_line: str, data: Dict[str, Any]) -> bool:
        """评估条件语句"""
        condition = condition_line.split('%}')[0].split('if')[1].strip()
        # 实现条件评估逻辑
        return eval(condition, {"__builtins__": {}}, data)

    def _format_change_ratio(self, current: int, previous: int) -> str:
        """格式化变化率"""
        if previous == 0:
            return "无前期数据" if current == 0 else "新增"
        
        change = ((current - previous) / previous) * 100
        if change > 0:
            return f"上升{round(change, 2)}%"
        elif change < 0:
            return f"下降{round(abs(change), 2)}%"
        return "持平"

    def _calculate_ratio(self, part: int, total: int) -> float:
        """计算占比"""
        return (part / total * 100) if total > 0 else 0

    def _analyze_event_distribution(self, events: List[Any], field: str) -> Dict[str, int]:
        """分析事件分布"""
        distribution = {}
        for event in events:
            key = getattr(event, field)
            distribution[key] = distribution.get(key, 0) + 1
        return distribution

    def _is_high_risk_attack(self, event: Any) -> bool:
        """判断是否为高风险攻击"""
        return event.risk_level >= HIGH_RISK_LEVEL

@shared_task(bind=True)
def generate_and_send_report(self, **kwargs):
    task_id = kwargs.get('task_id')
    title = kwargs.get('task_name')
    creator = kwargs.get('creator')
    
    # 创建任务日志
    task_log = TaskLog.objects.create(
        task_id=self.request.id,  # Celery任务ID
        task_name=f"{title}_{task_id}",
        start_time=datetime.now(),
        parameters=kwargs,
        result='执行中',
        creator=creator
    )
    logger.info("创建任务日志")
    try:
        scheduled_task = ScheduledTask.objects.get(id=task_id)
            
        if not scheduled_task.is_active:
            task_log.result = '失败'
            task_log.error_info = f"Task {task_id} is no longer active"
            task_log.end_time = datetime.now()
            task_log.save()
            return task_log.error_info
                
        template = Template.objects.get(id=scheduled_task.template.id)
            
            # 生成报告内容
        report_generator = ReportGenerator(template)
        report_content = report_generator.generate()
            
        title = f"{scheduled_task.name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # 保存报告
        report, created = Report.objects.get_or_create(
            schedule_task=scheduled_task,
            defaults={
                'title': title,
                'type': scheduled_task.template.template_type,
                'report_group': scheduled_task.template.template_group,
                'creator': scheduled_task.template.creator,
                'content': report_content,
                "report_date" : datetime.now().date()
            }
        )
            
            # 发送邮件
        email_sender = EmailSender()
        logger.info("准备发送邮件")
        email_sender.send_mail(report.id,title,report_content)
            
            # 更新执行时间
        scheduled_task.last_run = datetime.now()
        scheduled_task.save()
            
            # 更新任务日志为成功
        task_log.result = '成功'
        task_log.end_time = datetime.now()
        task_log.save()
        logger.info("创建任务日志成功")
            
        return f"Report generated and sent successfully: {title}"
        
    except Exception as e:
        # 更新任务日志为失败
        task_log.result = '失败'
        task_log.error_info = str(e)
        task_log.end_time = datetime.now()
        task_log.save()
        logger.info("创建失败任务日志")
        
        return f"Error: {str(e)}"


@shared_task
def update_celery_beat_schedule():
    try:
        # 获取所有激活的任务
        active_tasks = ScheduledTask.objects.filter(is_active=True)
        
        # 存储所有活跃任务的名称，用于后续清理
        active_task_names = set()

        # 获取现有的周期性任务
        existing_tasks = {
            task.name: task 
            for task in PeriodicTask.objects.filter(
                task='reports.tasks.generate_and_send_report'
            )
        }

        for task in active_tasks:
            task_name = f"{task.name}_generate_report_{task.id}"
            active_task_names.add(task_name)
            
            # 如果任务已存在且正在运行，跳过更新
            existing_task = existing_tasks.get(task_name)
            if existing_task:
                continue

            # 对于新任务，创建定时计划
            minute, hour, day, month, day_of_week = task.cron_expression.split()
            
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=minute,
                hour=hour,
                day_of_month=day,
                month_of_year=month,
                day_of_week=day_of_week
            )
            schedule.timezone = 'Asia/Shanghai'
            schedule.save()

            # 准备任务参数
            task_kwargs = {
                'task_id': task.id,
                'template_id': task.template.id,
                'title': task_name,
                'creator':task.template.creator,
            }
            logger.info(task_kwargs)
            
            # 只创建新任务，不更新现有任务
            PeriodicTask.objects.create(
                name=task_name,
                task='reports.tasks.generate_and_send_report',
                crontab=schedule,
                kwargs=json.dumps(task_kwargs),
                enabled=True,
            )
        
        # 清理不再激活的任务，但排除正在运行的任务
        inactive_tasks = PeriodicTask.objects.filter(
            task='reports.tasks.generate_and_send_report'
        ).exclude(
            name__in=active_task_names
        )
        
        for inactive_task in inactive_tasks:
            # 如果任务处于运行状态，跳过删除
            if TaskLog.objects.filter(
                task_name=inactive_task.name,
                result='执行中'
            ).exists():
                continue
            inactive_task.delete()
        
        return "Successfully updated celery beat schedule"
    except Exception as e:
        logger.error(f"Error in update_celery_beat_schedule: {str(e)}")
        return f"Error updating celery beat schedule: {str(e)}"