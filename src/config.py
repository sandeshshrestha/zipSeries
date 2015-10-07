import os
import json

with open(os.path.dirname(os.path.realpath(__file__)) + '/../data/target_releases.json') as data_file:
	RELEASE_LIST = json.load(data_file)
with open(os.path.dirname(os.path.realpath(__file__)) + '/../data/object_types.json') as data_file:
	OBJECT_TYPE_LIST = json.load(data_file)

UPGRADE_FROM = 'https://github.com/ginkoms/zipSeries'


PGM_DESCRIPTION = 'Copy libraries / objects from one iSeries (AS/400) to another running the same (or lower) release of OS/400 as source.' 
