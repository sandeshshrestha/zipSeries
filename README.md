# WIP - Not working (ETA medio October)


# zipSeries CLI

Copy libraries / objects from one iSeries (AS/400) to another running the same (or lower) release of OS/400 as the source machine

	$ zipSeries --help
	usage: zipSeries [--version] [--help] [OPTION]...

	Copy libraries / objects from one iSeries (AS/400) to another running
	  the same (or lower) release of OS/400 as source.

	Mandatory arguments to long options are mandatory for short options too.
	  -s, --source-srv=[server]       set server for the source
	  -u, --source-usr=[user]         set user profile for the source
	  -p, --source-pwd=[password]     set user password for the source
	  -l, --source-libl=[library]     set library for the source
	  -o, --source-obj=[object]       set oject for the source
									  leave blank if whole library is saved
	  -c, --source-config=[config]    use file to set source config
		  --source-save-file=[file]   save OS/400 savfile locally
										all other --source-* options will ignored 
										if this option is set

	  -S, --target-srv=[server]       set server for the target
	  -U, --target-usr=[user]         set user profile for the target
	  -P, --target-pwd=[password]     set user password for the target
	  -L, --target-libl=[library]     set library for the target
	  -C, --target-config=[config]    use file to set target config
		  --target-save-file=[file]   restore from OS/400 savfile stored locally
										all other --target-* options will ignored 
										if this option is set

		  --help                      display this help and exit
		  --version                   output version information and exit

## Install:

	git clone ssh://github.com/ginkoms/zipSeries
	cd zipSeries
	bash install.sh

Make sure that ~/bin is in your `$PATH` variable:

	export PATH="~/bin:$PATH"

## Usage:

**Copy single object:**

	# You will be prompted with password
	zipSeries \
		--source-srv=server1 --source-usr=QSECOFR --source-libl=MYLIB --source-obj=MYOBJ \
		--target-srv=server2 --target-usr=QSECOFR --target-libl=MYLIB

**Copy whole library:**

	# You will be prompted with password
	zipSeries \
		--source-srv=server1 --source-usr=QSECOFR --source-libl=MYLIB \
		--target-srv=server2 --target-usr=QSECOFR --target-libl=MYLIB

**Making backup:**

By specifying `--target-save-file=file.zs4` you can take local backups

	# You will be prompted with password
	zipSeries \
		--source-srv=server1 --source-usr=QSECOFR --source-libl=MYLIB --source-obj=MYOBJ \
		--target-save-file=~/my_save_file.zs4

**Restoring from backup:**

By specifying `--source-save-file=file.zs4` you can restore from a local backup

	# You will be prompted with password
	zipSeries \
		--source-save-file=~/my_save_file.zs4 \
		--target-srv=server --target-usr=QSECOFR --target-libl=MYLIB


## Config Files

You can create config files to ease tedious backup processes etc, all config files should be stored in /etc/zipSeries and should have the extension .conf:


	$ cat /etc/zipSeries/server1.conf
	srv server1
	usr QSECOFR
	pwd secret
	libl MYLIB
	obj MYOBJ

	$ zipSeries \
		--source-config=server1 \
		--target-save-file=~/my_save_file.zs4

