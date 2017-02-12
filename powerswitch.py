import RPi.GPIO as GPIO

class Powerswitch(object):
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, False)

    def on(self):
        GPIO.output(self.pin, True)
    
    def off(self):
        GPIO.output(self.pin, False)
    
    @property
    def is_on(self):
        return bool(GPIO.input(self.pin))
    
    @property
    def is_off(self):
        return not self.is_on
