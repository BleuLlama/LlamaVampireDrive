1 PRINT "Welcome to the LlamaVampireDrive system!"
2 PRINT ""
3 PRINT "Replace BOOT.BAS with your boot sequence program"
10 REM Clear TMS9918A Screen
20 TM=&h10 : TR=&h11
30 FOR I=0 TO 7
40 READ V : OUT TR,V : OUT TR,(I OR &h80)
50 NEXT I
60 DATA 0,208,14,0,0,0,0,12
80 REM Switch to TMS video
90 PRINT CHR$(&h1C);"0:RV:2";CHR$(&h07)