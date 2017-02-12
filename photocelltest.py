import time
import RPi.GPIO as io

io.setmode(io.BCM)

ldrpin = 17

io.setup(ldrpin, io.IN)

while True:
    print io.input(ldrpin)
    time.sleep(3);
