; TMS9918
;
;	TMS Core functions


.include "../Common/hardware.asm"
.include "../Common/basicusr.asm"

        .module TMS9918
.area   .CODE (ABS)


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; TMS color codes.

C_TRANS 	= 0x00	; transparent

C_BLACK		= 0x01
C_GRAY		= 0x0E
C_WHITE		= 0x0F

C_DRED		= 0x06
C_MRED		= 0x08
C_LRED		= 0x09

C_DYELLOW	= 0x0A
C_LYELLOW	= 0x0B

C_DGREEN	= 0x0C
C_MGREEN	= 0x02
C_LGREEN	= 0x03

C_DBLUE		= 0x04
C_LBLUE		= 0x05
C_CYAN		= 0x07

C_MAGENTA	= 0x0D

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;
;  Shared Memory Map!
;
; The following screenmode descriptors were composed by looking over all
; of the modes, figuring out needed block sizes and other restrictions, 
; and coming up with these all that use the same starting addresses 
; for each block.  Namely:

;                      ;  GFX1  GFX2  MCOL  TEXT
TMS_Name   = 0x3800    ;   Y     Y     Y     Y
TMS_Color  = 0x2000    ;   Y     Y     -     -
TMS_PatTab = 0x0000    ;   Y     Y     Y     Y
TMS_SprAtt = 0x3F00    ;   Y     Y     Y     -
TMS_SprPat = 0x1800    ;   Y     Y     Y     -
;  M1, M2, M3              M0    M3    M2    M1

.if( tmsGfxModes )

TMS_GFX1:
	.byte 0x00
	.byte TR_ME16 | TR_S8 | TR_INTD | TR_DISE
	.byte 0x0E, 0x80, 0x00, 0x7E, 0x03 ; memory mapping
	.byte C_BLACK

TMS_GFX2:
	.byte TR_M3
	.byte TR_ME16 | TR_S16 | TR_INTD | TR_DISE
	.byte 0x0E, 0xFF, 0x03, 0x7E, 0x03 ; memory mapping
	.byte C_WHITE

TMS_MCOL:
	.byte 0x00
	.byte TR_M2 | TR_ME16 | TR_SMAG | TR_S16 | TR_INTD | TR_DISE
	.byte 0x0E,    0, 0x00, 0x7E, 0x03 ; memory mapping
	.byte C_LBLUE

TMS_TEXT:
	.byte 0x00
	.byte TR_M1 | TR_ME16 | TR_INTD | TR_DISE
	.byte 0x0E,    0, 0x00,    0,    0 ; memory mapping
	.byte (C_WHITE<<4)|C_DGREEN

; Register 0:
;	0x02 	M3 bit
TR_M3   = 0x02

; Register 1:
;   0x01    Sprite Mag:  0x01: sprites scaled x2, 0x00: no mag
TR_SMAG = 0x01

;   0x02    Sprite Size: 0x02: 16x16 sprites, 0x00: 8x8 sprites
TR_S8   = 0x00
TR_S16  = 0x02

;   0x04    Reserved.  0x00
;   0x08    M2
TR_M2   = 0x08

;   0x10    M1
TR_M1   = 0x10 

;   0x20    Interrupts: 0x20: enabled, 0x00: disabled
TR_INTE = 0x20
TR_INTD = 0x00

;   0x40    Display Blank:  0x40: Enable display, 0x00: blank display
TR_DISE = 0x40
TR_DISB = 0x00

;   0x80    Memory size: 0x80: 16k VRAM, 0x00: 4K VRAM
TR_ME4  = 0x00
TR_ME16 = 0x80


.endif

.if( tmsFontBytes )
TMSFont:
	.byte	0,0,0,0, 0,0,0,0						; 0 all off
	.byte	255, 255, 255, 255,  255, 255, 255, 255 ; 1 all on
	.byte	254, 130, 130, 130,  130, 130, 254, 0 	; 2 box
	.byte	24, 24, 24, 254,  24, 24, 24, 0 		; 3 +
	.byte	0, 0, 0, 24,  0, 0, 0, 0				; 4 center dot

	.byte	112, 136, 128, 112, 8, 136, 112, 0		; 5 'S'
	.byte	128, 126, 66, 66, 66, 66, 126, 0		; 6 'C'
