import sys
import subprocess

# check_config makes sure that all config options are specified.
#  only the passwords can be left blank, they will be prompted later on
def check_config(config):
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


