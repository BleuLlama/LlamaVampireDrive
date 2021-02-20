#!/bin/python
#
#  Simple script to toggle some GPIOs -> relays -> video inputs
#  
#  Video 0 is the composite of the RC2014 and should be wired directly
#  to the outputs
#
#  Composite: RC2014 internal video
#  Aux 1: GPIO 17 should be wired to the Video 1 relay
#  Aux 2: GPIO 27 should be wired to the Video 2 relay
#

import RPi.GPIO as GPIO
import time
import os
import sys

gpio_aux1 = 17
gpio_aux2 = 27

whichVideo = 0

# raspi composite video switching
def Composite_Off():
	os.system('tvservice -o >/dev/null')

def Composite_On():
	os.system('tvservice --sdtvon="NTSC 4:3" > /dev/null')
	os.system('fbset --all -g 320 240 320 240 32 > /dev/null')

# which inputs are to be enabled
c_enable = False
a1_enable = False
a2_enable = False

# no input? turn everything off! 
if len( sys.argv ) < 2:
	opt = 0
else :
	opt = sys.argv[1].lower()

if   opt=='1' or opt=='c' or opt=='composite' or opt=='raspi':
	c_enable = True
elif opt=='2' or opt=='aux2':
	a1_enable = True
elif opt=='3' or opt=='aux3':
	a2_enable = True
# anything else will turn everything off.

# configure GPIO...
GPIO.setwarnings(False)
GPIO.setmode( GPIO.BCM )

# switch the pins to output mode...
GPIO.setup(gpio_aux1, GPIO.OUT)
GPIO.setup(gpio_aux2, GPIO.OUT)

# and enable the necessary inputs!
if( c_enable ):
	Composite_On()
else:
	Composite_Off()

if( a1_enable ): 
	GPIO.output(gpio_aux1,GPIO.HIGH)
else:
	GPIO.output(gpio_aux1,GPIO.LOW)

if( a2_enable ): 
	GPIO.output(gpio_aux2,GPIO.HIGH)
else:
	GPIO.output(gpio_aux2,GPIO.LOW)



# and finish it up!
#GPIO.cleanup()   # if we have cleanup() then it will reset the gpios.  we don't want that.
