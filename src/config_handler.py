import sys
import subprocess
from src.color import color

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
			sys.stderr.write('zipSeries: Missing option: \'' + color.BOLD + '-s, --source-svr server' + color.END + '\'\n')
			sys.exit(1)
		if config['source']['lib'] == None:
			sys.stderr.write('zipSeries: Missing option: \'' + color.BOLD + '-l, --source-lib library' + color.END + '\'\n')
			sys.exit(1)
		if config['source']['usr'] == None:
			sys.stderr.write('zipSeries: Missing option: \'' + color.BOLD + '-u, --source-usr user' + color.END + '\'\n')
			sys.exit(1)

	# Ignore all --target-* options if --source-save-file is specified
	if config['source']['save-file'] != None:
		if config['verbose']:
			print('zipSeries: using --source-save-file, all --target-* options are ignored')
	else:
		if config['target']['svr'] == None:
			sys.stderr.write('zipSeries: Missing option: \'' + color.BOLD + '-S, --target-svr server' + color.END + '\'\n')
			sys.exit(1)
		if config['target']['lib'] == None:
			sys.stderr.write('zipSeries: Missing option: \'' + color.BOLD + '-L, --target-lib library' + color.END + '\'\n')
			sys.exit(1)
		if config['target']['usr'] == None:
			sys.stderr.write('zipSeries: Missing option: \'' + color.BOLD + '-U, --target-usr user' + color.END + '\'\n')
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
			sys.stderr.write('zipSeries: cannot open \'' + color.BOLD + file + color.END + '\' for reading: No such file or directory\n')
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

		msg = line

		# If the config line cannot be parsed an error should be written
		if ' ' in line:
			split_index = line.index(' ')
			key = line[0:split_index]
			value = line[split_index+1:]

			if key in ['release', 'svr', 'usr', 'pwd', 'lib', 'obj', 'obj-type']:

				if config['verbose']:
					print('    setting key \'' + key + '\': \'' + value + '\'')

				if key == 'release' and value not in RELEASE_LIST:
					msg = 'release not supported: \'' + value + '\', supported releases: \'' + (', '.join(RELEASE_LIST)) + '\''
				elif key == 'obj-type' and value not in OBJECT_TYPE_LIST:
					msg = 'object type not supported: \'' + value + '\', supported types: \'' + (', '.join(OBJECT_TYPE_LIST)) + '\''

				else:
					if l_config[key] != None:
						print('zipSeries: key \'' + key + '\' is not used, allready set to \'' + l_config[key] + '\'')
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