.endif

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; TMSColor
;
; Set the current foreground and background colors
;	0b11110000 is foreground color
;	0b00001111 is background color
; IN:
;	A  		fg/bg color
TMSColor:
	out		(TMS_Register), a
	ld		a, #135
	out		(TMS_Register), a
	ret


; TMSFontPush
;
; Pushes the font data to the pattern table ram on the TMS
; IN:
;	B 		number of 8-byte glyphs to store
;	HL 		address of the font/glyph byte list
;	DE 		destination address in TMS space (pattern table)
; DIRTY:
;	BC
TMSFontPush:
	call	TMSMemLoc

_tff_glyphs:					; FOR X = B to 0 (for each glyph)
	push	bc
	ld		b, #8

_tff_store_glyph:				;   FOR Y = 0 .. 8
	ld		a, (hl) 			;     A = READ( HL )
	out		(TMS_Memory),a 		;     OUT( MEM ), A
	inc 	hl  				; 	  HL++
	djnz	_tff_store_glyph 	;   NEXT Y

	pop		bc
	djnz	_tff_glyphs 		; NEXT X

	ret


; TMSBlit
;
; copy memory from Z80 to TMS ram
; IN:
;	B 		number of bytes to copy
; 	HL 		address of z80 memory start
;	DE 		address of TMS memory start
; DIRTY:
;	BC, HL

TMSBlit:
	call	TMSMemLoc			; set the destination address on the TMS

_tb:							; FOR B = 0 to b
	ld 		a, (hl) 			;   A = READ( HL )
	out 	(TMS_Memory), a 	;   OUT( MEM ), A
	inc 	hl  				; 	HL++
	djnz	_tb					; NEXT B 

	ret

; TMSPoke
;	Sets 1 byte to the value A at address DE
; DIRTY:
;	BC, HL
TMSPoke:
	ld 		b, #1
	; fall through....

; TMSMemSet
;
;	Sets B bytes to the value in A at address DE
; IN:
;	B 		number of bytes to set
; 	A 		byte to copy in
; 	DE 		TMS Memory address
TMSMemSet:
	call	TMSMemLoc			; set the destination address
TMSMemCont:
_tms:
	out 	(TMS_Memory), a
	djnz 	_tms

	ret

; TMSMemLoc
;
; preps for a set memory function
; IN:
;	DE 		memory address in TMS space
TMSMemLoc:
	push 	af

	ld		a, e
	out		(TMS_Register), a

	ld		a, d
	or 		a, #0x40
	out		(TMS_Register), a

	pop 	af
	ret


; TMSModeSet
;
; Stores the mode setup to the TMS registers 0..8
; IN:
;	HL 		address of the screen mode descriptor
; DIRTY:
;	AF, BC, HL
TMSModeSet:
	ld 	b,	#8
	ld 	c,	#0
	;{
		gv2:
			ld		a, (hl)
			out		(TMS_Register), a

			ld		a, c
			or		a, #0x80
			out		(TMS_Register), a

			inc		c
			inc		hl
			djnz	gv2
	; }
	ret



; DelayDBG
; outputs a byte to serial, and delays about 1/10s
DelayDBG:
	; {
		push	af
		ld		a, #'L
		out		(ACIA_Data), a
		pop		af
	; }

; Delay
; only delay about 1/10 second
Delay:
	push	bc
	ld		b, #255
__d2:
	; { 
		push	bc
		ld		b, #255
		djnz	.
		pop		bc
		djnz	__d2
	; }
	pop		bc

	ret	


; TMSClr
;	clear bits of memory for sprite stuff
TMSClr:
	ld 		hl, #TMS_SprAtt
	ld 		b, #0xFF
	ld 		a, #0x00
	call 	TMSMemSet

	ld 		hl, #TMS_Color
	ld 		b, #0xff
	ld 		a, #C_WHITE
	call	TMSMemSet

	ret

TMSTest:
	call 	TMSClr

	; switch to the right display mode
	ld		hl, #TMS_TEXT
	call	TMSModeSet

	; store our font to the TMS
	ld		de, #TMS_PatTab		; pattern table (font memory)
	ld 		hl, #TMSFont		; font we want
	ld  	b, #7 				; 7 glyphs
	call 	TMSFontPush

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
	ret