#!/usr/bin/env python
#
#	find_usb_serial
#
#		yorgle@gmail.com
#
# simple tool to scan the list of available serial ports 
# and make an educated guess as to which is a connected
# usb serial or arduino.
#
# this requires pySerial
#
#  v1.02 - 2020-01-15 - AMAswap - created for raspi usage
#  v1.01 - 2021-01-08 - Possibilities list is now priority based
#  v1.00 - 2020-12-02 - initial version copied from another project
#

import serial
from serial.tools.list_ports import comports

class FindSerial(object):
	"""\
	All of the functions on top of PySerial
	to find a potential arduino or usb serial device
	"""

	def __init__( self, args ):
		self.possibilities = [ 'arduino', 'usbserial', 'usbmodem', 'ch340', 'wchusb', 'hc06', 'ttyS', 'ttyAM' ]

		self.options = args
		if self.options.best:
			self.options.ardy = True

	def couldBeArduino( self, trycomport ):
		for needle in self.possibilities:
			if needle.lower() in trycomport.description.lower():
				return True
			if needle.lower() in trycomport.device.lower():
				return True
		# nope
		return False

	def comPortContains( self, trycomport, needle ):
		if needle.lower() in trycomport.description.lower():
			return True
		if needle.lower() in trycomport.device.lower():
			return True
		return False


	# not used currently
	def detectArduinoPort( self, usrsearch ):
		theArduino = None;

		if self.simulation is True:
			return SimCom   # it is the port and the sim.
		
		ports = list(serial.tools.list_ports.comports())

		for tryComPort in ports:
			if usrsearch is None:
				# only check the builtins
				if self.couldBeArduino( tryComPort ):
					#print "Arduino on " + p.device
					theArduino = tryComPort
			else:
				# only check the usrsearch
				if usrsearch in tryComPort.description:
					#print "Requested port found on " + p.device
					theArduino = tryComPort

				if usrsearch in tryComPort.device:
					#print "Requested port found on " + p.device
					theArduino = tryComPort
		return theArduino;

	def listSerialPorts( self ):
		ports = list(serial.tools.list_ports.comports())
		count = 0

		if self.options.human:
			print "Detected serial ports:"

		for q in self.possibilities:
			if self.options.best == True and count > 0:
				continue

			for p in ports:
                                p.device = self.amaswap( p.device )
                                p.description = self.amaswap( p.description )

				if self.comPortContains( p, q ):
					count = count + 1

					if self.options.human:
						print "   " + p.device + " -- " + p.description
					else:
						print p.device


		if count == 0:
			if( self.options.human ):
				print "No ports found."
			else:
				print "NONE"

        def amaswap( self, txt ):
            if not self.options.amaswitch:
                return txt

            txt = txt.replace( "AMA", "S" )

            return txt

	def listSerialPorts_old( self ):
		ports = list(serial.tools.list_ports.comports())
		count = 0

		if self.options.human:
			print "Detected serial ports:"

		# TODO: rearrange this to be via the order preferred in self.possibilities

		#  For each self.possibilities
		#		for p in ports
		#			if matches, print.
		for p in ports:
			additional = ""
			if( not self.options.ardy or self.couldBeArduino( p ) ):

				# show the result
				if self.options.best == True and count > 0:
					#print "Skipped {}".format( count )
					continue

				if self.options.human:
					print "   " + p.device + " -- " + p.description
				else:
					print p.device

				count = count + 1


		if count == 0:
			if( self.options.human ):
				print "No ports found."
			else:
				print "NONE"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# default args can be used to override when calling main() from an other script
# e.g to create a miniterm-my-device.py
def main():
	"""Command line tool, entry point"""

	import argparse

	parser = argparse.ArgumentParser(
		description="find_usb_serial - A simple terminal program to find a serial port.")

	parser.add_argument(
		"--human",
		action="store_true",
		help="Show a human printable listing",
		default=False)

	parser.add_argument(
		"--best",
		action="store_true",
		help="Show ONLY the most likely option (sets --ardy true too)",
		default=False)

	parser.add_argument(
		"--amaswitch",
		action="store_true",
		help="switch ttyAMAx to ttySx.",
		default=True)

	parser.add_argument(
		"--ardy",
		action="store_true",
		help="Show only potential arduinos.",
		default=False)

	args = parser.parse_args()

	fs = FindSerial( args )
	fs.listSerialPorts()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
	main()
