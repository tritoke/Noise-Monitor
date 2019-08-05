#!/usr/bin/env python3
from csv import reader, writer
from datetime import datetime
from sys import argv
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import time

PREFIX = "/opt/noise-monitor"
SAMPLERATE = 44100


def get_data(seconds):
    """
    This function gets the necessary data over a ten second period.
    This includes a ten second average and a maximum over the ten seconds.
    returns a tuple: (current time in hours since dawn (float),
                      ten second average (float),
                      ten second maximum (float))
    """
    # get sound data
    myrecording = sd.rec(seconds * SAMPLERATE, samplerate=SAMPLERATE, channels=1)
    sd.wait(seconds)

    # compute fractional hours
    now = datetime.now()
    t = now.hour + (now.minute / 60) + (now.second / 3600)

    # compute mean and max
    mx = np.max(myrecording)
    avg = np.mean(myrecording)

    return (t, avg, mx)


def moving_average(x, w):
    return np.convolve(x, np.ones(w, dtype="double"), "valid") / w


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
data = []

print(f"Gathering data until {end_hour:02d}:{end_minute:02d}")
while datetime.now().hour < end_hour or datetime.now().minute < end_minute:
    # Get maximum sound in 10 seconds
    data.append(get_data(10))
    # Compute t as time as fractions of an hour
    print(f"{data[-1][0]}: {data[-1][1:]}")

# save data to a csv file
print("saving raw data to a CSV")
with open(f"{PREFIX}/data.csv", "w", newline="") as f:
    datawriter = writer(f)
    annotated = [("Time", "Mean", "Max")] + data
    datawriter.writerows(data)


# graph data and save to a PNG
print("graphing data")


times, means, maxes = np.array(data, "double").transpose()

today = datetime.strftime(datetime.now(), "%d/%m/%y")

plt.title(f"Graph of Maximums for {today}")
plt.plot(times, maxes)
plt.xlabel("Time")
plt.ylabel("Noise")
plt.ylim(0, 1)
plt.grid(True)

plt.savefig(f"{PREFIX}/maximum-graph.png")

# clear plot
plt.clf()

plt.title(f"Graph of 10 second averages for {today}")
plt.plot(times, means)
plt.xlabel("Time")
plt.ylabel("Noise")
plt.ylim(0, 1)
plt.grid(True)

plt.savefig(f"{PREFIX}/average-10.png")

# clear plot
plt.clf()

moving_time = moving_average(times, 3)
moving_mean = moving_average(means, 3)

plt.title(f"Graph of 30 second moving average for {today}")
plt.plot(moving_time, moving_mean)
plt.xlabel("Time")
plt.ylabel("Noise")
plt.ylim(0, 1)
plt.grid(True)

plt.savefig(f"{PREFIX}/average-30.png")


# create an empty file called finished so that the emailer
# knows it is clear to send the email with all the images
open(f"{PREFIX}/finished", "w").close()
