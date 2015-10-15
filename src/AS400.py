import uuid
import sys
import binascii
import zipfile
import glob
import os
from ftplib import FTP

from src.config import UPGRADE_FROM, PGM_DESCRIPTION

INFO_FILE = 'zipInfo.4zi';

def unzip_file(file, dest):
	with zipfile.ZipFile(file, 'r') as z:
		z.extractall(dest)

def read_file_ascii(file):
	with open(file, 'rb') as f:
		content = f.read()
		return binascii.hexlify(content)

def read_ascii(ascii, i, type='str', trace=False):
	ret = ''
	while i > 0:
		if type == 'int':
			ret = ascii.pop(0) + ascii.pop(0) + ret
		elif type == 'str':
			ret += ascii.pop(0) + ascii.pop(0)

		i -= 1

	if type == 'int':
		ret = int(ret, 16)
	elif type == 'str':
		ret = binascii.unhexlify(ret).rstrip('\x00')

		ret = ret.strip()

	if trace:
		print('zipSeries: parsing config: ' + ret)

	return ret

def create_ascii(val, l):
	is_str = isinstance(val, str)

	l = l * 2

	if is_str:
		ret = val.encode('hex')[0:l-2]
	else:
		ret = hex(val)[2:l]
		if len(ret) % 2:
			ret = '0' + ret

	while len(ret) < l:
		ret += '0'

	return ret

def create_timestamp():
	import datetime
	import time

	return datetime.datetime.fromtimestamp(time.time()).strftime('%-m/%-d/%Y %-I:%-M:%-S %p').upper()

