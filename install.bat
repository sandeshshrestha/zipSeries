%echo off

set rootdir = "%appdata%\zipSeriesCLI\"
set bindir = "%rootdir%\bin\"
set cfgdir = "%rootdir%\config\"

if exist "%rootdir%" (
	echo "zipSeries: zipSeries CLI is allready installed" >&2
	echo "zipSeries: exiting..." >&2
	exit /B 1
)

mkdir "%rootdir%"
mkdir "%bindir%"
mkdir "%cfgdir%"

"python.exe" -m py_compile zipSeries.py
rename zipSeries.pyc zipSeries
move /Y zipSeries "%bindir%"

set PATH="%rootdir%\bin\;%PATH%"
