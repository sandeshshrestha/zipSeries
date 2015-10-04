class AS400:
	def __init__(self, config):
		self.source = config['source']
		self.target = config['target']

	def save(self):
		# save_file is the file which the AS/400 library / object should be saved to
		save_file = ('/tmp/zipSeries-' + str(uuid.uuid1()) + '.zs4') if self.target['save-file'] == '' else self.target['save-file'];
		self.source['save-file'] = save_file
	
		# TODO Write FTP script

		print self.source

	def restore(self, file):
		# save_file is the saved file that should be restored on the AS/400
		save_file = self.source['save-file']
		
		# TODO Write FTP script
		
		print self.target