class AS400:
	contexts = {
		"NONE": 0,
		"SAVE": 10,
		"RESTORE": 20
	}
	def __init__(self, config):
		self.source = config['source']
		self.target = config['target']
		self.save_file = None
		self.config = config

		self.save_cleanup_job_log_file = False
		self.restore_cleanup_job_log_file = False
		
		self.context = AS400.contexts['NONE']
		
		_uuid = str(uuid.uuid1())
		self.uuid = 'zipSeries-' + _uuid
		self.save_uuid = 'zipSeries-save-' + _uuid
		self.restore_uuid = 'zipSeries-restore-' + _uuid

	def cl(self, cmd_name, data={}, quote=[]):

		cmd_name = os.path.dirname(os.path.realpath(__file__)) + '/../cl/' + cmd_name + '.clp'

		cmd = open(cmd_name, 'r').read()

		for prop, val in data.iteritems():
			if prop in quote:
				cmd = cmd.replace('&' + prop, '\''+ val +'\'')
			else:
				cmd = cmd.replace('&' + prop, val)

		cmd = cmd.strip()

		self.println('running iSeries (AS/400) command: ' + cmd, trace=True)

		return cmd

	def println(self, msg, error=False, verbose=False, trace=False):

		if (not verbose or self.config['verbose']) and (not trace or self.config['trace']):
			
			if self.context == self.contexts['SAVE']:
				prefix = 'zipSeries: save: '
			if self.context == self.contexts['RESTORE']:
				prefix = 'zipSeries: restore: '
			else:
				prefix = 'zipSeries: '
			
			if not error:
				print(prefix + msg)
			else:
				sys.stderr.write(prefix + 'error: ' + msg + '\n')

	def __getjoblog(self, ftp):

		as_ifs_job_log = self.uuid + '.joblog'

		if self.context == self.contexts['SAVE']:
			job_log_file = self.source['job-log-file']
			if self.source['job-log-file'] == None:
				job_log_file = '/tmp/' + self.save_uuid + '.joblog'
				self.source['job-log-file'] = job_log_file
				self.save_cleanup_job_log_file = True
		elif self.context == self.contexts['RESTORE']:
			job_log_file = self.target['job-log-file']
			if self.target['job-log-file'] == None:
				job_log_file = '/tmp/' + self.restore_uuid + '.joblog' 
				self.target['job-log-file'] = job_log_file
				self.restore_cleanup_job_log_file = True

		if job_log_file == None:
			raise Exception('no job_log_file defined')

		for cmd in self.cl('dspjoblog').splitlines():
			ftp.voidcmd('RCMD ' + cmd)

		ftp.voidcmd('RCMD ' + self.cl('cpytostmf', {
			'frommbr': '/QSYS.LIB/QTEMP.LIB/JOBLOG.FILE/JOBLOG.MBR',
			'tostmf': '/tmp/' + as_ifs_job_log,
			'stmfccsid': '1208'
		}, quote=['frommbr', 'tostmf']))

		with open(job_log_file, 'wb') as f:
			ftp.retrbinary('RETR /tmp/' + as_ifs_job_log, f.write)

		return job_log_file

	def __dspjoblog(self, error=False, source=False, target=False):
		if (not source or self.source['job-log']) and (not target or self.target['job-log']):
			if self.context == self.contexts['SAVE']:
				job_log_file = self.source['job-log-file'] if self.source['job-log-file'] else '/tmp/' + self.save_uuid + '.joblog'
			elif self.context == self.contexts['RESTORE']:
				job_log_file = self.target['job-log-file'] if self.target['job-log-file'] else '/tmp/' + self.restore_uuid + '.joblog' 

			with open(job_log_file) as f:
				for line in f:
					self.println(line.rstrip('\n'), error=error)

	def __parse_ascii(self, ascii):
		meta = {
			'version': read_ascii(ascii, 4, type='int', trace=self.config['trace']),
			'checksum': read_ascii(ascii, 4, type='int', trace=self.config['trace']),
			'save_lib': read_ascii(ascii, 12, trace=self.config['trace']),
			'save_type': read_ascii(ascii, 4, type='int', trace=self.config['trace']),
			'upgrade_from': read_ascii(ascii, 256, trace=self.config['trace']),
			'saved_by': read_ascii(ascii, 256, trace=self.config['trace']),
			'save_timestamp': read_ascii(ascii, 32, trace=self.config['trace']),
			'release': read_ascii(ascii, 11, trace=self.config['trace']),
			'restore_cmd': read_ascii(ascii, 256, trace=self.config['trace']),

			# the below is only used by zipSeries C++ dont use:
			'_svr': read_ascii(ascii, 256, trace=self.config['trace']),
			'_usr': read_ascii(ascii, 11, trace=self.config['trace']),
			'_lib': read_ascii(ascii, 11, trace=self.config['trace']),
			'_poster_file': read_ascii(ascii, 256, trace=self.config['trace']),
			'_poster_link': read_ascii(ascii, 256, trace=self.config['trace']),
			'_poster_stretch': read_ascii(ascii, 1, trace=self.config['trace']),
			'_tmp_name': read_ascii(ascii, 256, trace=self.config['trace'])
		}

		return meta

	def __create_ascii(self, tmp_file):

		checksum = 123478 # what is a checksum of? how is it calculated?

		save_type = 1 if self.source['obj'] != None else 0

		meta = {
			'version': create_ascii(101, 4),
			'checksum': create_ascii(checksum, 4),
			'save_lib': create_ascii(self.source['lib'], 12),
			'save_type': create_ascii(save_type, 4),
			'upgrade_from': create_ascii(UPGRADE_FROM, 256),
			'saved_by': create_ascii(PGM_DESCRIPTION, 256),
			'save_timestamp': create_ascii(create_timestamp(), 32),
			'release': create_ascii(self.target['release'], 11),
			'restore_cmd': create_ascii(self.target['restore_cmd'] or '', 256),

			# the below is only used by zipSeries C++ dont use:
			'_svr': create_ascii('', 256),
			'_usr': create_ascii('', 11),
			'_lib': create_ascii('*SAVLIB', 11),
			'_poster_file': create_ascii('', 256),
			'_poster_link': create_ascii('', 256),
			'_poster_stretch': create_ascii('', 1),
			'_tmp_name': create_ascii('C:\\qwerty\john\doe\\file.tmp', 256)
		}

		return (
			meta['version'] + meta['checksum'] + meta['save_lib'] + meta['save_type'] + meta['upgrade_from'] +
			meta['saved_by'] + meta['save_timestamp'] + meta['release'] + meta['restore_cmd'] +
			meta['_svr'] + meta['_usr'] + meta['_lib'] + meta['_poster_file'] + meta['_poster_link'] + meta['_poster_stretch'] + meta['_tmp_name']
		)

	def save(self):
		self.context = AS400.contexts['SAVE']
		# save_file is the file which the AS/400 library / object should be saved to
		self.save_file = (self.save_uuid + '.4zs') if self.source['save-file'] == None else self.source['save-file']

		root_dir = '/tmp/' + self.save_uuid;

		os.mkdir(root_dir)

		as_ifs_save_file = self.save_uuid + '.savf'
		tmp_file = os.path.join(root_dir, 'file.tmp')

		exit = 0

		try:
			self.println('connection to ' + self.source['svr'], verbose=True)

			ftp = FTP(self.source['svr'])

			ftp.set_pasv(True)
			ftp.set_debuglevel(0)

			ftp.login(user=self.source['usr'], passwd=self.source['pwd'])

			self.println('connected to ' + self.source['svr'], verbose=True)

			try:
				ftp.voidcmd('site namefmt 1')
				self.println('creating savefile', verbose=True)
				ftp.voidcmd('RCMD ' + self.cl('crtsavf'))

				if self.source['obj'] == None:
					self.println('saving library to savefile', verbose=True)
					ftp.voidcmd('RCMD ' + self.cl('savlib', {
						'lib': self.source['lib'],
						'release': self.target['release']
					}))
				else:
					self.println('saving object(s) to savefile', verbose=True)
					ftp.voidcmd('RCMD ' + self.cl('savobj', {
						'obj': ' '.join(self.source['obj']),
						'objtype': ' '.join(self.source['obj-type']),
						'lib': self.source['lib'],
						'release': self.target['release']
					}))

				self.println('copying save file to streamfile', verbose=True)
				ftp.voidcmd('RCMD ' + self.cl('cpytostmf', {
					'frommbr': '/QSYS.LIB/QTEMP.LIB/ZS.FILE',
					'tostmf': '/tmp/' + as_ifs_save_file,
					'stmfccsid': '*STMF'
				}, quote=['frommbr', 'tostmf']))

				self.println('downloading streamfile', verbose=True)

				with open(tmp_file, 'wb') as f:
					ftp.retrbinary('RETR /tmp/' + as_ifs_save_file, f.write)

				ftp.delete('/tmp/' + as_ifs_save_file)
		
			except Exception as e:
				self.println(str(e), error=True)
				exit = 1

		except Exception as e:
			self.println(str(e))
			exit = 1
		
		self.__getjoblog(ftp)
		ftp.quit()

		if exit == 0:
			ascii = self.__create_ascii(os.path.join(root_dir, tmp_file))

			with open(os.path.join(root_dir, INFO_FILE), 'wb') as f:
				f.write(binascii.unhexlify(ascii))

			self.println('creating zip file', verbose=True)
			zip = zipfile.ZipFile(self.save_file, 'w')
			self.println('zip: adding file ' + tmp_file, trace=True)
			zip.write(tmp_file, os.path.basename(tmp_file))
			self.println('zip: adding file ' + os.path.join(root_dir, INFO_FILE), trace=True)
			zip.write(os.path.join(root_dir, INFO_FILE), INFO_FILE)

			zip.close()

		# Remove temp files / directories
		self.println('cleaning up...', verbose=True)

		self.println('removing ' + tmp_file, trace=True)
		try:
			os.remove(tmp_file)
		except Exception as e:
			pass

		self.println('removing ' + os.path.join(root_dir, INFO_FILE), trace=True)
		try:
			os.remove(os.path.join(root_dir, INFO_FILE))
		except Exception as e:
			pass

		self.println('removing ' + root_dir, trace=True)
		try:
			os.rmdir(root_dir)
		except Exception as e:
			pass

		if exit == 0:
			self.println('done', verbose=True)
			self.__dspjoblog(source=True)
			self.context = AS400.contexts['NONE']
		else:
			self.__dspjoblog(error=True)
			self.context = AS400.contexts['NONE']

		if self.save_cleanup_job_log_file:
			self.println('removing ' + self.source['job-log-file'], trace=True)
			try:
				os.remove(self.source['job-log-file'])
			except Exception as e:
				pass

		if exit != 0:
			sys.exit(exit)

	def restore(self, save_file=None):
		self.context = AS400.contexts['RESTORE']
		# save_file should be restored on the AS/400
		if save_file == None:
			save_file = self.save_file

		root_dir = '/tmp/' + self.restore_uuid;

		unzip_file(save_file, dest=root_dir)

		self.println('unzipping \'' + save_file + '\' to \'' + root_dir + '\'', verbose=True)

		meta = self.__parse_ascii(list(read_file_ascii(os.path.join(root_dir,  INFO_FILE))))
		meta['restore_file'] = glob.glob(root_dir + '/*.tmp')[0]
		as_ifs_save_file = '/tmp/' + self.restore_uuid + '.savf'

		exit = 0

		try:
			self.println('connection to ' + self.target['svr'], verbose=True)

			ftp = FTP(self.target['svr'])

			ftp.set_pasv(True)
			ftp.set_debuglevel(0)

			ftp.login(user=self.target['usr'], passwd=self.target['pwd'])

			self.println('connected to ' + self.target['svr'], verbose=True)

			try:
				ftp.voidcmd('site namefmt 1')

				ftp.storbinary('STOR ' + as_ifs_save_file, open(meta['restore_file'], 'r'))

				ftp.voidcmd('RCMD ' + self.cl('cpyfrmstmf', {
					'fromstmf': as_ifs_save_file
				}, quote=['fromstmf']))

				# Object

				if meta['save_type'] == 1:
					ftp.voidcmd('RCMD ' + self.cl('rstobj', {
						'savlib': meta['save_lib'],
						'rstlib': self.target['lib']
					}))
				# lib
				else:
					ftp.voidcmd('RCMD ' + self.cl('rstlib', {
						'savlib': meta['save_lib'],
						'rstlib': self.target['lib']
					}))

				# Run restore command if specified
				if meta['restore_cmd'] != '':
					self.println('running iSeries (AS/400) restore command: ' + meta['restore_cmd'], verbose=True)
					ftp.voidcmd('RCMD ' + meta['restore_cmd'])

			except Exception as e:
				self.println(str(e), error=True)
				exit = 1

		except Exception as e:
			self.println(str(e), error=True)
			exit = 1

		self.__getjoblog(ftp)
		ftp.quit()

		# Remove temp files / directories
		self.println('cleaning up...', verbose=True)

		self.println('removing ' + root_dir, trace=True)
		try:
			os.remove(root_dir)
		except Exception as e:
			pass

		if exit == 0: 
			self.println('done', verbose=True)
			self.context = AS400.contexts['NONE']
			self.__dspjoblog(target=True)
		else:
			self.context = AS400.contexts['NONE']
		
		if self.restore_cleanup_job_log_file:
			self.println('removing ' + self.target['job-log-file'], trace=True)
			try:
				os.remove(self.target['job-log-file'])
			except Exception as e:
				pass

		if exit != 0:
			sys.exit(exit)

