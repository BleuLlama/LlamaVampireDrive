# makefile to use the basicusr core makefile to 
# generate a .BAS RC2014 Basic program

TARGBASE := llvdstrp

DEPFILES := \
	llvdstrp.asm \
	toolbox.asm \

include ../Common/basicusr.mak

test: clean all
	


edit:
	open llvdstrp.asm toolbox.asm ../Common/hardware.asm

.PHONY: edit
