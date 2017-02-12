#!/usr/bin/python
import smtplib

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USERNAME = 'mark.krautheim@gmail.com'
GMAIL_PASSWORD = 'joyxoadmsnfevxri' #CAUTION: This is stored in plain text!
VTEXTADDR = '8029891055@vtext.com'
EMAILADDR='mark.krautheim@gmail.com'

def send(subject, emailtext, alert=False):
    
    if alert is False:
        recipient = EMAILADDR
    else:
        recipient = VTEXTADDR

    headers = ["From: " + GMAIL_USERNAME,
               "Subject: " + subject,
               "To: " + recipient,
               "MIME-Version: 1.0",
               "Content-Type: text/html"]
    headers = "\r\n".join(headers)
    
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    
    session.ehlo()
    session.starttls()
    session.ehlo
    
    session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
    
    session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + emailtext)
    session.quit()
