#!/usr/bin/env python

import json
import requests
from requests.auth import HTTPBasicAuth
import time
import datetime
import numpy as np

import readadc
import mailsend

# Set up light sensor
import RPi.GPIO as io
io.setmode(io.BCM)
ldrpin = 17
io.setup(ldrpin, io.IN)

MINTEMP = 39.0  # degrees F
MAXTEMP = 41.0  # degrees F
ALERTTEMP = 38.0  # degrees F

with open('./config.json') as config_file:
    plotlyuserconf = json.load(config_file)

headers = {'Plotly-Client-Platform': 'python'}
auth = HTTPBasicAuth(plotlyuserconf['plotly_username'],
                     plotlyuserconf['plotly_api_key'])

# temperature sensor middle pin connected channel 0 of mcp3008
sensor_pin = 0
readadc.initialize()

#mailsend.send('Starting tmp36.py', 'Starting now..')

#the main sensor reading and plotting loop
cnt = 0
temps = []
meantempdata = []

AVGINTERVAL = 60  # Interval for averaging of 1/sec readings

meanoutfile = 'meantemps.out'
rawoutfile = 'rawtemps.out'
respoutfile = 'response.out'

rawoutfh = open(rawoutfile, 'a')
meanoutfh = open(meanoutfile, 'a', 0)

msgqueue = []
failmsgsent = False
stuckmsgsent = False

def its_dark():
    return not io.input(ldrpin)

def its_light():
    return not its_dark()

while True:
    cnt += 1
    sensor_data = readadc.readadc(sensor_pin,
                                  readadc.PINS.SPICLK,
                                  readadc.PINS.SPIMOSI,
                                  readadc.PINS.SPIMISO,
                                  readadc.PINS.SPICS)

    millivolts = sensor_data * (3300.0 / 1024.0)
    # 10 mv per degree
    tempC = ((millivolts - 100.0) / 10.0) - 40.0
    # convert celsius to fahrenheit
    tempF = (tempC * 9.0 / 5.0) + 32
    temps.append(tempF)

    curtime = datetime.datetime.now().isoformat().split('.')[0]
    rawoutfh.write('{} {:.2f}\n'.format(curtime, tempF))

    # Calculate average and write the data to plotly
    if cnt % AVGINTERVAL != 0:
        print 'secs={:2d} cnt={} temp={:.2f} switch:{} light:{}'\
              .format(60 - cnt % 60, cnt, tempF, readadc.powerswitch_is_on(), io.input(ldrpin))
    else:
        print 'Here!'
        meantemp = np.mean(sorted(temps)[3:-3])
        #meantempdata.append([curtime, meantemp])

        meanoutfh.write('{} {:.2f}\n'.format(curtime, meantemp))

        temps = []

        if meantemp < ALERTTEMP:
            if readadc.powerswitch_is_on():
                msgqueue.append(('*** Bulb problem? ***',
                                 'Temp dropped below {}!'.format(ALERTTEMP, False)))
                readadc.powerswitch_on()
                time.sleep(1.0)  # Give the light time to come on
        elif meantemp < MINTEMP:
            if readadc.powerswitch_is_off():
                msgqueue.append(('Turning on the light',
                                 'Temp dropped below {}'.format(MINTEMP), False))
                readadc.powerswitch_on()
                stuckmsgsent = False  # Reset
                time.sleep(1.0)  # Give the light time to come on
        elif meantemp > MAXTEMP:
            if readadc.powerswitch_is_on():
                msgqueue.append(('Turning off the light',
                                 'Temp above {}'.format(MAXTEMP), False))
                readadc.powerswitch_off()
                failmsgsent = False  # Reset
                time.sleep(4.0)  # Give the light time to dim

        # Check to make sure the light is really on if it's supposed to be
        if readadc.powerswitch_is_on() and its_dark():
            if failmsgsent is False:
                subj, msg = ('*** Bulb failure? ***',
                             "The powerswitch is on but it's dark down here!")
                msgqueue.append((subj, msg, False))  # email
                msgqueue.append((subj, msg, True))  # text
            failmsgsent = True

        # Check to make sure the light is really off if it's supposed to be
        if readadc.powerswitch_is_off() and its_light():
            if stuckmsgsent is False:
                subj, msg = ('*** Switch stuck? ***',
                             "The powerswitch is off but it's light down here!")
                msgqueue.append((subj, msg, False))  # email
                msgqueue.append((subj, msg, True))  # text
            stuckmsgsent = True

        # Send any queued messages
        while len(msgqueue) > 0:
            subj, msg, alert = msgqueue[0]
            
            try:
                mailsend.send(subj, msg, alert=alert)
                msgqueue.pop(0)
            except:
                pass

        #if cnt % (15 * AVGINTERVAL) == 0:
        #if cnt % (1 * AVGINTERVAL) == 0:
        #    print 'Here2!'
        #    rowdata = []
        #    for ctime, mtemp in meantempdata:
        #        rowdata.append([ctime, mtemp])

        #    rows = {"rows": rowdata}
        #    print 'rows', rows
        #        
        #    try:
        #        r = requests.post('https://api.plot.ly/v2/grids/subnivean:21/row',
        #                           auth=auth, headers=headers, json=rows)
        #        print 'response:', r.__dict__
        #        if r.status_code != 429:
        #            print 'Data uploaded (?)'
        #            meantempdata = []
        #        else:
        #            print 'Too many requests!'

        #        #meanoutfh.write('{}\n\n'.format(str(r)))

        #    except:
        #        print 'Request failed...'

    # delay between stream posts
    time.sleep(1.0)
