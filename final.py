from csv import writer
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from sys import argv
import matplotlib.pyplot as plt
import numpy as np
import smtplib
import sounddevice as sd
import time


SAMPLERATE = 44100


def sound_max(seconds):
    """
    This function generates data points for the graph.
    It returns the maximum value of the sound-data which
    is recorded in the ten second period following the
    function call.
    """
    myrecording = sd.rec(seconds * SAMPLERATE, samplerate=SAMPLERATE, channels=1)
    sd.wait(seconds)
    mx = np.max(myrecording)
    return mx


# parse command line arguments
if len(argv) < 2 or len(argv) > 3:  # print usage
    print(f"Usage: {argv[0]} <end hour> <end minute>")
    print("specifying end minute is optional however end hour must be specified")
    exit(1)
elif len(argv) == 2:  # only hour specified
    end_hour, end_minute = int(argv[1]), 0
else:  # hour and minute specified
    end_hour, end_minute = map(int, argv[1:3])


# gather data
xs, ys = [], []

print(f"Gathering data until {end_hour:02d}:{end_minute:02d}")

while datetime.now().hour < end_hour or datetime.now().minute < end_minute:
    # Get maximum sound in 10 seconds
    data_point = sound_max(10)
    # Compute t as time as fractions of an hour
    now = datetime.now()
    t = now.hour + (now.minute / 60) + (now.second / 3600)
    xs.append(t)
    ys.append(data_point)
    print(f"{t}: {data_point}")


# graph data and save to a PNG
print("graphing data")

plt.plot(xs, ys)
plt.xlabel("time")
plt.ylabel("max points")
plt.ylim(0, 1)
plt.grid(True)

plt.savefig("/tmp/graph.png")


# save data to a csv file
print("saving raw data to a CSV")
with open("/tmp/data.csv", "w", newline="") as f:
    datawriter = writer(f)
    data = zip(["Time"] + xs, ["Noise"] + ys)
    datawriter.writerows(data)


# send email to google group
print("Sending email to google group")
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
files = ["/tmp/graph.png", "/tmp/data.csv"]
for f in files:
    with open(f, "rb") as attachment:
        part = MIMEApplication(attachment.read(), Name=f)

    part["Content-Disposition"] = f"attachment; filename={f}"
    msg.attach(part)

s.sendmail(username, sendto, msg.as_string())
s.quit()
