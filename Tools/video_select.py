#!/bin/python
#
#  Simple script to toggle some GPIOs -> relays -> video inputs
#  
#  GPIO 17 should be wired to the Video 1 relay
#  GPIO 27 should be wired to the Video 2 relay
#

import RPi.GPIO as GPIO
import time
import sys

select_v1 = 17
select_v2 = 27

whichVideo = 0

if len( sys.argv ) < 2:
	whichVideo = 0

if len( sys.argv ) >= 2:
	if sys.argv[1] == "1":
		whichVideo = 1
	elif sys.argv[1] == "2":
		whichVideo = 2
	else:
		whichVideo = 0

GPIO.setwarnings(False)
GPIO.setmode( GPIO.BCM )

#  Running this will...

# switch the pins to output mode...
GPIO.setup(select_v1, GPIO.OUT)
GPIO.setup(select_v2, GPIO.OUT)

# and set it low...
if( whichVideo == 1 ):
	print "Video 1"
	GPIO.output(select_v1,GPIO.HIGH)
	GPIO.output(select_v2,GPIO.LOW)
elif( whichVideo == 2 ):
	print "Video 2"
	GPIO.output(select_v1,GPIO.LOW)
	GPIO.output(select_v2,GPIO.HIGH)
else:
	print "Video Off"
	GPIO.output(select_v1,GPIO.LOW)
	GPIO.output(select_v2,GPIO.LOW)

# and finish it up!
#GPIO.cleanup()   # if we have cleanup() then it will reset the gpios.  we don't want that.
