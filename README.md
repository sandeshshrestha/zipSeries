# WIP - Not working (ETA medio October)

* [Install](#install)
* [Usage](#usage)
  * [Copy single object](#copy-single-object)
  * [Copy whole library](#copy-whole-library)
  * [Restoring from backup](#restoring-from-backup)
* [Config Files](#config-files)


# zipSeries CLI

Copy libraries / objects from one iSeries (AS/400) to another running the same (or lower) release of OS/400 as the source machine

	$ zipSeries --help
	usage: usage: zipSeries [--version] [--help] [OPTION]...

	Copy libraries / objects from one iSeries (AS/400) to another running the same
	(or lower) release of OS/400 as source.

	optional arguments:
	  -h, --help                      show this help message and exit
	  -v, --verbose                   be more verbose/talkative during the
	                                  operation.
	  --version                       output version information and exit

	Source Options:
	  -s, --source-srv S_SRV          set server for the source
	  -u, --source-usr S_USR          set user profile for the source
	  -p, --source-pwd S_PWD          set user password for the source
	  -l, --source-libl S_LIBL        set library for the source
	  -o, --source-obj S_OBJ          set object for the source - leave blank if
	                                  whole library is saved
	  -c, --source-config S_CONFIG    read source config from file
	  --source-save-file S_SAVE_FILE  save OS/400 savfile locally all --target-*
	                                  options will ignored

	Source Options:
	  -S, --target-srv T_SRV          set server for the target
	  -U, --target-usr T_USR          set user profile for the target
	  -P, --target-pwd T_PWD          set user password for the target
	  -L, --target-libl T_LIBL        set library for the target
	  -C, --target-config T_CONFIG    read target config from file
	  --target-save-file T_SAVE_FILE  restore from OS/400 savfile stored locally
	                                  all --source-* options will ignored

## Install:

	git clone ssh://github.com/ginkoms/zipSeries
	cd zipSeries
	bash install.sh

Make sure that ~/bin is in your `$PATH` variable:

	export PATH="~/bin:$PATH"

## Usage:

###Copy single object:

	# You will be prompted with password
	zipSeries \
		--source-srv=server1 --source-usr=QSECOFR --source-libl=MYLIB --source-obj=MYOBJ \
		--target-srv=server2 --target-usr=QSECOFR --target-libl=MYLIB

###Copy whole library:

	# You will be prompted with password
	zipSeries \
		--source-srv=server1 --source-usr=QSECOFR --source-libl=MYLIB \
		--target-srv=server2 --target-usr=QSECOFR --target-libl=MYLIB

###Making backup:

By specifying `--target-save-file=file.zs4` you can take local backups

	# You will be prompted with password
	zipSeries \
		--source-srv=server1 --source-usr=QSECOFR --source-libl=MYLIB --source-obj=MYOBJ \
		--target-save-file=~/my_save_file.zs4

###Restoring from backup:

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

