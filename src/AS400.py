import uuid
import sys
import binascii
import zipfile
import glob
import os
from ftplib import FTP

from config import UPGRADE_FROM, PGM_DESCRIPTION

INFO_FILE = 'zipInfo.4zi';

def unzip_file(file, dest):
	with zipfile.ZipFile(file, 'r') as z:
		z.extractall(dest)

def read_file_ascii(file):
	with open(file, 'rb') as f:
		content = f.read()
		return binascii.hexlify(content)

def read_ascii(ascii, i, type='str'):
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
	def __init__(self, config):
		self.source = config['source']
		self.target = config['target']
		self.save_file = None
		self.config = config

	def cl(self, cmd_name, data={}, quote=[]):
	
		cmd_name = os.path.dirname(os.path.realpath(__file__)) + '/../cl/' + cmd_name + '.clp'

		cmd = open(cmd_name, 'r').read()

		for prop, val in data.iteritems():
			if prop in quote:
				cmd = cmd.replace('&' + prop, '\''+ val +'\'')
			else:
				cmd = cmd.replace('&' + prop, val)

		cmd = cmd.strip()
		
		if self.config['verbose']:
			print 'zipSeries: running iSeries (AS/400) command: ' + cmd
		
		return cmd

	def __parse_ascii(self, ascii):
		meta = {
			'version': read_ascii(ascii, 4, 'int'),
			'checksum': read_ascii(ascii, 4, 'int'),
			'save_libl': read_ascii(ascii, 12),
			'save_type': read_ascii(ascii, 4, 'int'),
			'upgrade_from': read_ascii(ascii, 256),
			'saved_by': read_ascii(ascii, 256),
			'save_timestamp': read_ascii(ascii, 32),
			'release': read_ascii(ascii, 11),
			'restore_cmd': read_ascii(ascii, 256),
			
			# the below is only used by zipSeries C++ dont use:
			'_srv': read_ascii(ascii, 256),
			'_usr': read_ascii(ascii, 11),
			'_libl': read_ascii(ascii, 11),
			'_poster_file': read_ascii(ascii, 256),
			'_poster_link': read_ascii(ascii, 256),
			'_poster_stretch': read_ascii(ascii, 1),
			'_tmp_name': read_ascii(ascii, 256)
		}
	
		if self.config['verbose']:
			print 'zipSeries: save file config:'
			print '    version: \'' + str(meta['version']) + '\''
			print '    checksum: \'' + str(meta['checksum']) + '\''
			print '    save_libl: \'' + str(meta['save_libl']) + '\''
			print '    save_type: \'' + str(meta['save_type']) + '\''
			print '    upgrade_from: \'' + str(meta['upgrade_from']) + '\''
			print '    saved_by: \'' + str(meta['saved_by']) + '\''
			print '    save_timestamp: \'' + str(meta['save_timestamp']) + '\''
			print '    release: \'' + str(meta['release']) + '\''
			print '    restore_cmd: \'' + str(meta['restore_cmd']) + '\''
		
		return meta

	def __create_save_file(self, root_dir):
		as_ifs_save_file = 'zipSeries-' + str(uuid.uuid1()) + '.savf'
		tmp_file = root_dir + '/' + 'file.tmp'

		try: 
			if self.config['verbose']:
				print 'zipSeries: connection to ' + self.source['srv']

			ftp = FTP(self.source['srv'])
			
			ftp.set_pasv(True)
			ftp.set_debuglevel(0)

			ftp.login(user=self.source['usr'], passwd=self.source['pwd'])
	
			if self.config['verbose']:
				print 'zipSeries: connected to ' + self.source['srv']

			try: 
				ftp.voidcmd('site namefmt 1')
				ftp.voidcmd('RCMD ' + self.cl('crtsavf'))

				if self.source['obj'] == None:
					ftp.voidcmd('RCMD ' + self.cl('savlib', {
						'libl': self.source['libl'],
						'release': self.target['release'] 
					}))
				else:
					ftp.voidcmd('RCMD ' + self.cl('savobj', {
						'obj': self.source['obj'],
						'libl': self.source['libl'],
						'release': self.target['release'] 
					}))

				ftp.voidcmd('RCMD ' + self.cl('cpytostmf', {
					'frommbr': '/QSYS.LIB/QTEMP.LIB/ZS.FILE',
					'tostmf': '/tmp/' + as_ifs_save_file,
					'stmfccsid': '*STMF'
				}, quote=['frommbr', 'tostmf']))

				with open(tmp_file, 'wb') as f:
					ftp.retrbinary('RETR /tmp/' + as_ifs_save_file, f.write)

			except Exception as e:
				sys.stderr.write('zipSeries: error: ' + str(e) + '\n')
				sys.stderr.write('zipSeries: JOBLOG: \n')
			
				# TODO display job log
				sys.exit(1)
				ftp.voidcmd('RCMD ' + self.cl('dspjoblog'))
				ftp.voidcmd('RCMD ' + self.cl('crtpf'))
				ftp.voidcmd('RCMD ' + self.cl('cpysplf'))
				ftp.voidcmd('RCMD ' + self.cl('cpytostmf', {
					'frommbr': '/QSYS.LIB/QTEMP.LIB/ZS_ERR.FILE/ZS_ERR.MBR',
					'tostmf': 'zs_' + str(uuid.uuid1()),
					'stmfccsid': '1208'
				}, quote=['frommbr', 'tostmf']))
				ftp.quit()

				sys.exit(1)

		except Exception as e:
			sys.stderr.write('zipSeries: error: ' + str(e) + '\n')

		try:
			ftp.quit()
		except Exception as e:
			pass
			
		return tmp_file

	def __create_ascii(self, tmp_file):
	
		checksum = 123478 # what is a checksum of? how is it calculated?
		
		save_type = 1 if self.source['obj'] != None else 0

		meta = {
			'version': create_ascii(101, 4),
			'checksum': create_ascii(checksum, 4),
			'save_libl': create_ascii(self.source['libl'], 12),
			'save_type': create_ascii(save_type, 4), 
			'upgrade_from': create_ascii(UPGRADE_FROM, 256),
			'saved_by': create_ascii(PGM_DESCRIPTION, 256),
			'save_timestamp': create_ascii(create_timestamp(), 32),
			'release': create_ascii(self.target['release'], 11),
			'restore_cmd': create_ascii(self.target['restore_cmd'], 256), # not supported yet
			
			# the below is only used by zipSeries C++ dont use:
			'_srv': create_ascii('', 256),
			'_usr': create_ascii('', 11),
			'_libl': create_ascii('*SAVLIB', 11),
			'_poster_file': create_ascii('', 256),
			'_poster_link': create_ascii('', 256),
			'_poster_stretch': create_ascii('', 1),
			'_tmp_name': create_ascii('C:\\qwerty\john\doe\\file.tmp', 256)
		}

		return (
			meta['version'] + meta['checksum'] + meta['save_libl'] + meta['save_type'] + meta['upgrade_from'] + 
			meta['saved_by'] + meta['save_timestamp'] + meta['release'] + meta['restore_cmd'] + 
			meta['_srv'] + meta['_usr'] + meta['_libl'] + meta['_poster_file'] + meta['_poster_link'] + meta['_poster_stretch'] + meta['_tmp_name']
		)

	def save(self):
		# save_file is the file which the AS/400 library / object should be saved to
		self.save_file = ('/tmp/zipSeries-' + str(uuid.uuid1()) + '.4zs') if self.source['save-file'] == None else self.source['save-file']
	
		root_dir = '/tmp/zipSeries-' + str(uuid.uuid1());

		os.mkdir(root_dir)

		tmp_file = self.__create_save_file(root_dir)
		ascii = self.__create_ascii(root_dir + '/' + tmp_file)

		with open(root_dir + '/' + INFO_FILE, 'wb') as f:
			f.write(binascii.unhexlify(ascii))

		zip = zipfile.ZipFile(self.save_file, 'w')
		zip.write(tmp_file, os.path.basename(tmp_file))
		zip.write(root_dir + '/' + INFO_FILE, INFO_FILE)
		zip.close()

		os.remove(tmp_file)
		os.remove(root_dir + '/' + INFO_FILE)
		os.rmdir(root_dir)
	
	def restore(self, save_file=None):
		# save_file should be restored on the AS/400
		if save_file == None:
			save_file = self.save_file
		
		root_dir = '/tmp/zipSeries-' + str(uuid.uuid1());

		unzip_file(save_file, dest=root_dir)
	
		if self.config['verbose']:
			print 'zipSeries: unzipping \'' + save_file + '\' to \'' + root_dir + '\'' 

		meta = self.__parse_ascii(list(read_file_ascii(root_dir + '/' + INFO_FILE)))
	
		meta['restore_file'] = glob.glob(root_dir + '/*.tmp')[0]

		as_ifs_save_file = '/tmp/zipSeries-' + str(uuid.uuid1()) + '.savf'
		
		try: 
			if self.config['verbose']:
				print 'zipSeries: connection to ' + self.target['srv']

			ftp = FTP(self.target['srv'])
			
			ftp.set_pasv(True)
			ftp.set_debuglevel(0)

			ftp.login(user=self.target['usr'], passwd=self.target['pwd'])
	
			if self.config['verbose']:
				print 'zipSeries: connected to ' + self.target['srv']

			try: 
				ftp.voidcmd('site namefmt 1')

				ftp.storbinary('STOR ' + as_ifs_save_file, open(meta['restore_file'], 'r'))

				ftp.voidcmd('RCMD ' + self.cl('cpyfrmstmf', {
					'fromstmf': as_ifs_save_file
				}, quote=['fromstmf']))
				
				# Object

				if meta['save_type'] == 1:
					ftp.voidcmd('RCMD ' + self.cl('rstobj', {
						'savlib': meta['save_libl'],
						'rstlib': self.target['libl']
					}))
				# Libl
				else:
					ftp.voidcmd('RCMD ' + self.cl('rstlib', {
						'savlib': meta['save_libl'],
						'rstlib': self.target['libl']
					}))

			except Exception as e:
				sys.stderr.write('zipSeries: error: ' + str(e) + '\n')
				sys.stderr.write('zipSeries: JOBLOG: \n')
		
				# TODO display job log
				sys.exit(1)
				ftp.voidcmd('RCMD ' + self.cl('dspjoblog'))
				ftp.voidcmd('RCMD ' + self.cl('crtpf'))
				ftp.voidcmd('RCMD ' + self.cl('cpysplf'))
				ftp.voidcmd('RCMD ' + self.cl('cpytostmf', {
					'frommbr': '/QSYS.LIB/QTEMP.LIB/ZS_ERR.FILE/ZS_ERR.MBR',
					'tostmf': 'zs_' + str(uuid.uuid1()),
					'stmfccsid': '1208'
				}, quote=['frommbr', 'tostmf']))
				ftp.quit()

				sys.exit(1)

		except Exception as e:
			sys.stderr.write('zipSeries: error: ' + str(e) + '\n')

		try:
			ftp.quit()
		except Exception as e:
			pass


		print self.target

