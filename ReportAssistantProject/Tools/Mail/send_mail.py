import smtplib
from email.mime.text import MIMEText

mailserver = "mail.stec-cn.com"
username_loginmail = "hanjie.hu"
username_sendmail = "hanjie.hu@stec-cn.com"
password_sendmail = "************"
received_mail = "lan.yu@charleslink.com,daren@charleslink.com,hanjie.hu@stec-cn.com"
# received_mail = "hanjie.hu@stec-cn.com,hanjie.hu@stec-cn.com"
# mail_subject = "test"

def send_mail(mail_subject, mail_content):
    email = MIMEText(mail_content, 'plain', 'utf-8')
    email['Subject'] = mail_subject
    email['From'] = username_sendmail
    email['To'] = received_mail

    try:
        smtp = smtplib.SMTP(mailserver, 25)
        smtp.starttls()
        smtp.login(username_loginmail, password_sendmail)
        smtp.sendmail(username_sendmail, received_mail.split(','), email.as_string())
        smtp.quit()
        print("邮件发送成功")
    except Exception as e:
        print("邮件发送失败")
        print(e)
