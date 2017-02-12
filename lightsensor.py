import RPi.GPIO as GPIO

class Lightsensor(object):
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    @property
    def light(self):
        return GPIO.input(self.pin)
    
    @property
    def dark(self):
        return not self.light
