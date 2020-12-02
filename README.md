# LlamaVampireDrive

A transparent over-the-serial-console storage solution.

# Overview

This drive system is meant to be a cheap (free) mass storage system for
serial-based computer systems that might not otherwise have a local
storage system, or may have one but it is inconvenient to transfer
content onto.  It may not be fast.

The primary use for this, for me, is to give a mass-storage solution
to my RC2014 Z80 vintage-like computer, which does not have any 
storage on it at all, other than volatile RAM.

The good things about this drive system is that it will be transparent
to the user, and provide all of the files and potentially resources
of the terminal computer to the target computer.

There are three phases of development for this as I see it. These 
are not necessarily dependent on each other.

# Document Terms & Conventions

In this document control sequences are signified like ^P.  ^P means
[CTRL]-[p], or HEX-ASCII 0x10.

In this document, <CR> signifies a line ending. Actual line endings
can be <CR> or <LF>.

For the sake of clarity, the two computers involved with a transaction
will be categorized like so:

## Terminal

This is the device in the system that the user is connecting from.  
It has the keyboard and display screen, as well as the mass storage 
system. The terminal is what is running the terminal emulation software 
with the vampire drive extensions.

## Target

This is the device that the user is connecting to.  In my case, the target is a 
RC2014 Z80 computer.  It has a FTDI connector providing a TTL-level RS232 interface.
I have mine connected through this interface to a USB-Serial device on my terminal
computer (my Mac).

# Features and Development Groups

## Group 1

Group 1 is a version of the python serial library's "miniterm.py" 
program, that is meant as a baseline and proof of concept for this 
interface.  Obviously, this can be used exclusively as the interface
without any additional features to be added.

- "Type" a local file to the target, with optional delay-per-character
- "Capture" serial text from the target to a file
- escape sequence versions of these commands to be commanded from the target

Built upon these are the features for the provided MS BASIC:

- "SAVE" support (enable capture to file, type 'list' store until done)
- "LOAD" support (just typing in a file)


## Group 2: Random File IO

Group 2 adds random file IO to the mix, providing an interface for the target
to open files for read/write, seek to specific file positions, read/write 
specific numbers of bytes, close the file.  It will support 16 simultaneous 
file handles.


## Group 3: Additional Resources

Group 3 adds file interfaces for other system resources, such as a 
realtime clock, http requests, bsd-socket connections/telnet 
connections, etc.

## Group 4: C Library

This is a version of the interface that is meant to be included in other
software, like PIGFX, LlamaTerminal, or an Arduino sketch for a true inline
serial interface.

## Group 5: Arduino Inline Interface

This is a device that plugs into the FTDI header on the target, and provides
another FTDI header for the terminal to connect to.  This device has its
own SD card for storage, and transparently provides this entire 
interface.

-----

# Filesystem Overview

LLVD expexts a directory (or symlink) in the current directory named "FS"
that contains all of the files it provides and stores.  In this directory
are a few subdirectories to keep things tidy:

## FS/

This is the root of the LLVD filesystem. Captures will be stored 
in this directory.


## FS/BASIC

This directory is the default directory for all of the basic programs.
Everything LOADed and SAVEd will be out of this directory.  CATALOG
will provide a listing of this directory as well.

## FS/DRV

This directory contains the virtual drive files.  More info on this
later in this document


-----

# The Protocol and Interface Commands


Here's a simple text diagram of the usual chain of command:

    [User]---[Keyboard]---[Miniterm]---[USB Serial]---[RC2014]

However, if it's broken out with the LLVDrv in place it looks
something like this:

    [User]---[Keyboard]---[   -> (LLVDrv commands)
                              -> (user input)

                                 ( Miniterm+LLVDrv )

                                     (LLVDrv commands) <-
                                                (disk) -> 
                                          (user input) -> ]---[USB Serial]---[RC2014]



# Protocol: From Terminal ^P

LLVDrv commands may have a "capture from Terminal" version, along with 
their standard "escape sequence from target" protocol.

This interface is based on a simple control key, then a letter (or multiple 
letters).  The control key is ^P.  Naturally, 
to actually send a ^P to the target, you would press it a second time.

When the system is doing one of its tasks, it may ignore the ^A key pressed,
for example when binary data or text file data is being sent to the target,
as that takes place further down the chain.

