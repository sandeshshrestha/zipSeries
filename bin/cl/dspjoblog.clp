QSYS/CRTPF FILE(QTEMP/JOBLOG) RCDLEN(528) SIZE(1000000 10000 100)
QSYS/OVRPRTF FILE(QPJOBLOG) HOLD(*YES) SPLFOWN(*JOB) OVRSCOPE(*JOB)
QSYS/DSPJOBLOG OUTPUT(*PRINT)
QSYS/CPYSPLF JOB(*) FILE(QPJOBLOG) TOFILE(QTEMP/JOBLOG) SPLNBR(*LAST)