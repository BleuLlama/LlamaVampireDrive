# Z80 Asm

NOTE: This directory is copied over from another project and
thus is out of date and out of sync with this project.  I will
be cleaning this up over time. - SL,2020


------
This directory contains a bunch of native z80 code projects
which are made to interface with the LLVampire Drive System.


The assembler used is "asz80" from the zcc package, which is available
in source form from my repository of Z80 dev tools available here:

    https://code.google.com/archive/p/bleu-romtools/

Also there is a required tool called "genroms" which converts Intel
hex files (IHX, HEX) to binary ROM files.

# Projects

- Common
  - Things common to all of the projects, shared makefile, rom definitions

- aciatest
  - Simple program I wrote to test polled IO for RC2014/68C50 emulation

- cpmbios
  - Development of a new BIOS that uses LLVampire Drive for its storage

- iotest
  - Another test for ACIA/68C50 emulation, and a test of loader ideas

- smalltest
  - Simple test to show how the build mechanism works
