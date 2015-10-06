import uuid

class AS400:
	def __init__(self, config):
		self.source = config['source']
		self.target = config['target']
		self.save_file = None

	def save(self):
		# save_file is the file which the AS/400 library / object should be saved to
		self.save_file = ('/tmp/zipSeries-' + str(uuid.uuid1()) + '.zs4') if self.source['save-file'] == '' else self.source['save-file']
		
		# TODO Write FTP script

		print self.source

	def restore(self, save_file=None):
		# save_file is the saved file that should be restored on the AS/400
		if save_file == None:
			save_file = self.save_file
		# TODO Write FTP script
		
		print self.target