The currently-planned ^P commands are:

## File IO

 - ^Pt<filename><CR>	type a file to the target
 - ^Pc<filename><CR>	capture to a file (only target output is saved)
 - ^Px					ends a running capture

 - ^Pb					loads "boot.bas", and sends "RUN" to run it.

## BASIC LOAD

Loads the specified file (or the last typed-in filename)
The default filename is "saved.bas".

 - ^Pl<filename><CR>	loads the specified filename
 - ^Pl<CR>	loads the last typed-in filename (or "saved.bas")

The user is prompted for the filename to use

## BASIC SAVE

Saves the current program to the specified filename (or the last typed-in filename)
The default filename is "saved.bas".

 - ^Ps<filename><CR>	saves to the specified filename
 - ^Ps<CR>	saves to the last typed-in filename

The user is prompted for the filename to use. 


## Miscellaneous

 - ^Pb			start the boot sequence on the target

 - ^P^P			send [CTRL]-[p]
 - ^Pp			send [CTRL]-[p]

 - ^Ph			send help text to terminal
 - ^P?			send help text to terminal
 - ^Pv			send version text to terminal
 - ^Pq          toggle quiet mode (target output is read and ignored)

 - ^Px			end a capture or autotype session (or do nothing)

## Future Commands

 - ^Pr			reboot the target system (TBD)



# Protocol: Target - To - Terminal

The commands available to the target may include:

- ASCII "type" of content from a file to the target
- ASCII "capture" of content from the target to a file
- Binary file loading and saving/transfer
- Sector based loading and saving for virtual disks
- Realtime Clock set/get
- Other GPIO functions, including target reset

I'll go through these one by one to explain their function as well as 
how to 'make them happen'...

## Message Types Explained

Type and Capture are used to send or receive exact text files
from the mass storage from the target computer.

Load and Save are basically Type and Capture, but with extra 
stuff around them to make them more user friendly for pure
BASIC programming.  Load will also send "NEW" to the target,
if the file to be loaded is readable. Save will do a capture,
but skip over the "LIST" and "Ok" text echo/responses.

Binary file loading and saving are good for accessing binary or 
text files that exist on the mass storage drive, and can be done
quicker than with the delay added for BASIC load and save

Sector based accesses are for OSes like CP/M which usually access
the sectors of a disk directly.  Rather than using compact flash
cards in other RC2014 systems, where the sector-based accesses will
go right to the sectors of the CF card, these go to directories on
the FAT filesystem that are dedicated for this purpose. Each 
virtual disk is a directory that contains all of the track and 
sectors as files on the FAT filesystem.  This makes distributing
and deploying sector-based filesystems as easy as copying files
normally or unzipping file heirarchies.

Then there are utility api commands, for accessing time and date,
gpio functions and such.  These are TBD


## Message Structure

The basics of the protocol is that the target will send a sequence
of characters (like ANSI escape codes) that will put LLVDrv into a 
"target interface mode" for a command until another character is 
sent, signifying the end.  Similarly, responses are structured the 
same way, using the same start and end characters.


The messages have a few parts to them:

	^^              START - ^\ or 0x1C or 28
	  D             DEVICE CHANNEL '0'..'9'
	   CC           COMMAND (two bytes)
	     ?:         INTENTION: '?' is request, ':' is response
	      data      DATA (0..x bytes)
	          ST    END - ^G or 0x07 or just plain 7


### START OF MESSAGE - ^\ - 0x1c - 28

The message is signified by sending 0x1c aka [CTRL]-[backslash].  This will 
switch LLVDrv into message listening mode.  This borrows the
"Control Extension" ANSI C0 control command.

Reference: https://en.wikipedia.org/wiki/C0_and_C1_control_codes


### DEVICE CHANNEL (one byte: '0'..'9')

For the most part, this can be ignored in the first versions
here, and will always be set as 0.

The text in this section is for future implementation, so 
for now, just use "0", and you can ignore this information. ;)

Next is an ascii value from '0' to '9'. This signifies which 
device in the chain should get the message.  A physical device 
may have one or more channels that it listens to. A device should 
always listen for its content on device channel 0.  Additional
endpoints on a device would incrememnt, as 1, 2, and so on. 

