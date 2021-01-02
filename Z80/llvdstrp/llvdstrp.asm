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
; entry point

;.org	0xF800

.org ENTRYORG

usr:
    ld  a, #0x00    ; bit 0, 0x01 is ROM Disable
                ; = 0x00 -> ROM is enabled
                ; = 0x01 -> ROM is disabled
    out (RomDisable), a ; restore ROM to be enabled

	push	hl
	ld		hl,	#splash
	call	Print
	pop		hl

	ld		hl, #T99GFX1
	call	TMSRegSend

	ld		a, #4
	call	TMSColor

	call	Delay

	ld		a, #33
	call	TMSColor

	jp 		ABPASS

	; return to BASIC
	jp		ABPASS

splash: .asciz  "Working...\n\r"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; console text

; Print
;   output the c-string pointed to by HL to the console
;   string must be null terminated (asciz)
Print:
    push    af
	to_loop:
		;{ 
			ld  	a, (hl)     ; get the next character
			cp  	#0x00       ; is it a NULL?
			jr  	z, termz    ; if yes, we're done here.

			call    PutCh
			inc 	hl      ; go to the next character
			jr  	to_loop     ; do it again!
		; }
	termz:
	pop 	af
    ret         ; we're done, return!


PutCh:
	push	af
	_OutWait:
		; {
			in		a, (TermStatus)
			and		#0x02
			jr		z, _OutWait
		; }
	pop		af
    out 	(TermData), a   ; echo
    ret


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Video stuff

TMSColor:
	out		(VidReg), a
	ld		a, #135
	out		(VidReg), a
	ret

VidMem	= 0x10
VidReg	= 0x11

T99GFX1: 	.byte 0, 208, 0, 0, 1, 0, 0, 244



TMSRegSend:
	ld 	b,	#8
	ld 	c,	#0
	;{
		gv2:
			ld		a, (hl)
			out		(VidReg), a

			ld		a, c
			or		a, #0x80
			out		(VidReg), a

			inc		c
			inc		hl
			djnz	gv2
	; }
	ret



; delay of 255*255 is something like 1/10 second or so
Delay:
	; {
		push	af
		ld		a, #'L
		out		(TermData), a
		pop		af
	; }

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
