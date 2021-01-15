# simple makefile to help dev on this project
# usually, you'd just run 'llvdrvterm.py' and select your serial port
# a la:  make run
#
# by default 'miniterm' ran at 9600 baud, but i changed it to 
# be 115200 so that it would not be necessary to set it on the cmd line

PORTNAME := $(shell python ../Tools/find_usb_serial.py --best)

all:	dev
.PHONY: all

dev:
ifeq '$(PORTNAME)' 'NONE'
	@echo "Unable to detect USB serial device."
else
	@echo "Autodetected: $(PORTNAME)"
	python llvdrvterm.py $(PORTNAME) 115200
endif
.PHONY: dev

sane:
	python miniterm.py $(PORTNAME) 115200
.PHONY: sane

run:
	python $(PORTNAME) - 115200
.PHONY: run