If a device receives a message for a channel number higher than
ones it handles, it should subtract the number of channels it 
listens to, and forward the entire message verbatim, starting with
the start-of-message, as above, and proceeding with the rest of 
the message until the end-of-message.

For example, if we have two physical devices on the chain, each 
handling two channels, each one will listen on their channel 0 and 1.
Let's say a message for channel 3 is sent down. The first device 
hears the start-of-message, then '3'. 3 is greater than 1, so it 
subtracts '2' (the number of channels it supports -- channels 0 and 1)
and then sends down the start-of-message byte, followed by the 
new channel value '1', and then the rest of the data of the 
message as it receives it, through the end-of-message indicator.


### COMMAND (two bytes)

This indicates what command is to be used.  Unknown commands
should be ignored and fail silently.  Here's a list of all of the 
commands.

 - ST:key:value  	- Set a setting value (also the response)
 - GT:key		  	- Get a setting value

 - OP:hnd:fn:mode	- open (fn)filename using mode "r" "w" "a", using handle id
 - SK:hnd:pos		- seek to the specified position for the handle id
 - CL:hnd			- close a file, using handle id

 - RH:hnd:nb		- request read of a number of bytes (nb)
 - WH:hnd:nb:hex	- write data to an open file

 - LS:path			- get list of filesystem entries

 - RS:d:t:s			- read sector (drive, track, sector)
 - WS:d:t:s:hex		- write sector (drive, track, sector)

 - CA:filename		- start capture to file
 - CE:				- End capture session

 - EE:text			- Echo text back to the target


For set and get, these are the available keys:
 - CD	- current directory
 - TM	- Current time HHMMSSmmm or HHMMSS, 24 hour time
 - DT	- Current date YYYYMMDD
 - QM	- Quiet Mode (1/0)


### FIELD SEPARATOR (one byte: ':')

This indicates separations between fields.

### DATA (0..? bytes)

Binary DATA content is sent as hex values in flat ASCII uppercase printable 
characters. That is to say that if you were sending the string 
"Hi!\0", the actual bytes sent down as the message would be 
"48692100".  This doubles the size of the data to be sent, plus the
overhead of the message wrapper, plus sending it over serial will
make this slower than CF accesses, but it can be easier to work
with, and less expensive to deploy, as it could be implemented within
existing terminal software, or in the PiGFX module for example.

### END OF MESSAGE - ^G - 0x07 - 7 (BELL)


This indicates the end of the message packet, and we return to normal
operations mode. This borrows the "Bell" ANSI C0 control command.

Reference: https://en.wikipedia.org/wiki/C0_and_C1_control_codes


## Message Commands


### ST:k:v --  set key 'k' to have value 'v'


The list of available settable keys:

- CD - /absolute path name to change as the 'current directory'
- TM - current time in zero-padded 24 hour format HHMMSSmmm : hours, minutes seconds, millis (optional)
- DT - current date in zero-padded format YYYYmmdd : year, month, day
- QM - quiet mode (inhibit echo to terminal), 1 = quiet, 0 = NOISY



Set the current time. be sure to zero-pad values to the right number of places.

    ST:TM:HHMMSS
    ST:TM:HHMMSSmmm

Get the current time:

    ST:TM

Set the current date, or the response for the above

    ST:DT:YYYYMMDD
    ST:DT:20190521

Get the current date:

    ST:DT

Turn on quiet mode:
	ST:QM:1

This will essentially eat all of the content from the target, 
so it does not echo back to the terminal.


### ER:hnd:n -- error code response

(details TBD)
Some example error responses:

	ER:0:Ok
	ER:1
	ER:2
	ER:4

- 0 is "no error"
- 1 is "no disk"
- 2 is "other error"
- 3 is "file isn't open"
- 4 is "not found"


### OP:hnd:fn:mode -- Open a file

Open the specified filename for IO operations.
Pass in a single digit for the file handle ID (1-9).
"fn" is the name of the file in the current directory.
"mode" can be the letter "R","W", or "A" signifying 'read',
'write' or 'append' respectively.

Open file #1 for reading:

 	OP:1:notes.txt:R

Open handle #2 for writing, overwriting existing file or create new:

	OP:2:output.bin:W

Open handle #6 for append or create new if it doesn't exist:

	OP:6:log.txt:A

