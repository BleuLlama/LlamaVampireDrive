; Bootstrap for the BASIC->ROM LOADER 
; for the LlamaVampireDrive system
;
;  This code is a payload on a BASIC program that will poke it into 
;  memory at 0xF800, then call USR(0) to trigger it.
;
;
;  This code itself will:
;	- make the LLVD calls to load "BOOT.ROM" to 0x0000...
;	- swap out the ROM for RAM at (0x0000-0x8000)
;	- call rst(0) / jump to 0x0000
;
;
;  This code assumes a RC2014 system with:
;	- NASCOM BASIC ROM at RUN
;	- 6850 ACIA at IO 0x80
;	- Pageable ROM module
;	- 64k RAM module
;  And is the precursor to loading CP/M


.include "../Common/hardware.asm"
.include "../Common/basicusr.asm"

        .module LLVD_STRAP
.area   .CODE (ABS)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Library options

; TMS 
tmsFontBytes = 1
tmsGfxModes = 1
tmsTestText = 0
tmsTestGfx = 1


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; entry point

;.org	0xF800

.org ENTRYORG

usr:
	ld	a, #0x01
	out	(DigitalIO), a
	
	; page swap to all-RAM
	ld 		a, #1
	out		(Page_Toggle), a
	;ld 		hl, #t_db0
	;call 	Print

	; send the bot file request
	ld		hl, #t_bootfile
	call	LLVD_Open0

	; catch the response
	ld		hl, #0xC000
	call	LLVD_R0_16

	; page swap back to ROM
	ld 		a, #1
	out		(Page_Toggle), a
	;ld 		hl, #t_db1
	;call 	Print

	ld 	a, #0b00000111
	out	(DigitalIO), a

	; return to BASIC
	ld		a, #0x10
	ld		b, #0x92	; 0x1092 -> 4242.d

	jp		ABPASS


t_bootfile:	.asciz "ROMs/boot.bin"
t_splash:	.asciz "Starting up...\n\r"
;t_db0:		.asciz "RAM bankswitched!\n\r"
;t_db1:		.asciz "And we're back!\n\r"

.include "../Common/toolbxlt.asm"
