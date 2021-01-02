1 REM LLVD example program to save rom data to a file
2 REM 2020-11-03 Scott Lawrence - yorgle@gmail.com

10 REM configuration
11 CLEAR 255
12 SZ = 1024		: REM number of bytes to save
13 BSZ = 16			: REM 16 bytes per block
14 BLKS = SZ / BSZ	: REM number of blocks

19 PRINT "Starting.  ";BLKS;" blocks." 

20 REM Open the file, use handle "1"
21 PRINT CHR$(&h1c);"0:OP:1:romdump.bin:w";CHR$(&h07);
22 REM TODO: read response here

90 REM Turn on quiet mode
91 REM PRINT CHR$(&h1c);"0:ST:QM:1";CHR$(&h07)

100 REM for each block...
110 FOR B = 0 TO BLKS
120 TX$ = "" : REM reset our transmit accumulator

200 REM for each byte in that block
200 FOR D = 0 TO (BSZ-1)
210 X = PEEK( (B * 16) + D )
220 IF X > 16 THEN 240
230 TX$ = TX$ + "0" : REM zero-pad 1 digit bytes
240 TX$ = TX$ + HEX$(X)
250 NEXT D

300 REM Write the block to the file
310 PRINT "Writing block "; B ; " of " ; BLKS
320 PRINT CHR$(&h1c);"0:WH:1:16:";TX$;CHR$(&h07);
330 NEXT B

900 REM close the file
910 PRINT CHR$(&h1c);"0:CL:1";CHR$(&h07);

1000 REM Resume noisy mode
1001 REM PRINT CHR$(&h1c);"0:ST:QM:0";CHR$(&h07)

1010 PRINT "Done!"
