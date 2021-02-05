#!/bin/python
#
#  gpio_shutdown.py
#
#   Adapated and completely changed by
#   Scott Lawrence
#   yorgle@gmail.com
#
# Shut down the Raspi cleanly when a GPIO line is held to ground
# Hook up a button directly betweem GPIO 20 and ground.
#
#  Press the button for 2-5 seconds to shut down.
#  If you hold it for more than 5 seconds it cancels
#  the action.
#
#  Hook up an LED from pin 21 through a resistor to ground as
# feedback for the process. 

#  The light is on when the script is run, which acts like 
# a second indicator that the machine has booted and is ready.
#  When you press the button down, the light will go off.
#  When you release it and it blinks, it will shut down the computer.
#  While pressing it, if the light comes back on, the shutdown
#  request is cancelled.  I call this the "oops" feature.
#  The light will come back on after the press
#  If the Pi is shutting down, it will remail lit until it is 
#  safe to remove power from the Pi.
#
#  To install,
#  sudo vi /etc/rc.local
#  and add this line: (change appropriately)
#    python /home/pi/Tools/gpio_shutdown.py &



import RPi.GPIO as GPIO
import time
import os

# Version History
#  1.0 - 2021-01-14 - initial completed version for my RC2014

# The gpio line the LED is connected to
led = 21

# The gpio line the button is connected to
button = 20


def Shutdown(channel):
    start_time = time.time()
    GPIO.output(led,GPIO.LOW)
    ledIs = 0

    # just ignore the first .2 sec (cheapo-debounce)
    while time.time() - start_time < 0.2:
        pass

    state = "idle"
    
    # Button is pressed...
    while GPIO.input( button ) == 0:
	# while the button is pressed
        duration = time.time() - start_time

	# after 5 seconds, it's cancel time, light off
        if duration > 5.0 and ledIs == 1:
            # cancel time
            GPIO.output(led,GPIO.LOW)
            ledIs = 0
            state = "cancel"

	# after 1 second, it's valid reboot time.  light on
	elif duration > 1.0 and ledIs == 0:
	    GPIO.output(led,GPIO.HIGH)
	    ledIs = 1
            state = "action"

        pass

    GPIO.output(led,GPIO.HIGH)
    duration = time.time() - start_time
    if state == "action":
        flash( 0.1 )
        os.system("sync")
        os.system("shutdown -h now")


def flash( dv ):
    GPIO.output( led,GPIO.LOW)
    time.sleep( dv )
    GPIO.output( led,GPIO.HIGH)
    time.sleep( dv )
    GPIO.output( led,GPIO.LOW)
    time.sleep( dv )
    GPIO.output( led,GPIO.HIGH)
    
    
GPIO.setmode( GPIO.BCM )

GPIO.setup(button, GPIO.IN, pull_up_down = GPIO.PUD_UP)

GPIO.setup(led,GPIO.OUT)
GPIO.output(led,GPIO.HIGH)

# Add our function to execute when the button pressed event happens
GPIO.add_event_detect(button, GPIO.FALLING, callback = Shutdown, bouncetime = 1000)

try:
    # Now wait!
    while 1:
        time.sleep(1)

except:
    pass

finally:
    print "exiting..."
    GPIO.cleanup()


