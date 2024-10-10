import datetime
from Tools import YanHuang
from Tools.Mail import send_mail

def querytask(earliestTime, latestTime, query):
    requestBody = {
        "query": query,
        "earliestTime": earliestTime,
        "latestTime": latestTime,
        "timezone": "Asia/Shanghai",
        "autoSort": False,
        "autoTruncate": True,
        "enableFieldsSummary": False,
        "enableTimeline": False,
        "enableSourceTrack": False,
        "forceUpdateSearch": False
    }
    print(requestBody)

    repley = YanHuang.Search.commands(self=YanHuang.Search(), searchCommands=requestBody)
    print('repley:')
    print(repley)
    repley_events = repley['events']
    print("repley_events:")
    print(repley_events)
    return repley_events

def task():
    # 设置当前日期
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    title = "【" + current_date + "】" + "信息安全简报（实业交通）"
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    beforeyesterday = datetime.datetime.now() - datetime.timedelta(days=2)

    report1_name = "**********\r\n*攻击\r\n**********\r\n"
    # report1_todayattack_number = 511
    # report1_yestodayattack_number = 511
    # report1_todayhighattack_attack_number = 46

    earliestTime = int(yesterday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000000)
    latestTime = int(yesterday.replace(hour=23, minute=59, second=59, microsecond=999).timestamp() * 1000000)
    report1_query = "WITH base AS (SELECT * FROM firewall_checkpoint WHERE product = \'SmartDefense\' and protection_type in (\'IPS\', \'anomaly\')) SELECT COUNT(*) AS \"数量\", severity FROM base GROUP BY severity"
    report1_events = querytask(earliestTime, latestTime, report1_query)
    report1_todayattack_number = sum(d['数量'] for d in report1_events)
    report1_todayhighattack_attack_number = sum(d['数量'] for d in report1_events if d['severity'] == '4')
    earliestTime = int(beforeyesterday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000000)
    latestTime = int(beforeyesterday.replace(hour=23, minute=59, second=59, microsecond=999).timestamp() * 1000000)
    report1_events = querytask(earliestTime, latestTime, report1_query)
    report1_yestodayattack_number = sum(d['数量'] for d in report1_events)

    report1_attack_ratio = round((report1_todayattack_number - report1_yestodayattack_number) / report1_yestodayattack_number * 100, 2)
    report1_todayhighattack_ratio = round(report1_todayhighattack_attack_number / report1_todayattack_number * 100, 2)
    if report1_attack_ratio > 0:
        report1_attack_updown = "上升" + str(report1_attack_ratio) + "%"
    if report1_attack_ratio < 0:
        report1_attack_updown = "下降" + str(abs(report1_attack_ratio)) + "%"
    if report1_attack_ratio == 0:
        report1_attack_updown = "持平"
    report1_content = report1_name + "当日0点-24点防火墙报告外部攻击事件" + str(
        report1_todayattack_number) + "例，与上一日" + str(
        report1_yestodayattack_number) + "例相比" + report1_attack_updown + "，" + "其中高危攻击事件" + str(
        report1_todayhighattack_attack_number) + "例占总数" + str(
        report1_todayhighattack_ratio) + "%，未发现异常攻击流量或事件，以上报告的攻击事件均已被阻止。"


    report2_name = "**********\r\n*内网高危行为\r\n**********\r\n"
    # report2_todayNGTP_number = 82
    # report2_yestodayNGTP_number = 82

    earliestTime = int(yesterday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000000)
    latestTime = int(yesterday.replace(hour=23, minute=59, second=59, microsecond=999).timestamp() * 1000000)
    report2_query = "WITH base AS (SELECT * FROM firewall_checkpoint WHERE product in (\'New Anti Virus\', \'Anti Malware\') and protection_type in (\'URL reputation\', \'DNS Trap\', \'protection\') and severity in (\'3\', \'4\')) SELECT COUNT(*) AS \"数量\", severity FROM base GROUP BY severity"
    report2_events = querytask(earliestTime, latestTime, report2_query)
    report2_todayNGTP_number = sum(d['数量'] for d in report2_events)
    earliestTime = int(beforeyesterday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000000)
    latestTime = int(beforeyesterday.replace(hour=23, minute=59, second=59, microsecond=999).timestamp() * 1000000)
    report2_events = querytask(earliestTime, latestTime, report2_query)
    report2_yestodayNGTP_number = sum(d['数量'] for d in report2_events)

    report2_NGTP_ratio = round((report2_todayNGTP_number - report2_yestodayNGTP_number) / report2_yestodayNGTP_number * 100, 2)
    if report2_NGTP_ratio > 0:
        report2_NGTP_updown = "上升" + str(report2_NGTP_ratio) + "%"
    if report2_NGTP_ratio < 0:
        report2_NGTP_updown = "下降" + str(abs(report2_NGTP_ratio)) + "%"
    if report2_NGTP_ratio == 0:
        report2_NGTP_updown = "持平"
    report2_content = report2_name + "当日0点-24点内网流量中检测到高危事件" + str(
        report2_todayNGTP_number) + "例，与上一日" + str(
        report2_yestodayNGTP_number) + "例相比" + report2_NGTP_updown + "，以上所报告的高危事件均已被阻止。目前正在对所有生产机进行逐步检查，对一天内发生多起高危事件的非生产机进行准入管控。"


    report3_name = "**********\r\n*用户问题\r\n**********\r\n"
    # report3_online_number = 71
    # report3_offline_number = 447
    # report3_online_proline_number = 47

    earliestTime = int(yesterday.replace(hour=22, minute=15, second=0, microsecond=0).timestamp() * 1000000)
    latestTime = int(yesterday.replace(hour=22, minute=45, second=0, microsecond=0).timestamp() * 1000000)

    report3_query = "SELECT * FROM nac_online_after_22clock_view"
    report3_events = querytask(earliestTime, latestTime, report3_query)
    report3_online_number = sum(d['数量'] for d in report3_events if d['状态'] == 'online')
    report3_offline_number =  sum(d['数量'] for d in report3_events if d['状态'] == 'offline')
    report3_query = "SELECT * FROM nac_IPConline_after_22clock_view"
    report3_events = querytask(earliestTime, latestTime, report3_query)
    report3_online_proline_number = sum(d['数量'] for d in report3_events if d['状态'] == 'online')

    # report3_online_ratio等于report3_online_number除以report3_online_number加上report3_offline_number的和,取小数点后两位
    report3_online_ratio = round(report3_online_number / (report3_online_number + report3_offline_number) * 100, 2)
    report3_offline_proline_ratio = round((report3_online_proline_number / report3_online_number) * 100, 2)
    report3_offline_ratio = round(((report3_online_number - report3_online_proline_number) / report3_online_number) * 100, 2)
    report3_content = report3_name + "当日22:00后，共有" + str(
        report3_online_number) + "台电脑未关机，未关机电脑占所有电脑的" + str(report3_online_ratio) + "%；产线电脑未关机" + str(
        report3_online_proline_number) + "台，占所有未关机电脑的" + str(report3_offline_proline_ratio) + "%，其余未关机电脑占" + str(report3_offline_ratio) + "%。"

    print(title)
    print(report1_content)
    print(report2_content)
    print(report3_content)
    mail_content = report1_content + "\r\n" + report2_content + "\r\n" + report3_content
    # mail_content = report1_content + "\r\n" + report2_content
    send_mail.send_mail(title, mail_content)

