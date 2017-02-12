import RPi.GPIO as GPIO
# change these as desired - they're the pins connected from the
# SPI port on the ADC to the GPIO Pins on the Raspi

# MCP3008 to Raspi (PiCobbler) Pin connections
class PINS:
    SPICLK = 18
    SPIMISO = 23
    SPIMOSI = 24
    SPICS = 25
    PSON = 22

 # set up the SPI interface pins
def initialize():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(PINS.SPIMOSI, GPIO.OUT)
    GPIO.setup(PINS.SPIMISO, GPIO.IN)
    GPIO.setup(PINS.SPICLK, GPIO.OUT)
    GPIO.setup(PINS.SPICS, GPIO.OUT)
    GPIO.setup(PINS.PSON, GPIO.OUT)
    GPIO.output(PINS.PSON, False)

# Function to read data from Analog Pin 0 from MCP3008 (don't need to edit)
# This function will be called in our loop to get the current sensor value
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if ((adcnum > 7) or (adcnum < 0)):
            return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here
    for i in range(5):
            if (commandout & 0x80):
                    GPIO.output(mosipin, True)
            else:
                    GPIO.output(mosipin, False)
            commandout <<= 1
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)
            adcout <<= 1
            if (GPIO.input(misopin)):
                    adcout |= 0x1

    GPIO.output(cspin, True)

    adcout /= 2       # first bit is 'null' so drop it
    return adcout

def powerswitch_on():
    GPIO.output(PINS.PSON, True)

def powerswitch_off():
    GPIO.output(PINS.PSON, False)

def powerswitch_is_on():
    return GPIO.input(PINS.PSON)

def powerswitch_is_off():
    return not powerswitch_is_on()
