# LlamaVampireDrive
#
#   offers file IO to a console-based connection
#   Python version, using hacked miniterm.py
#
#   Scott Lawrence - yorgle@gmail.com
#
#   1.01 2020-11-30     Textfile commands (capture, type)
#   1.00 2020-11-28     Initial version, BASIC commands
#

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
        self.version = "PY-LLVD v1.01 2020-11-30"

        self.filepath = 'FS/BASIC/'

        self.basic_filename = 'SAVED.BAS'
        self.captureForSAVE = False
        self.save_fh = False

        self.capture_filename = 'CAPTURE.TXT'
        self.captureToFile = False
        self.file_fh = False

        self.msdelay = 10 # seems ok
        self.ioblocksize = 64
        self.quietmode = False
        self.accumulator = ''
        self.passthru = True
        self.activationkey = unichr( 0x10 ) # Vampire command CTRL+P
        self.qprompt = 'V? '
        self.prompt = 'V> '


        self.userprint( "{} starting...".format( self.getVersion() ))
        self.userprint( "CTRL-P to interact." )


    # --------------------------------------------

    def echo(self, text):
        """text to be sent but displayed on console"""
        return text

    def rx(self, text):
        """text received from serial port"""

        if self.captureToFile:
            self.file_fh.write( text )

        # save to a file if we need to
        if self.captureForSAVE:
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
                            self.endCaptureForSave()
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
        if self.passthru and not self.quietmode:
            return text
        return ''

    def tx(self, text):
        """text to be sent to serial port"""
        #sys.stderr.write(' [TX:{}] '.format(repr(text)))
        #sys.stderr.flush()

        # don't capture stuff the user sends. leave this commented out.
        #if self.captureToFile:
        #    self.file_fh.write( text )

        return text


    # --------------------------------------------

    def userprint( self, txt ):
        sys.stdout.write( self.prompt + txt + "\n" )
        sys.stdout.flush()

    def usererror( self, txt ):
        sys.stdout.write( self.prompt + "ERROR: " + txt + "\n" )
        sys.stdout.flush()

    def getVersion( self ):
        return "LlamaVampireDrive ({})".format( self.version )

    def getFilePath( self ):
        return self.filepath

    def setFilename( self, filename ):
        if filename == "":
            return false
        self.basic_filename = filename
        return filename

    # --------------------------------------------

    # capture to file
    def startTextCapture( self, filename ):
        self.file_fh = open( self.getFilePath() + filename, 'w' )
        self.captureToFile = True
        self.userprint( filename + ": Capturing." )

    def endTextCapture( self ):
        self.captureToFile = False
        self.file_fh.close()
        self.userprint( self.capture_filename + ": Capture ended." )


    # capture for BASIC SAVE

    def startCaptureForSave( self, filename ):
        self.save_fh = open( self.getFilePath() + filename, 'w' )
        self.captureForSAVE = True
        self.userprint( filename + ": Saving until 'Ok'" )

    def endCaptureForSave( self ):
        self.captureForSAVE = False
        self.save_fh.close()
        self.userprint( self.basic_filename + ": Save complete." )


    # --------------------------------------------


    def get_help_text(self):
            """return the vampire help text"""
            # help text, starts with blank line!
            return """Vampire "CTRL-P" commands:

  BASIC commands:   (Default file: SAVED.BAS)
    ^Pc                 (C)ATALOG of BASIC files
    ^Pl<filename><CR>   (L)OAD from the specified filename
    ^Ps<filename><CR>   (S)AVE to the specified filename

  Textfile commands: (Default file: CAPTURE.TXT)
    ^Pt<filename><CR>   (T)ype content from a file to the target
    ^Pf<filename><CR>   capture all IO to a (f)ile..
    ^Px                 ..and E(x)it capture to the file

  Utility commands:
    ^Pb                 (b)oot - LOAD and RUN the program BOOT.BAS
    ^Ph                 Display this (h)elp text (or ^P^H or ^PH etc)
    ^P^P                Send CTRL-P
    ^Pd<int><CR>        Set per-char (d)elay in milliseconds
    ^Pd<CR>             Show per-char (d)elay in milliseconds
    ^Pq                 Toggle (q)uiet IO mode
    ^Pv                 Display (v)ersion"""

    # progress_line
    #   utility function to display a progress bar to the terminal
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


    # cmd_TypeToTarget
    #   send the specified text file to the target
    def cmd_TypeToTarget( self, filename, theSerial ):
        fs = 0
        try:
            fs = os.stat( self.getFilePath() + filename ).st_size
        except OSError as e:
            self.usererror( "{}: {} ---\n".format(filename, e) )
            return False

        total = 0
        self.userprint( "Typing {} ({} bytes)".format( filename, fs ) )
        try:
            with open( self.getFilePath() + filename, 'rb') as f:
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

                    sys.stdout.write( "\n\r" )
                    self.progress_line( total, fs )

        except IOError as e:
            self.usererror( "{}: {} ---\n".format(filename, e))
        return False


    # cmd_BASIC_Catalog
    #   Send a file listing of the current file path to the terminal
    def cmd_BASIC_Catalog( self ):
        f = []
        for (dirpath, dirnames, filenames) in walk( self.getFilePath() ):
            #f.extend(filenames)
            break
        for fn in filenames:
            fs = os.stat( self.getFilePath() + fn ).st_size
            print "    {:>5}  {}".format( fs, fn )


    # cmd_BASIC_Load
    #   pretty much the same thing, but it inhibits echo, and types "NEW" first
    def cmd_BASIC_Load( self, filename, theSerial ):
        fs = 0
        try:
            fs = os.stat( self.getFilePath() + filename ).st_size
        except OSError as e:
            self.usererror( "{}: {} ---\n".format(filename, e) )
            return False

        total = 0
        self.userprint( "Loading {}".format( filename ) )
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
            self.userprint( "Done." )
            self.passthru = True

        except IOError as e:
            self.usererror( "{}: {} ---\n".format(filename, e))
        return False

    # cmd_Boot
    #   load BOOT.BAS and RUN it.
    def cmd_Boot(self, theSerial):
        self.cmd_BASIC_Load( "BOOT.BAS", theSerial )
        theSerial.write( 'RUN\x0a\x0d' )

    # cmd_Reset
    #   do whatever's necessary to reset the target (gpio toggle, etc)
    def cmd_Reset(self, theSerial):
        self.userprint( "Reset" )
        theSerial.flush()

    # handle_user_command
    #   handle input from the user terminal while in LLVD mode
    def handle_user_command( self, c, theSerial ):
        print c

        # Utility Commands
        if c in 'vV':
            self.userprint( self.version )
            return False

        if c in 'hH?\x08':
            self.userprint( self.get_help_text() )
            return False

        if c in 'pP\x10':
            # vampire character again -> send itself
            theSerial.write(self.tx_encoder.encode(c))
            if self.echo:
                self.console.write(c)
            return False

        if c in 'Dd':   # set millisecond-per-typed-char delay
            userline = self.my_getline( self.prompt + "ms/char (0..1000)? " )

            if userline != "":
                try:
                    thisMsDelay = int( userline )
                    if thisMsDelay < 0 or thisMsDelay > 1000:
                        self.usererror( "{} is out of range (0..1000)".format( thisMsDelay ))
                    else:
                        self.userprint( "set(ms, {})".format( thisMsDelay ))
                        self.msdelay = thisMsDelay

                except ValueError as e:
                    self.usererror( "{} is not a valid ms duration".format( userline ))

            self.userprint( "Delay = {} ms".format( self.msdelay ));
            return False

        if c in 'qQ':
            if self.quietmode:
                self.quietmode = False
                self.userprint( "Quiet mode off." )
            else:
                self.quietmode = True
                self.userprint( "Quiet mode." )
            return False


        # Misc general utility

        if c in 'rR':
            self.cmd_Reset( theSerial )
            return False

        if c in 'bB':
            self.cmd_Boot( theSerial )
            return False


        # BASIC Commands

        if c in 'cC\x03':
            # catalog
            self.userprint( "Catalog:" )
            self.cmd_BASIC_Catalog()
            return False

        if c in 'Ll\x0c':
            filename = self.my_getline( "LLVD: Load file? " )

            if filename == "":
                filename = self.basic_filename
            else:
                self.setFilename( filename )

            self.cmd_BASIC_Load( filename, theSerial )
            return False

        if c in 'Ss':
            filename = ""
            while filename == "":
                filename = self.my_getline( self.prompt + "Save file? " )

                if filename == "":
                    filename = self.basic_filename
                else:
                    self.setFilename( filename )

            self.userprint( "Saving " + self.basic_filename )

            # actually save it
            theSerial.write( "\n\rLIST" );
            theSerial.flush();
            theSerial.write( "\n\r" );
            self.startCaptureForSave( self.basic_filename );
            return False


        # Textfile Commands

        if c in 'tT':
            filename = self.my_getline( "LLVD: Type file? " )

            if filename == "":
                self.userprint( "No filename. No action." )
                return False

            self.cmd_TypeToTarget( filename, theSerial )
            return False

        if c in 'fF':
            filename = ""
            while filename == "":
                filename = self.my_getline( "LLVD: Capture to file? " )

                if filename == "":
                    filename = self.capture_filename
                else:
                    self.capture_filename = filename

            self.startTextCapture( filename )
            return False

        if c in 'xX':
            self.endTextCapture()
            return False

        # not a command... 

        if c in '\x0a\x0d':
            # empty line. do nothing.
            return False

        self.usererror( "What? {} {}".format( hex(ord(c)), c ) )

        # returning false returns control to terminal operations
        return False
