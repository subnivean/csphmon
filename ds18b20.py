#!/usr/bin/env python3
import glob
import time
import datetime
import numpy as np
from w1thermsensor import W1ThermSensor, SensorNotReadyError

# Current directory
import mailsend
from powerswitch import Powerswitch

# All temps in degrees F
MINTEMP = 36.0
MAXTEMP = 39.0
ALERTTEMP = 35.5
THERMOOFFSET = 0.7
DEGREESF = 'fahrenheit'

# temperature sensor middle pin connected channel 0 of mcp3008
PSPIN = 22  # Powerswitch pin

AVGINTERVAL = 15  # Interval for averaging of readings
MEANOUTFILE = "meantemps.out"
# RAWOUTFILE = "rawtemps.out"

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

ps = Powerswitch(PSPIN)
sensor = W1ThermSensor(offset=THERMOOFFSET, offset_unit=DEGREESF)

# rawoutfh = open(RAWOUTFILE, "a")
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

    try:
        tempF = sensor.get_temperature(unit=DEGREESF)
    except SensorNotReadyError:
        print("Waiting for sensor to become ready...")
        time.sleep(15)
        continue

    temps.append(tempF)

    curtime = datetime.datetime.now().isoformat().split('.')[0]
    # rawoutfh.write(f"{curtime} {tempF:.2f}\n")

    if cnt % AVGINTERVAL != 0:
        print(f"secs={AVGINTERVAL - cnt % AVGINTERVAL:2d} cnt={cnt} "
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
    time.sleep((60 / AVGINTERVAL) - 1 + 0.121)
