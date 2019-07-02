#!/usr/bin/env python3.5
import smtplib as s
import ssl
from datetime import timedelta
gmail_usr = "starbucksautoma@gmail.com"
gmail_passwd = "p@$$W0rD!##"

me = "jared.dyreson@gmail.com"

def get_sys_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(timedelta(seconds = uptime_seconds))
    return uptime_string
def createEmailBody(content, sender=gmail_usr, reciever=me):
    subjects = ['Event has changed', 'Events have not changed', 'New scrape completed']
    subject = "Work report"
    body = """
    From: {}
    To: {}
    Subject: {}
    {}
    Bleep bloop, I am a bot!
    """.format(gmail_usr, me, subject, content)
    return body

def send_email(message):
    try:
        port = 465
        context = ssl.create_default_context()
        with s.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(gmail_usr, gmail_passwd)
            message = createEmailBody(message)
            server.sendmail(gmail_usr, me, message)
    except Exception as e:
        # make sure the account has "Less secure app access enabled in GMAIL settings"
        print("[-] Could not validate credentials")
        print("[-] Detailed erorr: {}".format(e))
