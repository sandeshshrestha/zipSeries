#!/usr/bin/env sh

# You will be prompted with password
zipSeries \
	--source-svr server1 --source-usr QSECOFR --source-lib MYLIB \
	--target-svr server2 --target-usr QSECOFR --target-lib MYLIB
