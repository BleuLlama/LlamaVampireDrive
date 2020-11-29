# simple makefile to help dev on this project
# usually, you'd just run 'llvdrvterm.py' and select your serial port
# a la:  make run
#
# by default 'miniterm' ran at 9600 baud, but i changed it to 
# be 115200 so that it would not be necessary to set it on the cmd line

all:	dev
.PHONY: all

dev:
	python llvdrvterm.py /dev/cu.usbmodem01871 115200
.PHONY: dev

sane:
	python miniterm.py /dev/cu.usbmodem01871 115200
.PHONY: sane


run:
	python llvdrvterm.py - 115200
.PHONY: run

