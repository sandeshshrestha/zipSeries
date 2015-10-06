import os
import json

with open(os.path.dirname(os.path.realpath(__file__)) + '/../target_releases.json') as data_file:
	RELEASE_LIST = json.load(data_file)
with open(os.path.dirname(os.path.realpath(__file__)) + '/../object_types.json') as data_file:
	OBJECT_TYPE_LIST = json.load(data_file)


