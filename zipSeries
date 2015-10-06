#!/usr/bin/env python

# zipSeries 1.2.6
# Copyright (C) 2015 System & Method A/S Denmark
# Released under the MIT license
#
# Written by Andreas Louv <and@sitemule.com>

VERSION = '1.2.6'

import sys
import os
import subprocess
import getpass
import uuid
import json
from src.color import color
from src.AS400 import AS400

with open(os.path.dirname(os.path.realpath(__file__)) + '/target_releases.json') as data_file:
	RELEASE_LIST = json.load(data_file)
with open(os.path.dirname(os.path.realpath(__file__)) + '/object_types.json') as data_file:
	OBJECT_TYPE_LIST = json.load(data_file)

def print_version():
	print 'zipSeries ' + VERSION
	print ''
	print 'Copyright (C) 2015 System & Method A/S Denmark'
	print 'Released under the MIT license'
	print ''
	print 'Written by Andreas Louv <and@sitemule.com>'

# read_config_file will call itself again with the sudo=True argument,
#   this is so we will only run as sudo if necessary.
def read_config_file(config, l_config, file, sudo=False):
	cmd = ['cat', file]

	if sudo:
		cmd.insert(0, 'sudo')

	try:
		f_config = subprocess.check_output(cmd, stderr=subprocess.STDOUT).splitlines()

	except Exception, e:
		if not sudo:
			return read_config_file(config, l_config, file, True)
		else:
			sys.stderr.write('zipSeries: cannot open \'' + color.BOLD + file + color.END + '\' for reading: No such file or directory\n')
			sys.exit(0)

	parse_config_file(config, l_config, file, f_config)


def parse_config_file(config, l_config, file, f_config):

	if config['verbose']:
		print 'zipSeries: Parsing config file: ' + file

	for i, line in enumerate(f_config):
		line = line.strip()
		# Allow empty lines and allow comments (line starting with '#')
		if line == '' or line[0] == '#':
			continue

		msg = line

		# If the config line cannot be parsed an error should be written
		if ' ' in line:
			split_index = line.index(' ')
			key = line[0:split_index]
			value = line[split_index+1:]

			if key in ['release', 'srv', 'usr', 'pwd', 'libl', 'obj', 'obj-type']:

				if config['verbose']:
					print 'zipSeries: reading key: \'' + key + '\''

				if key == 'release' and value not in RELEASE_LIST:
					msg = 'release not supported: \'' + value + '\', supported releases: \'' + (', '.join(RELEASE_LIST)) + '\''
				elif key == 'obj-type' and value not in OBJECT_TYPE_LIST:
					msg = 'object type not supported: \'' + value + '\', supported types: \'' + (', '.join(OBJECT_TYPE_LIST)) + '\''
					
				else:
					l_config[key] = value
					# Continue the iteration to prevent the error fallthough
					continue
			else:
				msg = 'key not recornized: \'' + color.BOLD + key + color.END + '\' in line \'' + line + '\''

		# Fallthough to error print
		sys.stderr.write('zipSeries: cannot parse \'' + color.BOLD + file + color.END + '\':\n')
		sys.stderr.write('Line (' + str(i+1) + '): ' + msg + '\n')
		sys.exit(1)

