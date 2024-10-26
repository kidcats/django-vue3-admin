import smtplib
from email.mime.text import MIMEText
from django.utils import timezone
from reports.models import EmailConfiguration, EmailSendRecord, Report, ReportType
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.mailserver = "smtp.gmail.com"
        self.port = 587
        self.username_loginmail = "kidcats233@gmail.com"
        self.username_sendmail = "kidcats233@gmail.com"
        self.password_sendmail = "rjag bipt ebbl wuro"
    
    def get_active_configurations(self, report_type_id):
        """获取指定报告类型的所有活动邮件配置"""
        return EmailConfiguration.objects.filter(
            report_type_id=report_type_id,
            status=True
        )

    def get_recipients_from_config(self, config):
        """从邮件配置中获取收件人列表"""
        config_instance = config.first()
        if not config_instance or not config_instance.recipients:
            return []
        return [email.strip() for email in config_instance.recipients.split(';') if email.strip()]

    def record_send_status(self, report, recipients, is_success, error_message=None):
        """记录邮件发送状态"""
        status = '成功' if is_success else '失败'
        record = EmailSendRecord.objects.create(
            report=report,
            recipients=';'.join(recipients),
            status=status,
            sent_at=datetime.now(),
            creator=report.creator,
            descriptions=error_message if error_message else "成功发送"
        )
        return record

    def send_mail(self, report_id, mail_subject, mail_content):
        try:
            # 获取Report对象
            report = Report.objects.get(id=report_id)
            
            report_type = ReportType.objects.get(id=report.type.id)
            email_config = self.get_active_configurations(report_type.id)
            logger.info(email_config.values())
            
            # 获取收件人列表
            recipients = self.get_recipients_from_config(email_config)
            if not recipients:
                raise ValueError("No recipients specified")

            # 建立SMTP连接
            smtp = smtplib.SMTP(self.mailserver, self.port)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self.username_loginmail, self.password_sendmail)

            success_recipients = []
            failed_recipients = []

            for recipient in recipients:
                try:
                    # 为每个收件人创建新的邮件实例
                    email = MIMEText(mail_content, 'plain', 'utf-8')
                    email['Subject'] = mail_subject
                    email['From'] = self.username_sendmail
                    email['To'] = recipient
                    
                    # 发送邮件
                    smtp.send_message(email)

                    # 记录成功状态
                    self.record_send_status(report, [recipient], True)
                    success_recipients.append(recipient)
                    logging.info(f"邮件发送成功 - Report ID: {report_id}, Recipient: {recipient}")

                except Exception as e:
                    error_message = str(e)
                    self.record_send_status(report, [recipient], False, error_message)
                    failed_recipients.append(recipient)
                    logging.error(f"邮件发送失败 - Report ID: {report_id}, Recipient: {recipient}, Error: {error_message}")

            # 关闭SMTP连接
            smtp.quit()

            # 汇总发送结果
            total_count = len(recipients)
            success_count = len(success_recipients)
            failed_count = len(failed_recipients)

            logging.info(f"""
            邮件发送完成 - Report ID: {report_id}
            总计收件人: {total_count}
            发送成功: {success_count}
            发送失败: {failed_count}
            成功列表: {success_recipients}
            失败列表: {failed_recipients}
            """)

            return success_count > 0

        except Report.DoesNotExist:
            error_message = f"Report with ID {report_id} does not exist"
            logging.error(error_message)
            return False

        except Exception as e:
            error_message = str(e)
            logging.error(f"邮件发送过程中发生错误 - Report ID: {report_id}, Error: {error_message}")
            return False