from snack import *
import gettext
import os
import ConfigParser
import sqlobject as sql


class WorkstationAdmin:
	def __init__(self, screen):
		self.screen = screen
		self.cadena = ""
	
	def showList(self, query):
		self.query = query
		self.listElement = Listbox(height=15, width=77, returnExit=1)
		self.buttons = ButtonBar(self.screen, ((gettext.gettext("Add"), "add"), 
												(gettext.gettext("Modify"), "modify"), 
												(gettext.gettext("Delete"), "delete"), 
												(gettext.gettext("Return"), "return")))
		for record in self.query:
			item = "%-20s %-15s %6s %-15s %-5s" % (record.usuario, record.nombre, record.ip, record.tipo, record.politica)
			self.listElement.append(item, record)
		self.grid = GridForm(self.screen, gettext.gettext('Workstation List'), 1, 2)
		self.grid.add(self.listElement, 0, 0)
		self.grid.add(self.buttons, 0, 1, growx=1)
		rta = self.grid.runOnce()
		return rta
	
	def ntEntryWindow(self, screen, title, text, prompts, allowCancel = 1, width = 40, 
		entryWidth = 20, buttons = [ 'Ok', 'Cancel' ], help = None, table = None):
		"""
		EntryWindow(screen, title, text, prompts, allowCancel = 1, width = 40,
		entryWidth = 20, buttons = [ 'Ok', 'Cancel' ], help = None):
		"""
		#self.bb = ButtonBar(screen, buttons);
		self.bb = ButtonBar(screen, (("Save", "save"), ("Cancel", "cancel")));
		t = TextboxReflowed(width, text)
		count = len(self.table.sqlmeta.columnList)
		sg = Grid(2, count)
		count = 0
		entryList = []
		for n in self.table.sqlmeta.columnList:
			if type(n) == sql.SOStringCol:	
				e = Entry(entryWidth)
			elif type(n) == sql.SOIntCol:
				e = Entry(entryWidth)
			elif type(n) == sql.SOBoolCol:
				if n.default == True:
					e = Checkbox("Enabled", isOn = 1)
				else:
					e = Checkbox("Enabled", isOn = 0)
			elif type(n) == sql.SOEnumCol:
				#e = RadioBar(self.screen,(("Proxy   ", 1, 0), ("Control ", 2, 0), ("Inactivo",0,1)))
				indice = 1
				contador = len(n.enumValues)
				self.cadena = "("
				for i in n.enumValues:
					if indice == 1:
						self.cadena += '(\"%s\", \"%s\", %d)' % (i.capitalize(), i, 1)
					else:
						self.cadena += '(\"%s\", \"%s\", %d)' % (i.capitalize(), i, 0)
					if indice < contador:
						self.cadena += ', '
					indice += 1
				self.cadena += ")"
				#print self.cadena
				#e = RadioBar(self.screen, '%s') % (self.cadena)
				e = RadioBar(self.screen, (("Proyx", "proxy", 1), ("Control", "control", 0), ("Port", "port", 0), ("No", "no", 0)))
			else:
				e = Entry(entryWidth)
			sg.setField(Label(n.name.capitalize() + ":"), 0, count, padding = (0, 0, 1, 1), anchorLeft = 1)
			sg.setField(e, 1, count, anchorLeft = 1)
			count += 1
			entryList.append(e)
		
		g = GridFormHelp(screen, title, help, 1, 3)
		g.add(t, 0, 0, padding = (0, 0, 0, 1))
		g.add(sg, 0, 1, padding = (0, 0, 0, 1))
		g.add(self.bb, 0, 2, growx = 1)
		result = g.runOnce()
		entryValues = []
		count = 0
		for n in self.table.sqlmeta.columnList:
			if type(n) == sql.SOEnumCol:
				entryValues.append(entryList[count].getSelection())
			else:
				entryValues.append(entryList[count].value())
			count = count + 1
		return (self.bb.buttonPressed(result), tuple(entryValues))
	
	def addWorkstation(self, title, text, screen, table):
		self.screen = screen
		self.title = title
		self.text = text
		#self.option = option
		self.table = table
		columnas = [col.name.capitalize() for col in self.table.sqlmeta.columnList]
		rta = self.ntEntryWindow(self.screen, self.title, self.text, columnas, self.table)
		if rta[0] == "save":
			campos= [col.name for col in self.table.sqlmeta.columnList]
			dict_campos={}
			for x in range(len(campos)):
				dict_campos[campos[x]] = rta[1][x]
			registro=self.table(**dict_campos)
		return rta

