; Toolbox
;
;	helper functions for this project
;	- Print to ACIA
;	- TMS core functions
; 	- delay routine
;	- mini-Llama Vampire Drive interface


.include "../Common/hardware.asm"
.include "../Common/basicusr.asm"

        .module TOOLBOX
.area   .CODE (ABS)


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; LLVD Group 2A (boot loader) interface

LLVD_M_START = 0x1C		; start of message
LLVD_M_CH0	 = 0x30		; channel 0 (ascii '0')
LLVD_M_END   = 0x07		; end of message

; commands supported:
;	OP:0:<filename>:r 			open "filename" as handle 0 for read
;	RH:0:16					read #bytes from file handle 0
;   GT:VI						get version info (only)


; LLVD_Open0
;	open file handle 0 for read 
;	pass in the filename as a null-terminated string via hl
;	preserves all registers
LLVD_Open0:
	push	hl
	push	hl

	ld		hl, #tl_OP0
	call	Print			; start of message

	pop		hl
	call	Print			; filename

	ld		hl, #tl_END
	call	Print			; end of message request

	pop		hl
	ret

tl_OP0:
	.byte	LLVD_M_START		; Start of message
	.asciz 	"0:OP:0:"			; Channel 0 : Open : handle 0

tl_END:
	.ascii	":r"				; For read
	.byte	LLVD_M_END, 0x00	; End of message


; LLVD_R0_16
;	read 16 bytes from file handle 0
;	pass in the location to store the data starting in hl
;	returns:
;		b 	number of bytes read
;		all other registers preserved
LLVD_R0_16:
	push 	hl
	ld		hl, #tl_R016
	call	Print			; send the read request
	pop		hl
	; TODO: read the content
	ld		b, #0
	ret

tl_R016:
	.byte	LLVD_M_START		; Start of message
	.ascii	"0:RH:0:16"			; Channel 0 : Read Hex : Handle 0 : 16 bytes
	.byte	LLVD_M_END, 0x00	; End of message

; LLVD Group 2B (the rest) interface
; commands supported:
;	ST, GT 			set, get
;	OP, SK, CL 		open, seek, close
;	RH, WH 			read, write
;	RS, WS 			read sector, write sector
;	LS 				directory list
;	CA, CE 			capture to file, end capture
;	EE 				echoback text
;
; set/Get keys:
;	TM 		get time
;	DT 		get date
; 	QM 		quiet mode
;	VI 		version info


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
			in		a, (ACIA_Status)
			and		#0x02
			jr		z, _OutWait
		; }
	pop		af
    out 	(ACIA_Data), a   ; echo
    ret


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Video stuff

TMSColor:
	out		(TMS_Register), a
	ld		a, #135
	out		(TMS_Register), a
	ret

T99GFX1: 	.byte 0, 208, 0, 0, 1, 0, 0, 244



TMSRegSend:
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



; delay of 255*255 is something like 1/10 second or so
Delay:
	; {
		push	af
		ld		a, #'L
		out		(ACIA_Data), a
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
