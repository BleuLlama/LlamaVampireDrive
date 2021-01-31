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
from os import path # path tools
import math
from datetime import datetime 

from Transform import Transform


class LlamaVampireDrive( Transform ):
    """support for the vampire drive system"""
    # I know most of this is also copied in miniterm, but I wanted a full
    # version of the implementation here.

    def __init__(self):
        self.version = "PY-LLVD v1.01 2020-11-30"

        self.basic_filepath = 'FS/BASIC/'
        self.basic_filename = 'SAVED.BAS'
        self.captureForSAVE = False
        self.save_fh = False

        self.filepath = 'FS/'
        self.capture_filename = 'CAPTURE.TXT'
        self.captureToFile = False
        self.file_fh = False

        # every delayCountMax bytes, wait for msDelay milliseconds
        # after testing this a lot, i've found that this actually
        # runs quite well and super fast! (relatively)
        self.delayCountMax = 8
        self.msDelay = 10

        # for direct-connected pi, 16/10 works well
        # for usb-serial or bluetooth, 8/25 usually works

        self.ioblocksize = 64
        self.quietmode = False
        self.accumulator = ''
        self.passthru = True
        self.activationkey = unichr( 0x10 ) # Vampire command CTRL+P
        self.qprompt = 'V? '
        self.prompt = 'V> '

        self.msg_start = 0x1c
        self.msg_end = 0x07

        self.rx_mode = 'thru'

        self.vdebug = 0

        self.userprint( "{} starting...".format( self.getVersion() ))
        self.userprint( "CTRL-P to interact." )

        self.theSerial = False

        self.VARS = {
            'CD':'/',
            'TM':'HHMMSSmmm',
            'DT':'YYYYMMDD',
            'QM':'0'
        }

        self.FILES = {}


    def SetSerial( self, ser ):
        self.theSerial = ser

    # --------------------------------------------

    def echo(self, text):
        """text to be sent but displayed on console"""
        return text


    def rx(self, text):
        """text received from serial port"""
        ret = ''

        for ch in text:
            ret = ret + self.rx_byte( ch )

        return ret


    def rx_byte( self, ch ):

        #self.userprint( "{} {} {}".format( ord( ch ), ch , self.rx_mode ))
        if self.rx_mode == 'thru':
            if ord( ch ) == self.msg_start:
                self.rx_mode = 'vampire'
                self.vampire_message = []
                self.vampire_acc = ''
                return ''

        elif self.rx_mode == 'vampire':
            if ord( ch ) == self.msg_end:
                self._vampire_store()
                self.handle_vampire_command( self.vampire_message )
                self.rx_mode = 'thru'
                return ''
            else:
                self.handle_vampire_byte( ch )

            # always bail when we get a message byte.
            return ''
        else :
            pass


        if self.captureToFile:
            self.file_fh.write( ch )

        # save to a file if we need to
        if self.captureForSAVE:
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
                        return '' # make sure we bail out of the loop.

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
            return ch
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
    # handlers for stuff from the target...
    # --------------------------------------------


    def cmd_Set( self, args ):
        key = args[0]
        value = args[1]

        self.VARS[ key ] = value

        # special handlers
        if key == 'QM': # quiet mode
            if value == '1':
                self.quietmode = True
            else:
                self.quietmode = False

        # NOTE: time and date are ignored for this implementation.


    def cmd_Get( self, args ):
        key = args[0]
        value = ''

        if key == 'TM':
            now = datetime.now()
            value = now.strftime( "%H%M%S" )

        elif key == 'DT':
            now = datetime.now()
            value = now.strftime( "%Y%m%d" )
        else: 
            value = self.VARS[ key ]

        # send out the results to the target
        self.theSerial.write( ("ST:" + key + ":" + value).encode('utf-8') )


    def cmd_FileOpen( self, args ):
        self.userprint( "File Open: " + ', '.join( args ))

        handle = args[0]
        fname = args[1]
        fullfpath = self.filepath + fname
        mode = args[2]

        if not path.exists( fullfpath ):
            print "ERROR:  {}: File does not exist!".format( fullfpath )
            return

        print "OPEN {} FOR {} AS {}".format( fname, mode, handle )

        try:
            self.FILES[ handle ] = open( fullfpath, mode+"b" )

        except IOError:
            print "ERROR:  {}: IO Error opening file.".format( fullfpath )
        except OSError:
            print "ERROR:  {}: Error opening file.".format( fullfpath )

    def cmd_FileClose( self, args ):
        handle = args[0]
        print "FILECLOSE #{}".format( handle )
        self.FILES[ handle ].close();
        self.FILES[ handle ] = False

    def cmd_FileTell( self, args ):
        handle = args[0]
        value = self.FILES[ handle ].tell()
        self.userprint( "FILETELL #{} -> {}".format( handle, value ))
        self.theSerial.write( ("FT:" + handle + ":" + value).encode('utf-8') )


    def cmd_FileSeek( self, args ):
        handle = args[0]
        value = args[1]
        self.userprint( "FILESEEK #{} TO {}".format( handle, value ))
        if value == "END":
            self.FILES[ handle ].seek( 0, 2 )
        else:
            self.FILES[ handle ].seek( int( value ) )


    def cmd_ReadHex( self, args ):
        self.userprint( "Read Hex: " + ', '.join( args ))


    def cmd_WriteHex( self, args ):
        handle = args[0]
        nbytes = int( args[1] )
        data = args[2]
        buf = [0]*nbytes

        self.userprint( "WRITE #{} [{}] => {}".format(handle, nbytes, data ))

        for i in range( 0, nbytes ):
            bdata = data[ i*2:(i*2)+2 ]
            b = int( bdata, 16 )
            #print( "byte {} is {} {}". format( i, bdata, b ))
            buf[i] = b

        self.FILES[ handle ].write( bytearray( buf ))

    def cmd_ListDir( self, args ):
        path = args[0]
        self.userprint( "LS {}".format( path ) )


    def cmd_ReadSector( self, args ):
        drive = args[0]
        track = args[1]
        sector = args[2]

        self.userprint( "SEC RD D{} T{} S{}".format( disk, track, sector ) )


    def cmd_WriteSector( self, args ):
        drive = args[0]
        track = args[1]
        sector = args[2]
        data = args[3]
        self.userprint( "SEC WR D{} T{} S{} {}".format( disk, track, sector, data ) )


    def cmd_CaptureStart( self, args ):
        fname = args[0]
        self.userprint( "CAPTURE TO {}".format( fname ))


    def cmd_CaptureEnd( self, args ):
        self.userprint( "CAPTURE END" )


    # cmd_Echoback
    #   send text back to the user
    def cmd_Echoback( self, args, withNl ):
        content = args[ 0 ].encode('utf-8')

        self.theSerial.write( content )
        if withNl:
            self.theSerial.write('\x0a\x0d' )


    def handle_vampire_command( self, cmdlist ):
        device = cmdlist[0]
        command = ''
        args = []
        
        if len( cmdlist ) > 1:
            command = cmdlist[1]

        if len( cmdlist ) > 2:
            args = cmdlist[2:]

        self.userprint( '\n Dev: ' + device ) # ignored. placeholder.
        self.userprint( ' Cmd: ' + command + ' ( ' + ', '.join( args ) + ' )\n')

        if command == 'ST':
            self.cmd_Set( args )
            return

        if command == 'GT':
            self.cmd_Get( args )
            return

        if command == 'OP':
            self.cmd_FileOpen( args )
            return

        if command == 'SK':
            self.cmd_FileSeek( args )
            return            

        if command == 'FT':
            self.cmd_FileTell( args )
            return

        if command == 'CL':
            self.cmd_FileClose( args )
            return

        if command == 'RH':
            self.cmd_ReadHex( args )
            return

        if command == 'WH':
            self.cmd_WriteHex( args )
            return

        if command == 'LS':
            self.cmd_ListDir( args )
            return

        if command == 'RS':
            self.cmd_ReadSector( args )
            return

        if command == 'WS':
            self.cmd_WriteSector( args )
            return

        if command == 'CA':
            self.cmd_CaptureStart( args )
            return

        if command == 'CE':
            self.cmd_CaptureEnd( args )
            return

        if command == 'EE':
            self.cmd_Echoback( args, False )
            return

        if command == 'EL':
            self.cmd_Echoback( args, True )
            return

        self.userprint( 'VMPCMD? ' + ','.join( self.vampire_message ))


    def _vampire_store( self ):
        self.vampire_message.append( self.vampire_acc )
        self.vampire_acc = ''


    def handle_vampire_byte( self, ch ):
        if ch == ':':
            self._vampire_store()
        else :
            self.vampire_acc = self.vampire_acc + ch

    # --------------------------------------------

    def userprint( self, txt ):
        sys.stdout.write( self.prompt + txt + "\n" )
        sys.stdout.flush()

    def usererror( self, txt ):
        sys.stdout.write( self.prompt + "ERROR: " + txt + "\n" )
        sys.stdout.flush()

    def getVersion( self ):
        return "LlamaVampireDrive ({})".format( self.version )

    def setBasicFilename( self, filename ):
        if filename == "":
            return false
        self.basic_filename = filename
        return filename

    # --------------------------------------------

    # capture to file
    def startTextCapture( self, filename ):
        self.file_fh = open( self.filepath + filename, 'w' )
        self.captureToFile = True
        self.userprint( filename + ": Capturing." )

    def endTextCapture( self ):
        self.captureToFile = False
        self.file_fh.close()
        self.userprint( self.capture_filename + ": Capture ended." )


    # capture for BASIC SAVE

    def startCaptureForSave( self, filename ):
        self.save_fh = open( self.basic_filepath + filename, 'w' )
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
    ^Pr                 (r)eset the target via reset_target.py
    ^P0                 Select Video (0) (RPI composite) via video_select.py
    ^P1                 Select Video (1) (TMS) via video_select.py
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
            fs = os.stat( self.filepath + filename ).st_size
        except OSError as e:
            self.usererror( "{}: {} ---\n".format(filename, e) )
            return False

        total = 0
        self.userprint( "Typing {} ({} bytes)".format( filename, fs ) )
        try:
            with open( self.filepath + filename, 'rb') as f:
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

                        delay( self.msDelay )

                    sys.stdout.write( "\n\r" )
                    self.progress_line( total, fs )

        except IOError as e:
            self.usererror( "{}: {} ---\n".format(filename, e))
        return False

    def get_DirListFiles( self, filepath ):
        for (dirpath, dirnames, filenames) in walk( filepath ):
            #f.extend(filenames)
            break
        return sorted( filenames, key=lambda s: s.lower() )

    def get_DirListDirs( self, filepath ):
        for (dirpath, dirnames, filenames) in walk( filepath ):
            #f.extend(filenames)
            break
        return sorted( dirnames, key=lambda s: s.lower() )


    # cmd_BASIC_Catalog
    #   Send a file listing of the current file path to the terminal
    def cmd_BASIC_Catalog( self ):
        for (dirpath, dirnames, filenames) in walk( self.basic_filepath ):
            #f.extend(filenames)
            break

        #dirnames.sort()
        #filenames.sort()

        for fn in sorted( dirnames, key=lambda s: s.lower() ):
            print "    {:>3} {:>5} {}/".format( '~', 'DIR', fn )

        idx = 0
        for fn in sorted( filenames, key=lambda s: s.lower() ):
            fs = os.stat( self.basic_filepath + fn ).st_size
            print "    {:>3} {:>5} {}".format( idx, fs, fn )
            idx = idx+1


    # cmd_BASIC_Load
    #   pretty much the same thing, but it inhibits echo, and types "NEW" first
    def cmd_BASIC_Load( self, filename, theSerial ):
        fs = 0

        try:
            if filename.lstrip('-').isdigit():
                flist = self.get_DirListFiles( self.basic_filepath )
                filename = flist[ int( filename ) ]
        except IndexError as e:
            self.usererror( "{}: {} ---\n".format(filename, e) )
            return False

        try:
            fs = os.stat( self.basic_filepath + filename ).st_size
        except OSError as e:
            self.usererror( "{}: {} ---\n".format(filename, e) )
            return False

        total = 0
        self.userprint( "Loading {}".format( filename ) )
        try:
            with open( self.basic_filepath + filename, 'rb') as f:

                self.progress_line( total, fs )

                self.passthru = False
                theSerial.write( "\x03\x0a\x0dNEW\x0a\x0d" );
                delay( 100 )

                delayCount = 0
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

                        delayCount = delayCount + 1
                        if delayCount > self.delayCountMax:
                            delayCount = 0
                            delay( self.msDelay )

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
        os.system( "../Tools/reset_target.py" );
        theSerial.flush()

    # cmd_Video0
    #   do whatever's necessary to switch to video input 0
    def cmd_Video0(self, theSerial):
        os.system( "../Tools/video_select.py 0" );
        theSerial.flush()

    # cmd_Video1
    #   do whatever's necessary to switch to video input 1
    def cmd_Video1(self, theSerial):
        os.system( "../Tools/video_select.py 1" );
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
            theSerial.write( 0x10 )
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
                        self.msDelay = thisMsDelay

                except ValueError as e:
                    self.usererror( "{} is not a valid ms duration".format( userline ))

            self.userprint( "Delay = {} ms".format( self.msDelay ));
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
                self.setBasicFilename( filename )

            self.cmd_BASIC_Load( filename, theSerial )
            return False

        if c in 'Ss':
            filename = ""
            while filename == "":
                filename = self.my_getline( self.prompt + "Save file? " )

                if filename == "":
                    filename = self.basic_filename
                else:
                    self.setBasicFilename( filename )

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
