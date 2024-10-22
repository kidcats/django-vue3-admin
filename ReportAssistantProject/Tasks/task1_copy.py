import datetime
from typing import Dict, List, Any, Tuple
from Tools import YanHuang
from Tools.Mail import send_mail
from dataclasses import dataclass
from abc import ABC, abstractmethod

# 常量定义
TIMEZONE = "Asia/Shanghai"
QUERY_TIME_RANGE = (22, 15, 22, 45)  # 查询时间范围 (开始小时, 开始分钟, 结束小时, 结束分钟)

@dataclass
class QueryConfig:
    """查询配置数据类"""
    query: str
    product: str
    protection_type: List[str]
    severity: List[str]

# 查询配置
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
    """查询执行器类"""

    @staticmethod
    def create_query_request(query: str, earliest_time: int, latest_time: int) -> Dict[str, Any]:
        """
        创建查询请求体
        
        参数:
        query (str): 查询语句
        earliest_time (int): 查询开始时间戳（微秒）
        latest_time (int): 查询结束时间戳（微秒）
        
        返回:
        Dict[str, Any]: 包含查询请求详情的字典
        """
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
    def execute_query(request_body: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        执行查询并返回结果
        
        参数:
        request_body (Dict[str, Any]): 查询请求体
        
        返回:
        List[Dict[str, Any]]: 查询结果列表
        """
        reply = YanHuang.Search.commands(self=YanHuang.Search(), searchCommands=request_body)
        return reply['events']

class TimeHelper:
    """时间辅助类"""

    @staticmethod
    def get_timestamp_range(date: datetime.datetime) -> Tuple[int, int]:
        """
        获取指定日期的开始和结束时间戳
        
        参数:
        date (datetime.datetime): 指定日期
        
        返回:
        Tuple[int, int]: (开始时间戳, 结束时间戳)，单位为微秒
        """
        start = int(date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000000)
        end = int(date.replace(hour=23, minute=59, second=59, microsecond=999).timestamp() * 1000000)
        return start, end

    @staticmethod
    def get_query_time_range(date: datetime.datetime) -> Tuple[int, int]:
        """
        获取查询时间范围的时间戳
        
        参数:
        date (datetime.datetime): 指定日期
        
        返回:
        Tuple[int, int]: (查询开始时间戳, 查询结束时间戳)，单位为微秒
        """
        start = int(date.replace(hour=QUERY_TIME_RANGE[0], minute=QUERY_TIME_RANGE[1], second=0, microsecond=0).timestamp() * 1000000)
        end = int(date.replace(hour=QUERY_TIME_RANGE[2], minute=QUERY_TIME_RANGE[3], second=0, microsecond=0).timestamp() * 1000000)
        return start, end

class ReportGenerator(ABC):
    """报告生成器抽象基类"""

    def __init__(self):
        self.query_executor = QueryExecutor()
        self.time_helper = TimeHelper()

    @abstractmethod
    def generate_report(self) -> str:
        """
        生成报告
        
        返回:
        str: 生成的报告文本
        """
        pass

    def calculate_change_ratio(self, current: int, previous: int) -> Tuple[float, str]:
        """
        计算变化率和变化描述
        
        参数:
        current (int): 当前值
        previous (int): 前一个值

        返回:
        Tuple[float, str]: (变化率, 变化描述)
        """
        if previous == 0:
            return 0, "无法计算（前值为0）"
        
        # 计算变化率: (当前值 - 前一个值) / 前一个值 * 100%
        ratio = round((current - previous) / previous * 100, 2)
        if ratio > 0:
            description = f"上升{ratio}%"
        elif ratio < 0:
            description = f"下降{abs(ratio)}%"
        else:
            description = "持平"
        return ratio, description

class AttackReportGenerator(ReportGenerator):
    """攻击情况报告生成器"""

    def generate_report(self) -> str:
        """
        生成攻击情况报告
        
        返回:
        str: 攻击情况报告文本
        """
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        before_yesterday = datetime.datetime.now() - datetime.timedelta(days=2)

        query = ATTACK_QUERY_CONFIG.query.format(
            product=ATTACK_QUERY_CONFIG.product,
            protection_type=', '.join(ATTACK_QUERY_CONFIG.protection_type)
        )

        yesterday_events = self.query_executor.execute_query(
            self.query_executor.create_query_request(query, *self.time_helper.get_timestamp_range(yesterday))
        )
        before_yesterday_events = self.query_executor.execute_query(
            self.query_executor.create_query_request(query, *self.time_helper.get_timestamp_range(before_yesterday))
        )

        # 计算攻击次数
        today_attack_number = sum(d['数量'] for d in yesterday_events)
        today_high_attack_number = sum(d['数量'] for d in yesterday_events if d['severity'] in ATTACK_QUERY_CONFIG.severity)
        yesterday_attack_number = sum(d['数量'] for d in before_yesterday_events)

        # 计算变化率和高危攻击比例
        _, attack_change = self.calculate_change_ratio(today_attack_number, yesterday_attack_number)
        # 高危攻击比例 = 高危攻击次数 / 总攻击次数 * 100%
        high_attack_ratio = round(today_high_attack_number / today_attack_number * 100, 2) if today_attack_number != 0 else 0

        return f"**********\n*攻击\n**********\n" \
               f"当日0点-24点防火墙报告外部攻击事件{today_attack_number}例，与上一日{yesterday_attack_number}例相比{attack_change}，" \
               f"其中高危攻击事件{today_high_attack_number}例占总数{high_attack_ratio}%，" \
               f"未发现异常攻击流量或事件，以上报告的攻击事件均已被阻止。"

class HighRiskBehaviorReportGenerator(ReportGenerator):
    """内网高危行为报告生成器"""

    def generate_report(self) -> str:
        """
        生成内网高危行为报告
        
        返回:
        str: 内网高危行为报告文本
        """
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        before_yesterday = datetime.datetime.now() - datetime.timedelta(days=2)

        query = HIGH_RISK_QUERY_CONFIG.query.format(
            product=HIGH_RISK_QUERY_CONFIG.product,
            protection_type=', '.join(HIGH_RISK_QUERY_CONFIG.protection_type),
            severity=', '.join(HIGH_RISK_QUERY_CONFIG.severity)
        )

        yesterday_events = self.query_executor.execute_query(
            self.query_executor.create_query_request(query, *self.time_helper.get_timestamp_range(yesterday))
        )
        before_yesterday_events = self.query_executor.execute_query(
            self.query_executor.create_query_request(query, *self.time_helper.get_timestamp_range(before_yesterday))
        )

        # 计算高危事件数量
        today_high_risk_number = sum(d['数量'] for d in yesterday_events)
        yesterday_high_risk_number = sum(d['数量'] for d in before_yesterday_events)

        # 计算变化率
        _, high_risk_change = self.calculate_change_ratio(today_high_risk_number, yesterday_high_risk_number)

        return f"**********\n*内网高危行为\n**********\n" \
               f"当日0点-24点内网流量中检测到高危事件{today_high_risk_number}例，与上一日{yesterday_high_risk_number}例相比{high_risk_change}，" \
               f"以上所报告的高危事件均已被阻止。目前正在对所有生产机进行逐步检查，对一天内发生多起高危事件的非生产机进行准入管控。"

class UserIssueReportGenerator(ReportGenerator):
    """用户问题（未关机情况）报告生成器"""

    def generate_report(self) -> str:
        """
        生成用户问题（未关机情况）报告
        
        返回:
        str: 用户问题报告文本
        """
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        start, end = self.time_helper.get_query_time_range(yesterday)

        online_events = self.query_executor.execute_query(
            self.query_executor.create_query_request(USER_ISSUE_QUERY_CONFIG['online'], start, end)
        )
        proline_events = self.query_executor.execute_query(
            self.query_executor.create_query_request(USER_ISSUE_QUERY_CONFIG['proline'], start, end)
        )

        # 计算各类设备数量
        online_number = sum(d['数量'] for d in online_events if d['状态'] == 'online')
        offline_number = sum(d['数量'] for d in online_events if d['状态'] == 'offline')
        online_proline_number = sum(d['数量'] for d in proline_events if d['状态'] == 'online')

        # 计算比例
        total_computers = online_number + offline_number
        # 未关机比例 = 未关机电脑数 / 总电脑数 * 100%
        online_ratio = round(online_number / total_computers * 100, 2) if total_computers != 0 else 0
        # 产线未关机比例 = 产线未关机电脑数 / 未关机电脑数 * 100%
        proline_ratio = round(online_proline_number / online_number * 100, 2) if online_number != 0 else 0
        # 非产线未关机比例 = (未关机电脑数 - 产线未关机电脑数) / 未关机电脑数 * 100%
        non_proline_ratio = round((online_number - online_proline_number) / online_number * 100, 2) if online_number != 0 else 0

        return f"**********\n*用户问题\n**********\n" \
               f"当日22:00后，共有{online_number}台电脑未关机，未关机电脑占所有电脑的{online_ratio}%；" \
               f"产线电脑未关机{online_proline_number}台，占所有未关机电脑的{proline_ratio}%，" \
               f"其余未关机电脑占{non_proline_ratio}%。"

class DailyReportGenerator:
    """每日报告生成器"""

    def __init__(self):
        self.attack_report_generator = AttackReportGenerator()
        self.high_risk_report_generator = HighRiskBehaviorReportGenerator()
        self.user_issue_report_generator = UserIssueReportGenerator()

    def generate_daily_report(self) -> Tuple[str, str]:
        """
        生成每日安全简报
        
        返回:
        Tuple[str, str]: (报告标题, 报告内容)
        """
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        title = f"【{current_date}】信息安全简报（实业交通）"

        attack_report = self.attack_report_generator.generate_report()
        high_risk_report = self.high_risk_report_generator.generate_report()
        user_issue_report = self.user_issue_report_generator.generate_report()

        content = f"{attack_report}\n\n{high_risk_report}\n\n{user_issue_report}"

        return title, content

def send_daily_report(title: str, content: str) -> None:
    """
    发送每日安全简报邮件
    
    参数:
    title (str): 邮件标题
    content (str): 邮件内容
    """
    send_mail.send_mail(title, content)

def main() -> None:
    """
    主函数，执行每日报告生成和发送流程
    """
    report_generator = DailyReportGenerator()
    title, content = report_generator.generate_daily_report()
    send_daily_report(title, content)

if __name__ == "__main__":
    main()