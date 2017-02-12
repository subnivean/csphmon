#!/usr/bin/env python

import RPi.GPIO as io

io.setmode(io.BCM)

powerpin = 22

io.setup(powerpin, io.OUT)
io.output(powerpin, False)
