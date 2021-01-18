#!/usr/bin/env python3
import glob
import time
import datetime
import numpy as np

# Current directory
import mailsend
from powerswitch import Powerswitch

# All temps in degrees F
MINTEMP = 37.5
MAXTEMP = 42.0
ALERTTEMP = 36.5

# temperature sensor middle pin connected channel 0 of mcp3008
PSPIN = 22  # Powerswitch pin

AVGINTERVAL = 60  # Interval for averaging of readings
MEANOUTFILE = "meantemps.out"
RAWOUTFILE = "rawtemps.out"

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[1]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    with open(device_file, 'r') as fh:
        lines = fh.readlines()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f

ps = Powerswitch(PSPIN)

rawoutfh = open(RAWOUTFILE, "a")
meanoutfh = open(MEANOUTFILE, "ab", 0)

cnt = 0
temps = []
msgqueue = []
lastmeantemp = None
tdir = u"\u2198"
minsincelastchg = 0
last30 = []  # Container to hold last 30 minutes
while True:
    cnt += 1

    tempF = read_temp()
    temps.append(tempF)

    curtime = datetime.datetime.now().isoformat().split('.')[0]
    rawoutfh.write(f"{curtime} {tempF:.2f}\n")

    if cnt % AVGINTERVAL != 0:
        print(f"secs={60 - cnt % 60:2d} cnt={cnt} "
              f"temp={tempF:.2f} switch:{ps.is_on}")
    else:
        print("Here!")

        meantemp = np.median(temps)

        last30.append(meantemp)
        if len(last30) > 30:
            last30.pop(0)

        rmean10ndx = min(len(last30), 10)
        rmean10 = np.mean(last30[-rmean10ndx:])

        if lastmeantemp is not None:
            if meantemp - lastmeantemp > 0:
                tdir = u"\u2197"
                minsincelastchg = 0
            elif meantemp - lastmeantemp < 0:
                tdir = u"\u2198"
                minsincelastchg = 0

        lastmeantemp = meantemp

        dline = bytes(f"{curtime} {meantemp:.2f} {tdir} ({minsincelastchg}) {rmean10:.2f}\n", "UTF-8")
        meanoutfh.write(dline)

        minsincelastchg += 1

        temps = []  # Reset

        if meantemp < ALERTTEMP:
            if ps.is_on:
                msgqueue.append(("*** Heater problem? ***",
                                 f"Temp dropped below {ALERTTEMP}!", False))
                ps.on()  # Try again
        elif meantemp < MINTEMP:
            if ps.is_off:
                msgqueue.append(("Turning on the heater",
                                 f"Temp dropped below {MINTEMP}", False))
                ps.on()
        elif meantemp > MAXTEMP:
            if ps.is_on:
                msgqueue.append(("Turning off the heater",
                                 f"Temp above {MAXTEMP}", False))
                ps.off()

        # Send any queued messages
        while len(msgqueue) > 0:
            subj, msg, alert = msgqueue.pop(0)
            try:
                mailsend.send(subj, msg, alert=alert)
                print("Mail sent!")
            except:
                print("Mail not sent!")

    # Set delay to get ~1 second between readings
    time.sleep(0.10)
