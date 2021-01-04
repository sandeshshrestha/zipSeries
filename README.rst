=============
zipSeries CLI
=============

.. contents::
	:backlinks: none

.. sectnum::

Introduction
============

What is zipSeries CLI?
----------------------

zipSeries CLI is a command line interface for the software `zipSeries <http://www.system-method.com/ZipSeries>`_.

Copy libraries / objects from one iSeries (AS/400) to another running the same (or lower) release of OS/400 as the source machine

How is zipSeries CLI licensed?
------------------------------

MIT license. See the `LICENSE file <LICENSE>`_ in the distribution.

zipSeries --help
----------------

.. code-block::

	$ zipSeries --help
	usage: usage: zipSeries [--version] | [--help] | [OPTION]...

	Copy libraries / objects from one iSeries (AS/400) to another running the same
	(or lower) release of OS/400 as source.

	source options:
	  -s , --source-svr       set server for the source
	  -u , --source-usr       set user profile for the source
	  -p , --source-pwd       set user password for the source
	  -l , --source-lib       set library for the source
	  -o , --source-obj       set object for the source - leave blank if whole
	                          library is saved
	  --source-obj-type       set object type for the source
	  -c , --source-config    read source config from file
	  --source-save-file      save OS/400 savfile locally all --target-* options
	                          will ignored
	  --source-job-log-file   save source servers job log to a file

	target options:
	  --target-release        set OS/400 release for the target
	  -S , --target-svr       set server for the target
	  -U , --target-usr       set user profile for the target
	  -P , --target-pwd       set user password for the target
	  -L , --target-lib       set library for the target
	  -C , --target-config    read target config from file
	  --target-save-file      restore from OS/400 savfile stored locally all
	                          --source-* options will ignored
	  --target-restore-cmd    command to run when object(s) / library is restored
	                          on target machine
	  --target-job-log-file   save target servers job log to a file

	options:
	  --source-job-log        display source servers job log
	  --target-job-log        display target servers job log
	  --no-prompt             do not prompt on empty password and empty object
	  -v, --verbose           be more verbose/talkative during the operation
	  --trace                 trace commands and other information
	  --silent                silent mode. Don't output warnings
	  --version               output version information and exit
	  --help                  show this help message and exit



Install
=======

.. code-block:: bash

	$ cd ~
	$ git clone https://github.com/andlrc/zipSeries ~/.zipSeries
	$ cd .zipSeries
	$ echo 'PATH="$PATH:$HOME/.zipSeries/bin" >> ~/.bashrc'

Usage
=====

Copy single object
------------------

.. code-block:: bash

	# You will be prompted with password
	zipSeries \
		--source-svr server1 --source-usr QSECOFR --source-lib MYLIB --source-obj MYOBJ \
		--target-svr server2 --target-usr QSECOFR --target-lib MYLIB

Copy multiply objects
---------------------

.. code-block:: bash

	# You will be prompted with password
	zipSeries \
		--source-svr server1 --source-usr QSECOFR --source-lib MYLIB --source-obj MYOBJ --source-obj MYOBJ2 \
		--target-svr server2 --target-usr QSECOFR --target-lib MYLIB

Copy whole library
------------------

.. code-block:: bash

	# You will be prompted with password
	zipSeries \
		--source-svr server1 --source-usr QSECOFR --source-lib MYLIB \
		--target-svr server2 --target-usr QSECOFR --target-lib MYLIB

Making backup
-------------

By specifying `--source-save-file file.4zs` you can take local backups

.. code-block:: bash

	# You will be prompted with password
	zipSeries \
		--source-svr server1 --source-usr QSECOFR --source-lib MYLIB --source-obj MYOBJ \
		--source-save-file ~/my_save_file.zs4

Restoring from backup
---------------------

By specifying `--target-save-file file.4zs` you can restore from a local backup

.. code-block:: bash

	# You will be prompted with password
	zipSeries \
		--target-save-file ~/my_save_file.zs4 \
		--target-svr server --target-usr QSECOFR --target-lib MYLIB

Config Files
------------

You can create config files to ease tedious backup processes etc, all config files should be stored in /etc/zipSeries and should have the extension .conf:

.. code-block:: bash

	$ cat /etc/zipSeries/server1.conf
	svr server1
	usr QSECOFR
	pwd secret
	lib MYLIB
	obj MYOBJ

	$ zipSeries \
		--source-config server1 \
		--source-save-file ~/my_save_file.zs4

Next Versions
=============

See `TODO.md <TODO.md>`_
