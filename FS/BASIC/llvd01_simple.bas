1 REM Example program showing LLVampire usage
2 REM 2020-11-01 Scott Lawrence - yorgle@gmail.com
3 REM Not perfect due to buffering, etc.
10 PRINT "Greetings."
20 REM Turn on quiet mode
21 PRINT CHR$(&h1c);"0:ST:QM:1";CHR$(&h07) 
30 REM Inject text
31 PRINT CHR$(&h1c);"0:EL:Some Text";CHR$(&h07)
40 REM Read it back in
41 INPUT A$	
50 REM Turn off quiet mode
51 PRINT CHR$(&h1c);"0:ST:QM:0";CHR$(&h07)
60 REM Output the read-in text
61 PRINT "The text is |"; A$; "| Whee!"
70 REM get the current time
71 PRINT CHR$(&h1c);"0:GT:TM:0";CHR$(&h07)
72 PRINT CHR$(&h1c);"0:EL:";CHR$(&h07)
73 INPUT T$
74 PRINT "The current time is "; T$