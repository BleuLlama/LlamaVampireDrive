; RC2014 Hardware Defines
;
;          2016-2021 Scott Lawrence
;
;  This code is free for any use. MIT License, etc.
;
	.module RC2014HW

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; some defines we will use (for ports)

;;;;;;;;;;;;;;;;;;;;
; 	RC2014 MC6850 ACIA Serial IO Module
ACIA_Status	= 0x80	; Status on MC6850 for terminal comms
ACIA_Data	= 0x81	; Data on MC6850 for terminal comms
  ACIA_Ready	= 0x01  ;  bit to check if there's data ready


;;;;;;;;;;;;;;;;;;;;
; RC2014 Paged ROM Module
;  writes to this port will toggle 0x0000-0x7FFF from RAM to ROM.
;  Resetting the system forces it back to ROM.
Page_Toggle  	= 0x38	


;;;;;;;;;;;;;;;;;;;;
; 	RC2014 Digital IO Module
; reads: bit values for buttons
; writes: sets the LEDs
DIGIO_0	= 0x00	; Configured as port 0x00
DIGIO_1	= 0x01	; Configured as port 0x01
DIGIO_2	= 0x02	; Configured as port 0x02

; this is the one we're using:
DigitalIO 	= DIGIO_0


;;;;;;;;;;;;;;;;;;;;
; 	TMS9918A Video Card
;	https://github.com/jblang/TMS9918A

; settings for MSX-1
;	J4: 5th,  J6: right,  JP1: upper,  JP2: upper
TMS_MSX_MEM = 0x98
TMS_MSX_REG = 0x99

; settings for ColecoVision
;	J4: 6th,  J6: left,  JP1: lower,  JP2: lower
TMS_MSX_MEM = 0xBE
TMS_MSX_REG = 0xBF

; settings for SORD M5
;	J4: 1st,  J6: right,  JP1: lower,  JP2: lower
TMS_SORD_MEM = 0x10
TMS_SORD_REG = 0x11


; this is the one we're using:
TMS_Memory   = TMS_SORD_MEM	; Memory port
TMS_Register = TMS_SORD_REG	; Control Register Port


; Color codes.
C_TRANS 	= 0

C_BLACK		= 1
C_GRAY		= 14
C_WHITE		= 15

C_DRED		= 6
C_MRED		= 8
C_LRED		= 9

C_DYELLOW	= 10
C_LYELLOW	= 11

C_DGREEN	= 12
C_MGREEN	= 2
C_LGREEN	= 3

C_DBLUE		= 4
C_LBLUE		= 5
C_CYAN		= 7

C_MAGENTA	= 13


;;;;;;;;;;;;;;;;;;;;
; 	Emulation Control
EmulatorControl	= 0xEE
	; Read for version of emulator:
	;   'A' for RC2014 emu (32k)    v1.0 2016/10/10
	;   'B' for RC2014LL emu (64k)  v1.0 2016/10/10
	; write F0 to exit emulator
 EmuExit	= 0xF0
    ; RC2014 will respond as FF or 00
