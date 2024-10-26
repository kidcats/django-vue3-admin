import smtplib
from email.mime.text import MIMEText
from django.utils import timezone
from reports.models import EmailConfiguration,EmailSendRecord,Report,ReportType
from datetime import datetime

# class EmailSender:
#     def __init__(self):
#         self.mailserver = "mail.stec-cn.com"
#         self.username_loginmail = "hanjie.hu"
#         self.username_sendmail = "hanjie.hu@stec-cn.com"
#         self.password_sendmail = "************"
class EmailSender:
    def __init__(self):
        self.mailserver = "smtp.office365.com"  # Outlook SMTP服务器
        self.port = 587  # Outlook推荐端口
        self.username_loginmail = "kidcats233@outlook.com"  # 完整邮箱地址
        self.username_sendmail = "kidcats233@outlook.com"  # 发件人邮箱
        self.password_sendmail = "11202425xzy"  # 应用密码或账户密码
    
    def get_active_configurations(self, report_type_id):
        """获取指定报告类型的所有活动邮件配置"""
        return EmailConfiguration.objects.filter(
            report_type_id=report_type_id,
            status=True
        )

    def get_recipients_from_config(self, config):
        """从邮件配置中获取收件人列表"""
        if not config.recipients:
            return []
        return [email.strip() for email in config.recipients.split(';') if email.strip()]

    def record_send_status(self, report, recipients, is_success, error_message=None):
        """记录邮件发送状态"""
        status = '成功' if is_success else '失败'
        record = EmailSendRecord.objects.create(
            report=report,
            recipients=';'.join(recipients),
            status=status,
            sent_at=datetime.now(),
            creator=report.creator,
            description=error_message if error_message else None
        )
        return record

    def send_mail(self, report_id, mail_subject, mail_content):
        try:
            # 获取Report对象
            report = Report.objects.get(id=report_id)
            report_type = ReportType.objects.get(id=report.type)
            email_config = self.get_active_configurations(report_type.id)
            
            # 获取收件人列表
            recipients = self.get_recipients_from_config(email_config)
            if not recipients:
                raise ValueError("No recipients specified")

            # 构造邮件
            email = MIMEText(mail_content, 'plain', 'utf-8')
            email['Subject'] = mail_subject
            email['From'] = self.username_sendmail
            email['To'] = ';'.join(recipients)

            # # 发送邮件
            # smtp = smtplib.SMTP(self.mailserver, 25)
            # smtp.starttls()
            # smtp.login(self.username_loginmail, self.password_sendmail)
            # smtp.sendmail(self.username_sendmail, recipients, email.as_string())
            # smtp.quit()
            # 建立连接并发送
            smtp = smtplib.SMTP(self.mailserver, self.port)
            smtp.ehlo()  # 向邮件服务器发送EHLO
            smtp.starttls()  # 启用TLS加密
            smtp.login(self.username_loginmail, self.password_sendmail)
            smtp.send_message(email)
            smtp.quit()

            # 记录成功状态
            self.record_send_status(report, recipients, True)
            logging.info(f"邮件发送成功 - Report ID: {report_id}")
            return True

        except Report.DoesNotExist:
            error_message = f"Report with ID {report_id} does not exist"
            print(error_message)
            return False

        except Exception as e:
            # 记录失败状态
            error_message = str(e)
            if 'report' in locals() and 'recipients' in locals():
                self.record_send_status(report, recipients, False, error_message)
            print(f"邮件发送失败 - Report ID: {report_id}")
            print(f"错误信息: {error_message}")
            return False