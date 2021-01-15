#!/bin/python
#
#  Simple script to toggle a GPIO line to reset the RC2014 
#  
# Tie GPIO12 directly to RC2014 backplane pin 20 (RESET)
#

import RPi.GPIO as GPIO
import time

rc_reset = 12

print "Resetting RC2014..."
GPIO.setmode( GPIO.BCM )

#  Running this will...

# switch the pin to output mode...
GPIO.setup(rc_reset,GPIO.OUT)

# and set it low...
GPIO.output(rc_reset,GPIO.LOW)

# for .2 seconds...
time.sleep(0.2)

# then restore it high
GPIO.output(rc_reset,GPIO.HIGH)

# return the gpio to an input (high-z presumably)
GPIO.setup(rc_reset, GPIO.IN )

# and finish it up!
GPIO.cleanup()
