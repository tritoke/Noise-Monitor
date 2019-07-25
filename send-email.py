#!/usr/bin/env python3
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
import os
import smtplib
from time import sleep

PREFIX = "/opt/noise-monitor"


if os.path.isfile(f"{PREFIX}/finished"):
    exit()

files = [
    f"{PREFIX}/{i}"
    for i in os.listdir(PREFIX)
    if i.endswith(".png") or i.endswith(".csv")
]
if files == []:
    exit()

while True:
    prev_files = files
    sleep(30)
    files = [
        f"{PREFIX}/{i}"
        for i in os.listdir(PREFIX)
        if i.endswith(".png") or i.endswith(".csv")
    ]
    if files == prev_files:
        break

# send email to google group

s = smtplib.SMTP("smtp.gmail.com", 587)
s.starttls()
s.ehlo()

username = "noisemonitor123@gmail.com"
password = "NoiseMonitor123"
s.login(username, password)

sendto = ["noisemonitor@googlegroups.com"]

msg = MIMEMultipart()
msg["From"] = username
msg["To"] = sendto[0]
msg["Date"] = formatdate(localtime=True)

current_date = datetime.strftime(datetime.now(), "%d/%m/%Y")
msg["Subject"] = f"Graph for {current_date}"

# add attachments

for f in files:
    with open(f, "rb") as attachment:
        part = MIMEApplication(attachment.read(), Name=f)

    part["Content-Disposition"] = f"attachment; filename={f}"
    msg.attach(part)

s.sendmail(username, sendto, msg.as_string())
s.quit()
