#!/bin/python
#
#  Simple script to toggle some GPIOs -> relays -> video inputs
#  
#  GPIO 5 should be wired to the Video 0 relay
#  GPIO 6 should be wired to the Video 1 relay
#

import RPi.GPIO as GPIO
import time
import sys

select_v0 = 5
select_v1 = 61`

whichVideo = 0

if len( sys.argv ) < 2:
	whichVideo = 0

if len( sys.argv ) >= 2:
	if sys.argv[1] == "1":
		whichVideo = 1


print "Video {}".format( whichVideo )

GPIO.setwarnings(False)
GPIO.setmode( GPIO.BCM )

#  Running this will...

# switch the pins to output mode...
GPIO.setup(select_v0, GPIO.OUT)
GPIO.setup(select_v1, GPIO.OUT)

# and set it low...
if( whichVideo == 0 ):
	print "V0"
	GPIO.output(select_v0,GPIO.HIGH)
	GPIO.output(select_v1,GPIO.LOW)
else:
	print "V1"
	GPIO.output(select_v0,GPIO.LOW)
	GPIO.output(select_v1,GPIO.HIGH)

# and finish it up!
#GPIO.cleanup()   # if we have cleanup() then it will reset the gpios.  we don't want that.
