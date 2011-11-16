from snack import *
import gettext
import os
import ConfigParser

class WorkstationAdmin:
	def __init__(self, screen):
		self.screen = screen
	
	def showList(self, query):
		self.query = query
		self.listElement = Listbox(height=12, width=50, returnExit=1)
		self.buttons = ButtonBar(self.screen, (("View", "view"), ("Delete", "delete"), ("Exit", "exit")))
		for record in self.query:
			self.listElement.append(record.usuario + ", " + record.nombre + ", " + record.ip, record)
		self.grid = GridForm(self.screen, gettext.gettext('Workstation List'), 1, 2)
		self.grid.add(self.listElement, 0, 0)
		self.grid.add(self.buttons, 0, 1, growx=1)
		rta = self.grid.runOnce()
		return rta
