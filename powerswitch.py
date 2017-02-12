import time
import RPi.GPIO as io

io.setmode(io.BCM)

ldrpin = 17
powerpin = 22

io.setup(powerpin, io.OUT)
io.setup(ldrpin, io.IN)

io.output(powerpin, False)

io.output(powerpin, True)

#while True:
while False:
    if not io.input(ldrpin):
        print("POWER ON")
        io.output(powerpin, True)
    else:
        print("POWER OFF")
        io.output(powerpin, False)
    time.sleep(2.0)
