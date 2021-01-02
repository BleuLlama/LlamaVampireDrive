# Makefile for RC2014/LL

ROMSDIR := ../FS/ROMs

all:	roms

ROMDIRS := \
	baslload \
	selftest 

OLDDIRS: = \
	smalltest \
	aciatest \
	iotest


roms: 
	@echo "Building ROMs"
	for dir in $(ROMDIRS); do \
               $(MAKE) -C $$dir; \
             done

clean:
	@echo "Cleaning up all products"
	-rm -rf $(ROMSDIR)/*
	for dir in $(ROMDIRS); do \
               $(MAKE) -C $$dir clean; \
             done
