#!/usr/bin/python2

# zipSeries 1.3.0
# Copyright (C) 2015 System & Method A/S Denmark
# Released under the MIT license
#
# Written by Andreas Louv <and@sitemule.com>

VERSION = '1.3.0'

import sys
import getpass
from src.config import RELEASE_LIST, OBJECT_TYPE_LIST, PGM_DESCRIPTION
from src.AS400 import AS400
from src.config_handler import read_config_file, check_config

# Python 3: raw_input() was renamed to input()
# Source: http://stackoverflow.com/a/7321970/887539
try: input = raw_input
except NameError: pass

def print_version():
	print('zipSeries ' + VERSION)
	print('')
	print('Copyright (C) 2015 System & Method A/S Denmark')
	print('Released under the MIT license')
	print('')
	print('Written by Andreas Louv <and@sitemule.com>')

def main():
	import signal, argparse, getpass

	def gracefull_exit(signum, frame):
		print('zipSeries: gracefully shutting zipSeries down. Use Ctrl + C in the future')
		sys.exit(0)
	
	# Windows doesnt have the SIGTSTP signal
	try: 
		signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))
		signal.signal(signal.SIGTSTP, gracefull_exit)
	except Exception as e:
		pass
	
	parser = argparse.ArgumentParser(
		usage='usage: zipSeries [--version] | [--help] | [OPTION]...',
		formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=100),
		add_help=False,
		description=PGM_DESCRIPTION
	)

	source_group = parser.add_argument_group('source options')
	target_group = parser.add_argument_group('target options')
	general_group = parser.add_argument_group('options')

	# Source
	source_group.add_argument('-s', '--source-svr',
		dest='s_svr',
		metavar='',
		help='set server for the source'
	)
	source_group.add_argument('-u', '--source-usr',
		dest='s_usr',
		metavar='',
		help='set user profile for the source'
	)
	source_group.add_argument('-p', '--source-pwd',
		dest='s_pwd',
		metavar='',
		help='set user password for the source'
	)
	source_group.add_argument('-l', '--source-lib',
		dest='s_lib',
		metavar='',
		help='set library for the source'
	)
	source_group.add_argument('-o', '--source-obj',
		dest='s_obj',
		metavar='',
		action='append',
		help='set object for the source - leave blank if whole library is saved'
	)
	source_group.add_argument('--source-obj-type',
		dest='s_obj_type',
		metavar='',
		action='append',
		choices=OBJECT_TYPE_LIST,
		help='set object type for the source'
	)
	source_group.add_argument('-c', '--source-config',
		dest='s_config',
		metavar='',
		help='read source config from file'
	)
	source_group.add_argument('--source-save-file',
		dest='s_save_file',
		metavar='',
		help='save OS/400 savfile locally all --target-* options will ignored'
	)
	source_group.add_argument('--source-job-log-file',
		dest='s_job_log_file',
		metavar='',
		help='save source servers job log to a file'
	)

	# Target
	target_group.add_argument('--target-release',
		metavar='',
		choices=RELEASE_LIST,
		dest='t_release',
		help='set OS/400 release for the target'
	)
	target_group.add_argument('-S', '--target-svr',
		dest='t_svr',
		metavar='',
		help='set server for the target'
	)
	target_group.add_argument('-U', '--target-usr',
		dest='t_usr',
		metavar='',
		help='set user profile for the target'
	)
	target_group.add_argument('-P', '--target-pwd',
		dest='t_pwd',
		metavar='',
		help='set user password for the target'
	)
	target_group.add_argument('-L', '--target-lib',
		dest='t_lib',
		metavar='',
		help='set library for the target'
	)
	target_group.add_argument('-C', '--target-config',
		dest='t_config',
		metavar='',
		help='read target config from file'
	)
	target_group.add_argument('--target-save-file',
		dest='t_save_file',
		metavar='',
		help='restore from OS/400 savfile stored locally all --source-* options will ignored'
	)
	target_group.add_argument('--target-restore-cmd',
		dest='t_restore_cmd',
		metavar='',
		help='command to run when object(s) / library is restored on target machine'
	)
	target_group.add_argument('--target-job-log-file',
		dest='t_job_log_file',
		metavar='',
		help='save target servers job log to a file'
	)

	# General
	general_group.add_argument('--source-job-log',
		dest='s_job_log',
		action='store_true',
		default=False,
		help='display source servers job log'
	)
	general_group.add_argument('--target-job-log',
		dest='t_job_log',
		action='store_true',
		default=False,
		help='display target servers job log'
	)
	general_group.add_argument('--no-prompt',
		dest='no_prompt',
		action='store_true',
		default=False,
		help='do not prompt on empty password and empty object'
	)
	general_group.add_argument('-v', '--verbose',
		dest='verbose',
		action='store_true',
		default=False,
		help='be more verbose/talkative during the operation'
	)
	general_group.add_argument('--trace',
		dest='trace',
		action='store_true',
		default=False,
		help='trace commands and other information'
	)
	general_group.add_argument('--silent',
		dest='silent',
		action='store_true',
		default=False,
		help='silent mode. Don\'t output warnings'
	)
	general_group.add_argument('--version',
		dest='version',
		action='store_true',
		default=False,
		help='output version information and exit'
	)
	general_group.add_argument('--help',
		dest='help',
		action='store_true',
		default=False,
		help='show this help message and exit'
	)

	args = parser.parse_args()

	if args.help:
		parser.print_help()
		sys.exit(0)
	if args.version:
		print_version()
		sys.exit(0)

	config = {
		# when verbose is True zipSeries will print information about the programs workfow
		'no-prompt': args.no_prompt,
		'trace': args.silent == False and args.trace,
		'verbose': args.silent == False and (args.verbose or args.trace),
		'silent': args.silent,
		'source': {
			'svr': args.s_svr,
			'usr': args.s_usr,
			'pwd': args.s_pwd, # (optional - will prompt when needed)
			'lib': args.s_lib,
			'obj': args.s_obj if args.s_obj != None and len(args.s_obj) else None, # (optional)
			'obj-type': args.s_obj_type if args.s_obj_type != None and len(args.s_obj_type) else None,
			'save-file': args.s_save_file,
			'job-log': args.s_job_log,
			'job-log-file': args.s_job_log_file
		},
		'target': {
			'release': args.t_release,
			'svr': args.t_svr,
			'usr': args.t_usr,
			'pwd': args.t_pwd, # (optional - will prompt when needed)
			'lib': args.t_lib,
			'save-file': args.t_save_file,
			'restore_cmd': args.t_restore_cmd,
			'job-log': args.t_job_log,
			'job-log-file': args.t_job_log_file
		}
	}

	if args.s_config:
		read_config_file(config, config['source'], '/etc/zipSeries/' + args.s_config + '.conf')

	if args.t_config:
		read_config_file(config, config['target'], '/etc/zipSeries/' + args.t_config + '.conf')

	if config['source']['obj-type'] == None:
		config['source']['obj-type'] = ["*ALL"]

	if config['target']['release'] == None:
		config['target']['release'] = "*CURRENT"

	check_config(config)

	# if no --target-save-file is specified and no --source-obj is specified
	#   there should be prompted for an object, simply because thats what you
	#   usually wants. Make sure that you can still export a full library
	if config['no-prompt'] == False and config['target']['save-file'] == None and config['source']['obj'] == None:
		obj = input('Enter object to save (*NONE = full library, space for multiply objects): ')
		if obj != '' and obj != '*NONE':
			config['source']['obj'] = obj.split(' ')

	as400 = AS400(config)

	if config['target']['save-file'] == None:
		if config['source']['pwd'] == None and config['no-prompt'] == False:
			config['source']['pwd'] = getpass.getpass('Enter source user password: ')

		as400.save()

	if config['source']['save-file'] == None:
		if config['target']['pwd'] == None and config['no-prompt'] == False:
			config['target']['pwd'] = getpass.getpass('Enter target user password: ')

		as400.restore(config['target']['save-file'])

# only run if called from command line
if __name__ == '__main__':
	main()