def main():
	import argparse
	parser = argparse.ArgumentParser(
		description='Copy libraries / objects from one iSeries (AS/400) to another running the same (or lower) release of OS/400 as source.', 
		usage='usage: zipSeries [--version] | [--help] | [OPTION]...',
		formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=100),
		add_help=False
	)

	source_group = parser.add_argument_group('source options')
	target_group = parser.add_argument_group('target options')
	general_group = parser.add_argument_group('options')
	
	# Source
	source_group.add_argument('-s', '--source-srv', 
		dest='s_srv',
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
	source_group.add_argument('-l', '--source-libl', 
		dest='s_libl', 
		metavar='',
		help='set library for the source'
	)
	source_group.add_argument('-o', '--source-obj', 
		dest='s_obj', 
		metavar='',
		help='set object for the source - leave blank if whole library is saved'
	)
	source_group.add_argument('--source-obj-type',
		dest='s_obj_type',
		metavar='',
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

	# Target
	target_group.add_argument('--target-release', 
		default='*CURRENT',
		metavar='',
		choices=RELEASE_LIST,
		dest='t_release', 
		help='set OS/400 release for the target'
	)
	target_group.add_argument('-S', '--target-srv', 
		dest='t_srv', 
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
	target_group.add_argument('-L', '--target-libl', 
		dest='t_libl', 
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

	# General
	general_group.add_argument('-v', '--verbose', 
		dest='verbose', 
		action='store_true', 
		default=False, 
		help='be more verbose/talkative during the operation'
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
		'verbose': args.verbose,
		'source': {
			'srv': args.s_srv,
			'usr': args.s_usr,
			'pwd': args.s_pwd, # (optional - will prompt when needed)
			'libl': args.s_libl,
			'obj': args.s_obj, # (optional)
			'obj-type': args.s_obj_type,
			'save-file': args.s_save_file
		},
		'target': {
			'release': args.t_release,
			'srv': args.t_srv,
			'usr': args.t_usr,
			'pwd': args.t_pwd, # (optional - will prompt when needed)
			'libl': args.t_libl,
			'save-file': args.t_save_file
		}
	}


	if args.s_config:
		read_config_file(config, config['source'], '/etc/zipSeries/' + args.s_config + '.conf')

	if args.t_config:
		read_config_file(config, config['target'], '/etc/zipSeries/' + args.t_config + '.conf')

	checkConfig(config)

	as400 = AS400(config)
	
	if config['target']['save-file'] == None:
		if config['source']['pwd'] == None:
			config['source']['pwd'] = getpass.getpass('Enter source user password: ')
		try:
			as400.save()
		except Exception, e:
			sys.stderr.write('zipSeries: Error happened while making savefile:\n');
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)

	if config['source']['save-file'] == None:
		if config['target']['pwd'] == None:
			config['target']['pwd'] = getpass.getpass('Enter target user password: ')
		try:
			as400.restore(config['target']['save-file'])
		except Exception, e:
			sys.stderr.write('zipSeries: Error happened while restoring savefile:\n');
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)

# checkConfig makes sure that all config options are specified.
#  only the passwords can be left blank, they will be prompted later on
def checkConfig(config):
	# Source Config
	# Ignore all --source-* options if --source-save-file is specified
	if config['target']['save-file'] != None:
		if config['verbose']:
			print 'zipSeries: using --target-save-file, all --source-* options are ignored'
	else:
		if config['source']['srv'] == None:
			sys.stderr.write('zipSeries: Missing option: \'' + color.BOLD + '-s, --source-srv=server' + color.END + '\'\n')
			sys.exit(1)
		if config['source']['libl'] == None:
			sys.stderr.write('zipSeries: Missing option: \'' + color.BOLD + '-l, --source-libl=library' + color.END + '\'\n')
			sys.exit(1)
		if config['source']['usr'] == None:
			sys.stderr.write('zipSeries: Missing option: \'' + color.BOLD + '-u, --source-usr=user' + color.END + '\'\n')
			sys.exit(1)

	# Ignore all --target-* options if --source-save-file is specified
	if config['source']['save-file'] != None:
		if config['verbose']:
			print 'zipSeries: using --target-save-file, all --target-* options are ignored'
	else:
		if config['target']['srv'] == None:
			sys.stderr.write('zipSeries: Missing option: \'' + color.BOLD + '-S, --target-srv=server' + color.END + '\'\n')
			sys.exit(1)
		if config['target']['libl'] == None:
			sys.stderr.write('zipSeries: Missing option: \'' + color.BOLD + '-L, --target-libl=library' + color.END + '\'\n')
			sys.exit(1)
		if config['target']['usr'] == None:
			sys.stderr.write('zipSeries: Missing option: \'' + color.BOLD + '-U, --target-usr=user' + color.END + '\'\n')
			sys.exit(1)

# only run if called from command line
if __name__ == '__main__':
	main()
