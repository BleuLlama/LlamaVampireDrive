; ASM based tests for TMS stuff
;
;  This code is a payload on a BASIC program that will poke it into 
;  memory at 0xF800, then call USR(0) to trigger it.
;
;
;  This code assumes a RC2014 system with:
;	- NASCOM BASIC ROM at RUN
;	- TMS9918A video card
;	- 6850 ACIA at IO 0x80


.include "../Common/hardware.asm"
.include "../Common/basicusr.asm"

        .module LLVD_STRAP
.area   .CODE (ABS)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Library options

; TMS 
tmsGfxModes = 1
tmsTestText = 0
tmsTestGfx = 1


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; entry point

;.org	0xF800

.org ENTRYORG

usr:
	call TMSTest

	;ld	a, #C_LGREEN
	;call 	TMSColor

	; return to BASIC
	ld		a, #0x10
	ld		b, #0x92	; 0x1092 -> 4242.d

	jp		ABPASS


TMSTest:
	call 	TMSClr

	; switch to the right display mode
	;ld		hl, #TMS_BLANK
	ld		hl, #TMS_TEXT
	call	TMSModeSet

	; store our font to the TMS
	ld		de, #TMS_PatTab		; pattern table (font memory)
	ld 		hl, #TMSFont		; font we want
	ld  	b, #7 				; 7 glyphs
	call 	TMSFontPush

	ld 		de, #TMS_PatTab + (8*'0)	; ascii 0
	ld 		hl, #TMSFontDigits		; digit fonts
	ld 		b, #10*8
	call 	TMSBlit

	; store stuff to the screen tilemap (name table)
	ld 		de, #TMS_Name 		; name table (character ram)
	ld 		a, #4				; shove in this character

	; textmode fill...
	ld 		b, #255				; this many times
	call 	TMSMemSet
	ld 		b, #255
	call 	TMSMemCont			; and again
	ld 		b, #255
	call 	TMSMemCont			; and again
	ld 		b, #255
	call 	TMSMemCont			; and again

	call	TMSMFill

	ld 		a, #1				; char #2
	ld 		de, #TMS_Name + 0 	; top left
	call 	TMSPoke
	ld 		de, #TMS_Name + 39 	; top right
	call 	TMSPoke
	ld 		de, #TMS_Name + 920 ; bot left
	call 	TMSPoke
	ld 		de, #TMS_Name + 959 ; bot right
	call 	TMSPoke

	ret


	; store some data to the tms
	;ld 		de, #0x0800 		; name table (character ram)
	;ld 		hl, #memxxx			; local source pointer
	;ld 		b, #16				; copy 16 bytes
	;call 	TMSBlit				; store it to TMS mem

.include "../Common/tms9918.asm"


;;;;;;;;;;;;;;;;;;;;;;;;
; Internal "font"

TMSFont:
	.byte	0,0,0,0, 0,0,0,0						; 0 all off
	.byte	255, 255, 255, 255,  255, 255, 255, 255 ; 1 all on
	.byte	254, 130, 130, 130,  130, 130, 254, 0 	; 2 box
	.byte	24, 24, 24, 254,  24, 24, 24, 0 		; 3 +
	.byte	0, 0, 0, 24,  0, 0, 0, 0				; 4 center dot

TMSFontDigits:
	; based on "Ready-P9" on fontstruct
	; 0
	.byte   0b01110000
	.byte   0b10001000
	.byte   0b10011000
	.byte   0b10101000
	.byte   0b11001000
	.byte   0b10001000
	.byte   0b01110000
	.byte   0b00000000

	; 1
	.byte   0b00100000
	.byte   0b01100000
	.byte   0b00100000
	.byte   0b00100000
	.byte   0b00100000
	.byte   0b00100000
	.byte   0b01110000
	.byte   0b00000000

	; 2
	.byte   0b01110000
	.byte   0b10001000
	.byte   0b00001000
	.byte   0b00010000
	.byte   0b00100000
	.byte   0b01000000
	.byte   0b11111000
	.byte   0b00000000

	; 3
	.byte   0b11111000
	.byte   0b00010000
	.byte   0b00100000
	.byte   0b00010000
	.byte   0b00001000
	.byte   0b10001000
	.byte   0b01110000
	.byte   0b00000000

	; 4
	.byte   0b00010000
	.byte   0b00110000
	.byte   0b01010000
	.byte   0b10010000
	.byte   0b11111000
	.byte   0b00010000
	.byte   0b00010000
	.byte   0b00000000

	; 5
	.byte   0b11111000
	.byte   0b10000000
	.byte   0b11110000
	.byte   0b00001000
	.byte   0b00001000
	.byte   0b10001000
	.byte   0b01110000
	.byte   0b00000000

	; 6
	.byte   0b00110000
	.byte   0b01000000
	.byte   0b10000000
	.byte   0b11110000
	.byte   0b10001000
	.byte   0b10001000
	.byte   0b01110000
	.byte   0b00000000

	; 7
	.byte   0b11111000
	.byte   0b00001000
	.byte   0b00010000
	.byte   0b00100000
	.byte   0b00100000
	.byte   0b00100000
	.byte   0b00100000
	.byte   0b00000000

	; 8
	.byte   0b01110000
	.byte   0b10001000
	.byte   0b10001000
	.byte   0b01110000
	.byte   0b10001000
	.byte   0b10001000
	.byte   0b01110000
	.byte   0b00000000

	; 9
	.byte   0b01110000
	.byte   0b10001000
	.byte   0b10001000
	.byte   0b01111000
	.byte   0b00001000
	.byte   0b00010000
	.byte   0b01100000
	.byte   0b00000000

