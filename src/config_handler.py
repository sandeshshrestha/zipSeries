import sys
import subprocess

# check_config makes sure that all config options are specified.
#  only the passwords can be left blank, they will be prompted later on
def check_config(config):
	# Source Config
	# Ignore all --source-* options if --source-save-file is specified
	if config['target']['save-file'] != None:
		if config['verbose']:
			print('zipSeries: using --target-save-file, all --source-* options are ignored')
	else:
		if config['source']['svr'] == None:
			sys.stderr.write('zipSeries: Missing option: \'-s, --source-svr server\'\n')
			sys.exit(1)
		if config['source']['lib'] == None:
			sys.stderr.write('zipSeries: Missing option: \'-l, --source-lib library\'\n')
			sys.exit(1)
		if config['source']['usr'] == None:
			sys.stderr.write('zipSeries: Missing option: \'-u, --source-usr user\'\n')
			sys.exit(1)

	# Ignore all --target-* options if --source-save-file is specified
	if config['source']['save-file'] != None:
		if config['verbose']:
			print('zipSeries: using --source-save-file, all --target-* options are ignored')
	else:
		if config['target']['svr'] == None:
			sys.stderr.write('zipSeries: Missing option: \'-S, --target-svr server\'\n')
			sys.exit(1)
		if config['target']['lib'] == None:
			sys.stderr.write('zipSeries: Missing option: \'-L, --target-lib library\'\n')
			sys.exit(1)
		if config['target']['usr'] == None:
			sys.stderr.write('zipSeries: Missing option: \'-U, --target-usr user\'\n')
			sys.exit(1)

# read_config_file will call itself again with the sudo=True argument,
#   this is so we will only run as sudo if necessary.
def read_config_file(config, l_config, file, sudo=False):
	cmd = ['cat', file]

	if sudo:
		cmd.insert(0, 'sudo')

	try:
		f_config = subprocess.check_output(cmd, stderr=subprocess.STDOUT).splitlines()

	except Exception as e:
		if not sudo:
			return read_config_file(config, l_config, file, True)
		else:
			sys.stderr.write('zipSeries: cannot open \'' + file + '\' for reading: No such file or directory\n')
			sys.exit(0)

	parse_config_file(config, l_config, file, f_config)


def parse_config_file(config, l_config, file, f_config):

	if config['verbose']:
		print('zipSeries: Parsing config file: ' + file)

	for i, line in enumerate(f_config):
		line = line.strip()
		# Allow empty lines and allow comments (line starting with '#')
		if line == '' or line[0] == '#':
			continue

		if config['verbose']:
			print('zipSeries: processing:' + line)

		err_msg = None

		# If the config line cannot be parsed an error should be written
		if ' ' in line:
			split_index = line.index(' ')
			key = line[0:split_index]
			value = line[split_index+1:]
			
			if l_config[key] != None:
				print('zipSeries: key \'' + key + '\' is allready set to \'' + l_config[key] + '\'')
				continue

			# Release 
			if key == 'release':
				if value in RELEASE_LIST:
					l_config[key] = value
				else:
					err_msg = 'release not supported: \'' + value + '\', supported releases: \'' + (', '.join(RELEASE_LIST)) + '\''

			# TODO Support a space seperated list of object types
			elif key == 'obj-type':
				if value in OBJECT_TYPE_LIST:
					l_config[key] = value.split(' ')
				else:
					err_msg = 'object type not supported: \'' + value + '\', supported types: \'' + (', '.join(OBJECT_TYPE_LIST)) + '\''
			
			# Standard values (cannot be validated)
			elif key in ['svr', 'usr', 'pwd', 'lib', 'obj']:
				l_config[key] = value
			else:
				err_msg = 'key not recornized: \'' + key + '\' in line \'' + line + '\''

		if err_msg != None:
			sys.stderr.write('zipSeries: cannot parse \'' + file + '\':\n')
			sys.stderr.write('Line (' + str(i+1) + '): ' + msg + '\n')
			sys.exit(1)


