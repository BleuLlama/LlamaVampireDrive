#!/bin/python
#
# Simple script to test the LED

import RPi.GPIO as GPIO
import time

# The gpio line the LED is connected to
led = 21

GPIO.setwarnings( False )
GPIO.setmode( GPIO.BCM )
GPIO.setup( led,GPIO.OUT )

def flash( nt, dv ):
	while nt > 0:
	    GPIO.output( led,GPIO.LOW )
	    time.sleep( dv )
	    GPIO.output( led,GPIO.HIGH )
	    time.sleep( dv )
	    nt -= 1

flash( 3, .1 )
