import datetime
import os
import re
import requests
import schedule as schedule

import Tasks
from Tools import YanHuang, Forescout

from Tools.Mail import send_mail


if __name__ == '__main__':
    # YanHuang.Auth.login()
    # send_mail.send_mail(mail_content)
    Tasks.scheduleTake1()
    # schedule.every().day.at("00:15").do(Tasks.scheduleTake1)
    # while True:
    #     schedule.run_pending()