Similar to fopen()


### SK:hnd:pos		- seek to the specified position for the handle id

This lets you seek randomly into a file. 'pos' is an integer value, 
but can also be one of these special words:

- START - seek to the beginning of the file (same as '0')
- END - seek to the end of the file

If negative values are used, they specify the number of bytes from the
end of the file.  A position of -1, for example, would make it such 
that if you read one byte you will get the last byte of the file.

Similar to fseek()


### FT:hnd		- tell the position in the file

This will tell you the byte position you're currently in, in the 
specified file.

Similar to ftell()


### CL:hnd -- close a file, using handle id

Close the requested file by handle id.

Similar to fclose()


### RH:hnd:nbytes -- read n bytes from file

Read 16 bytes from the file handle 5:

	RH:5:16

Which may respond something like this:

	RH:5:16:00230A83BCF92929294391249104fcd

Note that the 16 responded here indicates the number of bytes read from
the file, which expands out to hex, where two ascii characters are used
to represent one byte.

If fewer than the requested are indicated there, that will
indicate that an end of file (EOF) has been encountered.  It will truncate 
the returned record to match this.  For example, if 32 bytes were requested,
but only three were returned, the response may look like this:

    RH:5:3:452233

Also note that the field containing the number of bytes is NOT zero padded.
Zero padded values are optional.  That is to say, this is equivalent to
the above message:

    RH:5:0003:452233

Similar to fread()


### WH:hnd:nbytes:hex -- write n bytes in hex to file

Just like the above, but writing it.  Responses are in the form
WH:hnd:nbytes, like so:

    WH:5:4

Similar to fwrite()


### LS:p	-- Request filesystem list entries of path p

This will request a directory listing, responding with 
a list of file entries, ending with an empty file listing 
as explained below.

	LS:PATH

The path separator is '/', and fancy paths like "./" and "../" 
are not allowed.  All absolute paths start with "/" which is the 
contents of the FS/ directory on the mass storage device.

For example, the default path for BASIC programs is "/BASIC/" 
which can be found on the filesystem at "FS/BASIC/"


### LS:t:n:sz	-- Response for a file entry...

- 't' is the type of file, 'D' for directory, 'F' for file. 'E' for end of list
- 'n' is the name of the file in the directory, directories end with a slash /
- 'sz' is the filesize in bytes

Here's an example response of a short directory listing sequence:

	LS:F:readme.txt:921;
	LS:F:boot.bas:193;
	LS:D:files/;
	LS:D:junk;
	LS:;


### RS:d:t:s / WS:d:t:s:... - Virtual sector IO

These will read and write to the definied drive 'd', track 't' and 
sector 's'.  The WRS is also used as the response for a RDS command.

read drive D, track T, sector S:

	RS?D:T:S

write a sector file out:

	WS:D:T:S:92384092834098239048209384


### CA:f / E.	-- capture output from the target to a file


Start capture to the file specified

	CA:filename

End the capture session

	CE:

### EE:text, EL:text	-- echo the text back to the target

Just echo the text back, verbatim.  ^G and : are not allowed.

	EE:hello, this is text!

Or echo it back with CR/LF line endings:
	EL:1000 PRINT "Bloogle"


## Filesystem - Details

The filesystem on the flash drive is set up specifically to
make usage more useful.  All of the files and heirarchies for
these interactions are within a directory named "FS".  For
the sake of this document, this folder/directory will be
referred to as MS:/FS  This is the LL directory in the mass
storage drive.

For the boot process, the files explained above are on the
disk as:

    MS:/FS/BOOTC000.BAS
    MS:/FS/BOOT0000.ROM

The virtual disks are stored in the DRV subdirectory:

	MS:/FS/DRV/

In there, each folder is a virtual disk.  For now, there is
a 1:1 corrolation between these disks and CP/M disks.  So
for the first three drives, their contents will be in the
folders:

	MS:/FS/DRV/A/
	MS:/FS/DRV/B/
	MS:/FS/DRV/C/

And within each are a 4-digit zero padded directory that
specifes the track, and within each of those are a file for
each sector's data, named similarly. Example;

File containing Drive B, Track 34, sector 3 would be in:

	MS:/FS/DRV/B/0034/0003.BIN

And so on.
