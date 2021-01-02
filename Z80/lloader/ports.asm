; Ports
;          Ports examiner app for LLoader
;
;          2016-06-15 Scott Lawrence
;
;  This code is free for any use. MIT License, etc.

	.module Ports

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; InPort
;	read in the specified port and print it out
InPort:
	ld	hl, #str_port	; request a byte for the port
	call	Print
	call 	GetByteFromUser
	call	PrintNL

	ld	c, b		; port to read from in a
	in	a, (c)

	push	af		; print out the port data
	ld	hl, #str_data
	call	Print
	pop	af

	call	printByte	; print the value
	call	PrintNL

	xor	a
	ret			; next

; OutPort
;	output the specified byte to the specified port
OutPort:
	ld	hl, #str_port	; request a byte for the port
	call	Print
	call 	GetByteFromUser
	call	PrintNL
	ld	c, b

	ld	hl, #str_data	; request the port data
	call	Print
	call 	GetByteFromUser
	ld	a, b

	out	(c),a		; send it out
	call	PrintNL

	xor	a
	ret


str_port:
	.asciz	"Port: 0x"

str_data:
	.asciz	"Data: 0x"

str_address:
	.asciz 	"Address: 0x"

str_spaces:
	.asciz	" "


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; Terminal app
;  Opens the SD port, and sends stuff to and fro

str_intro:
	.ascii	"Terminal connection opening\n\r"
	.asciz	"Hit backtick ` to end\n\r"

str_outro:
	.asciz	"\n\rTerminated connection\n\r"

TerminalApp:
	ld	hl, #str_intro
	call	Print

	ld 	a, #'~
	out	(SDData),a
	ld 	a, #'0
	out	(SDData),a
	ld 	a, #':
	out	(SDData),a
	ld 	a, #'I
	out	(SDData),a
	ld 	a, #0x0d
	out	(SDData),a
	ld 	a, #0x0a
	out	(SDData),a


	; the main loop
	; check for input from either port
	; and send it to the other port  ))<>((
TermLoop:
	call	SDToTerm	; send stuff to the temrinal
	call	TermToSD	; Send stuff from the terminal

	cp	#'`		; if A is backtick, we can return
	jr	nz, TermLoop	; nope.  do it again!

	; if user types backtick, return.
TermExit:
	ld	hl, #str_outro
	call	Print
	xor	a
	ret


	; check for user Terminal input
	; send it to the SD drive
TermToSD:
	in      a, (TermStatus) ; ready to read a byte?
	and     #DataReady      ; see if a byte is available

	jr	z, RetWith0
	in      a, (TermData)   ; get it!

	out	(SDData), a	; a has the byte we sent
	ret
RetWith0:
	xor	a
	ret


	; check for SD drive output
	; send it to the user Terminal
SDToTerm:
	in	a, (SDStatus)
	and	#DataReady	; mask off the "data is ready bit
	;ret	nz		; nope. return.

	in	a, (SDData)	; get a byte from the SD interface
	;push	af
	;call	printByte
	;call	PrintNL
	;pop	af
	call	PutCh 		; send the byte out to the terminal
	ret
