import uuid
import sys
import binascii
import zipfile
import glob

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
		ret = str(int(ret, 16))	
	elif type == 'str':
		ret = binascii.unhexlify(ret).rstrip('\x00')

		ret = ret.strip()
	
	return ret

class AS400:
	def __init__(self, config):
		self.source = config['source']
		self.target = config['target']
		self.save_file = None
		self.config = config

	def __parse_ascii(self, ascii):
		meta = {
			'version': read_ascii(ascii, 4, 'int'),
			'checksum': read_ascii(ascii, 4, 'int'),
			'save_libl': read_ascii(ascii, 12),
			'save_type': read_ascii(ascii, 4, 'int'), # int 0, 1
			'upgrade_from': read_ascii(ascii, 256), # RELEASE_LIST
			'saved_by': read_ascii(ascii, 256),
			'save_timestamp': read_ascii(ascii, 32),
			'release': read_ascii(ascii, 11),
			'restore_cmd': read_ascii(ascii, 256), # not supported yet
			
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

	def save(self):
		# save_file is the file which the AS/400 library / object should be saved to
		self.save_file = ('/tmp/zipSeries-' + str(uuid.uuid1()) + '.zs4') if self.source['save-file'] == '' else self.source['save-file']
	
		root_dir = '/tmp/zipSeries-' + str(uuid.uuid1());

		# TODO Write FTP script

		print self.source

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

		# TODO Write FTP script
		
		print self.target

