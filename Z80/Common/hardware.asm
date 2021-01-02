; RC2014 Hardware Defines
;
;          2016-2020 Scott Lawrence
;
;  This code is free for any use. MIT License, etc.
;
	.module RC2014HW

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; some defines we will use (for ports)

;;;;;;;;;;;;;;;;;;;;
; RC2014 MC6850 ACIA Serial IO Module
TermStatus	= 0x80	; Status on MC6850 for terminal comms
TermData	= 0x81	; Data on MC6850 for terminal comms
  DataReady	= 0x01  ;  bit to check if there's data ready

;;;;;;;;;;;;;;;;;;;;
; RC2014 Paged ROM Module
MemPage  	= 0x38	; write to toggle ROM-RAM
					; reset to force it to ROM

;;;;;;;;;;;;;;;;;;;;
; RC2014 Digital IO Module
DigitalIO	= 0x00	; Read buttons, write LEDs

;;;;;;;;;;;;;;;;;;;;
; TMS9918 Video Card - Configured as SORD-M5
TMSMemory   = 0x10	; Memory port
TMSRegister = 0x11	; Control Register Port

;;;;;;;;;;;;;;;;;;;;
; Emulation Control
EmulatorControl	= 0xEE
	; Read for version of emulator:
	;   'A' for RC2014 emu (32k)    v1.0 2016/10/10
	;   'B' for RC2014LL emu (64k)  v1.0 2016/10/10
	; write F0 to exit emulator
 EmuExit	= 0xF0
    ; RC2014 will respond as FF or 00