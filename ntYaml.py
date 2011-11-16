#!/usr/bin/env python

import yaml
from yaml import Loader

class ntYaml():
	def __init__(self, filename):
		self.filename = filename

	def setVersion(self, version=None):
		self.version = version
	
	def getVersion(self):
		return self.version

	def load(self):
		nt_file = open(self.filename, 'r')
		self.load = yaml.load(nt_file)

	def dump(self):
		print yaml.dump(self.load)

	def has_key(self, key):
		self.key = key
		return self.load.has_key(self.key)

	def clear(self):
		self.load.clear()

	def getValues(self):
		return self.load.values()

	def getKeys(self):
		return self.load.keys()
	
	def getCopy(self):
		return self.load.copy()

#nty = ntYaml("ejemplo.yaml")
#nty.load()
#nty.dump()
#print nty.has_key("hola")
#print nty.getValues()
#print nty.getKeys()
#nty.clear()
