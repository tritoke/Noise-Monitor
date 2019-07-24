#!/usr/bin/env python3
from csv import reader
from datetime import datetime
from sys import argv
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import time


PREFIX = "/opt/noise-monitor"
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


def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w


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

# use this file as hacky mutex so email thing sends all the graphs and the csv at once
# just creates a file and we remove it after writing all the graphs
with open("finished", "w") as f:
pass

# save data to a csv file
print("saving raw data to a CSV")
with open(f"{PREFIX}/data.csv", "w", newline="") as f:
    datawriter = writer(f)
    data = zip(["Time"] + xs, ["Noise"] + ys)
    datawriter.writerows(data)


with open(f"{PREFIX}/data.csv", newline="") as f:
    data = np.array(list(reader(f))[1:],dtype="float64")
    xs,ys = data.transpose()

# graph data and save to a PNG
print("graphing data")

plt.plot(xs,ys)
plt.xlabel("Time")
plt.ylabel("Noise")
plt.ylim(0, 1)
plt.grid(True)

plt.savefig(f"{PREFIX}/graph.png")

# this clears the figure but not the axes as they don't change
plt.clf()

m_xs = moving_average(xs, 120)
m_ys = moving_average(ys, 120)

plt.plot(m_xs,m_ys)
plt.xlabel("Time")
plt.ylabel("Noise")
plt.ylim(0, 1)
plt.grid(True)

plt.savefig(f"{PREFIX}/moving.png")

os.remove(f"{PREFIX}/finished")
