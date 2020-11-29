
import codecs
import os
import sys
import threading

import serial
from serial.tools.list_ports import comports
from serial.tools import hexlify_codec

import time         # for sleep
from GS_Timing import millis, delay
from os import walk # directory listing
import math

from Transform import Transform


class LlamaVampireDrive( Transform ):
    """support for the vampire drive system"""
    # I know most of this is also copied in miniterm, but I wanted a full
    # version of the implementation here.

    def __init__(self):
        self.version = "PY-LLVD v1.00 2020-11-28"
        self.filepath = '../BASIC/'
        self.save_filename = 'saved.bas'
        self.msdelay = 10 # seems ok
        self.ioblocksize = 64

        self.capturing = False
        self.captureForSAVE = False
        self.save_fh = False
        self.accumulator = ''
        self.passthru = True
        self.activationkey = unichr( 0x10 ) # Vampire command CTRL+P
        self.shortname = 'LLVD'


        sys.stderr.write( "{} starting...\n".format( self.getVersion() ))
        sys.stderr.write( "LLVD: CTRL-P to interact.\n" )
        sys.stderr.flush()

    # --------------------------------------------

    def getVersion( self ):
        return "LlamaVampireDrive ({})".format( self.version )

    def getFilePath( self ):
        return self.filepath

    def setSaveFilename( self, filename ):
        if filename == "":
            return false

        self.save_filename = filename
        return filename

    # --------------------------------------------

    def endCapture( self ):
        self.save_fh.close()
        self.capturing = False
        print "\n\rLLVD: " + self.save_filename + ": Save comple."

    def internal_startCapture( self ):
        self.save_fh = open( self.getFilePath() + self.save_filename, 'w' )
        self.capturing = True

    def startCapture( self ):
        self.captureUntilOk = False
        self.internal_startCapture()
        print "\n\rLLVD: " + self.save_filename + ": Saving..."

    def startCaptureForSave( self ):
        self.captureForSAVE = True
        self.internal_startCapture()
        print "\n\rLLVD: " + self.save_filename + ": Saving until 'Ok'"

    # --------------------------------------------

    def echo(self, text):
        """text to be sent but displayed on console"""
        return text

    def rx(self, text):
        """text received from serial port"""

        # save to a file if we need to
        if self.capturing:
            # make sure we're doing this byte by byte..
            for ch in text:
                # re-accumulate it into lines:
                if ch in "\n\r":
                    # skip empty lines
                    if self.accumulator == "":
                        pass
                    else:
                        # do something with contented lines
                        if self.accumulator == 'Ok':
                            # on Ok, we're done.
                            self.endCapture()
                            return text # make sure we bail out of the loop.

                        elif self.accumulator == 'LIST':
                            # skip LIST lines
                            pass

                        else:
                            # write out the accumulator line
                            self.save_fh.write( self.accumulator )
                            self.save_fh.write( '\x0a' )

                    # and reset the accumulator
                    self.accumulator = ''

                else:
                    # just add it to the accumulator
                    self.accumulator = self.accumulator + ch

        # pass it on...
        if self.passthru:
            return text
        return ''

    def tx(self, text):
        """text to be sent to serial port"""
        #sys.stderr.write(' [TX:{}] '.format(repr(text)))
        #sys.stderr.flush()

        return text

    # --------------------------------------------


    def get_help_text(self):
            """return the vampire help text"""
            # help text, starts with blank line!
            return """
--- Vampire options:
---
---     ^Ph             display this help text (or ^P^H or ^PH etc)
---     ^P^P            send CTRL-P
---     ^Pd <int>       set per-char ms delay (10)
---     ^Pc             CATALOG of BASIC files
---     ^Pl <string>    LOAD from the specified filename
---     ^Ps <string>    SAVE to the specified filename
"""

    def progress_line( self, currval, topval ):
        # sanity check
        if topval == 0:
            topval = 0.01

        # textual output
        sys.stdout.write( '{:>5}/{:<5} {:>3}% '.format( currval, topval, 100*currval/topval))

        # graphical output
        bar_length = 30
        a = bar_length * currval/topval
        b = bar_length - a 
        sys.stdout.write( '[' + ('='*a) + '.'*b + ']\n\r' )


    # since we're in a mode where there's no echo, the usual getline
    # doesn't show echo while typing, so i wrote this one to handle it all.
    def my_getline( self, prompt='? ' ):
        CRLF = '\x0a\x0d'
        CR   = '\x0d'
        LF   = '\x0a'
        clearline = '\x1b[2K'   # ANSI/VT100 clear to end of line

        lineacc = ''
        while len( lineacc ) < 100:  # just in case.
            sys.stdout.write( CR + clearline + prompt + lineacc ) # backspace space

            x = sys.stdin.read( 1 )

            if x in '\x0a\x0d\x03\x1b': # NL, CR, ^C, ESC
                sys.stdout.write( CRLF )
                return lineacc

            if x in '\x08\x7f': # BS DEL
                lineacc = lineacc[:-1]
            else:
                lineacc = lineacc + x

        return lineacc



    def handle_user_command( self, c, theSerial ):
        print c

        if c in 'hH\x08':
            sys.stderr.write( self.get_vampire_help_text() )
            return False

        if c in 'pP\x10':
            # vampire character again -> send itself
            theSerial.write(self.tx_encoder.encode(c))
            if self.echo:
                self.console.write(c)
            return False

        if c in 'rR':
            print "LLVD: Reset"
            theSerial.flush()
            return False


        if c in 'cC\x03':
            # catalog
            print "LLVD: Catalog:"
            f = []
            for (dirpath, dirnames, filenames) in walk( self.getFilePath() ):
                #f.extend(filenames)
                break
            for fn in filenames:
                fs = os.stat( self.getFilePath() + fn ).st_size
                print "    {:>5}  {}".format( fs, fn )
            return False


        if c in 'Ll\x0c':
            filename = self.my_getline( "LLVD: Load file? " )
            if filename == "":
                print "LLVD: ERROR: No filename."
                return False
            
            fs = 0
            try:
                fs = os.stat( self.getFilePath() + filename ).st_size
            except OSError as e:
                sys.stderr.write('LLVD: ERROR {}: {} ---\n'.format(filename, e))
                return False

            total = 0
            print "LLVD: Loading {}".format( filename )
            try:
                with open( self.getFilePath() + filename, 'rb') as f:

                    self.progress_line( total, fs )

                    self.passthru = False
                    theSerial.write( "NEW\x0a\x0d" );
                    delay( 100 )

                    while True:
                        block = f.read( self.ioblocksize )
                        total = total + len(block)
                        if not block:
                            break

                        for idx in range(0, len(block)): 
                            theSerial.write( block[idx] )

                            # convert \n to \n\r
                            if block[idx] == '\x0a':
                                theSerial.write( '\x0d' )

                            delay( self.msdelay )

                        self.progress_line( total, fs )

                theSerial.write( '\x0a\x0d' )
                print '\nLLVD: Done.'
                self.passthru = True

            except IOError as e:
                sys.stderr.write('LLVD: ERROR {}: {} ---\n'.format(filename, e))
            return False


        if c in 'Ss':
            filename = ""
            while filename == "":
                filename = self.my_getline( "LLVD: Save file? " )

                if filename == "":
                    filename = self.save_filename
                else:
                    self.setSaveFilename( filename )

            print "Saving " + self.save_filename

            # actually save it
            theSerial.write( "\n\rLIST" );
            theSerial.flush();
            theSerial.write( "\n\r" );
            self.startCaptureForSave();
            return False

        if c in 'Dd':   # set millisecond-per-typed-char delay
            filename = self.my_getline( "LLVD: ms/char (0..1000)? " )

            if userline == "":
                print "No changes."
                return False
            try:
                thisMsDelay = int( userline )
                if thisMsDelay < 0 or thisMsDelay > 1000:
                    print "ERROR: {} is out of range (0..1000)".format( thisMsDelay )
                    return False
                print "set(ms, {})".format( thisMsDelay )
                self.msdelay = thisMsDelay
                return False

            except ValueError as e:
                print "LLVD: ERROR: {} is not a valid ms duration".format( userline )


        if c in '\x0a\x0d':
            return False

        print "LLVD: ERROR: Unknown char: {} {}".format( hex(ord(c)), c )


        # returning false returns control to terminal operations
        return False
