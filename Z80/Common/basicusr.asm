; RC2014 BASIC usr() hooks
;
;          2016-2021 Scott Lawrence
;
;  This code is free for any use. MIT License, etc.
;
	.module BASICUSR

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; stuff needed for interfacing with USR() in BASIC

; the integer parameter frim the USR() call is loaded to register DE by calling DEINT
DEINT	   = 0x0a07
; eg: 
;	    call  DEINT
;		ld    a, e
;		cp    #10
;		....

; if you have a value to return, put it in register AB then call ABPASS
ABPASS	   = 0x117D
; eg:
;		ld    a, #0
;		ld    b, #42
;		call  ABPASS


; and this is the location for our entry point.
ENTRYORG   = 0xF800
; eg:
;	.org ENTRYORG
;		-- your code here---
;		ret
