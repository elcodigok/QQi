from snack import *
import gettext
#import os
#import ConfigParser
import sqlobject as sql


class WorkstationAdmin:

    def __init__(self, screen):
        self.screen = screen
        self.cadena = ""

    def showList(self, query):
        self.query = query
        self.listElement = Listbox(height=15, width=77, returnExit=1)
        self.buttons = ButtonBar(self.screen, (
                                        (gettext.gettext("Group"), "group"),
                                        (gettext.gettext("Add"), "add"),
                                        (gettext.gettext("Modify"), "modify"),
                                        (gettext.gettext("Delete"), "delete"),
                                        (gettext.gettext("Return"), "return")))
        if (self.query.count() > 0):
            for record in self.query:
                item = "%-20s %-15s %6s %-15s %-5s" % (record.usuario, record.nombre, record.ip, record.tipo, record.politica)
                self.listElement.append(item, record)
        else:
            self.listElement.append(gettext.gettext("There are no records"), 0)
        self.grid = GridForm(self.screen, gettext.gettext('Workstation List'), 1, 2)
        self.grid.add(self.listElement, 0, 0)
        self.grid.add(self.buttons, 0, 1, growx=1)
        rta = self.grid.runOnce()
        return (self.buttons.buttonPressed(rta), self.listElement.current())

    def listWorkstationGroup(self, id_workstation):
        record = id_workstation.grupos
        list = Listbox(height=10, width=47, returnExit=1)
        buttons = ButtonBar(self.screen, (
                    (gettext.gettext("Add"), "add"),
                    (gettext.gettext("Delete"), "delete"),
                    (gettext.gettext("Back"), "back")))
        for r in record:
            list.append(r.nombre, r)
        g = GridForm(self.screen, gettext.gettext("Groups List"), 1, 2)
        g.add(list, 0, 0)
        g.add(buttons, 0, 1, growx=1)
        rta = g.runOnce()
        options = buttons.buttonPressed(rta)
        if (options == "add"):
            print "****************************************************"
        elif (options == "delete"):
            id_workstation.removeGrupo(list.current().id)


    def ntEntryWindow(self, screen, title, text, prompts, allowCancel=1,
                        width=40, entryWidth=20,
                        buttons=['Ok', 'Cancel'], help=None,
                        table=None, record=None, edit=None):
        #self.bb = ButtonBar(screen, buttons);
        self.bb = ButtonBar(screen, (
                                (gettext.gettext("Save"), "save"),
                                (gettext.gettext("Cancel"), "cancel"),
                                    ))
        t = TextboxReflowed(width, text)
        count = len(self.table.sqlmeta.columnList)
        sg = Grid(2, count)
        count = 0
        entryList = []
        for n in self.table.sqlmeta.columnList:
            if type(n) == sql.SOStringCol:
                if (edit == True):
                    e = Entry(entryWidth, text=record._SO_getValue(n.name))
                else:
                    e = Entry(entryWidth)
            elif type(n) == sql.SOIntCol:
                if (edit == True):
                    e = Entry(entryWidth, text=record._SO_getValue(n.name))
                else:
                    e = Entry(entryWidth)
            elif type(n) == sql.SOBoolCol:
                if n.default == True:
                    e = Checkbox(gettext.gettext("Enabled"), isOn=1)
                else:
                    e = Checkbox(gettext.gettext("Enabled"), isOn=0)
            elif type(n) == sql.SOEnumCol:
                indice = 1
                contador = len(n.enumValues)
                self.cadena = "("
                for i in n.enumValues:
                    if indice == 1:
                        self.cadena += '(\"%s\", \"%s\", %d)' % (i.capitalize(),
                                                                i,
                                                                1)
                    else:
                        self.cadena += '(\"%s\", \"%s\", %d)' % (i.capitalize(),
                                                                i,
                                                                0)
                    if indice < contador:
                        self.cadena += ', '
                    indice += 1
                self.cadena += ")"
                #print self.cadena
                #e = RadioBar(self.screen, self.cadena)
                e = RadioBar(self.screen, (
                                    (gettext.gettext("Proyx"), "proxy", 1),
                                    (gettext.gettext("Control"), "control", 0),
                                    (gettext.gettext("Port"), "port", 0),
                                    (gettext.gettext("No"), "no", 0)
                                    ))
            else:
                if (edit == True):
                    e = Entry(entryWidth, text=record._SO_getValue(n.name))
                else:
                    e = Entry(entryWidth)
            sg.setField(Label(n.name.capitalize() + ":"), 0, count, padding=(0, 0, 1, 1), anchorLeft=1)
            sg.setField(e, 1, count, anchorLeft=1)
            count += 1
            entryList.append(e)

        g = GridFormHelp(screen, title, help, 1, 3)
        g.add(t, 0, 0, padding=(0, 0, 0, 1))
        g.add(sg, 0, 1, padding=(0, 0, 0, 1))
        g.add(self.bb, 0, 2, growx=1)
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
            dict_campos = {}
            for x in range(len(campos)):
                dict_campos[campos[x]] = rta[1][x]
            registro = self.table(**dict_campos)
        return rta

    def editWorkstation(self, title, text, screen, table, registro):
        self.screen = screen
        self.title = title
        self.text = text
        self.table = table
        self.registro = registro
        columnas = [col.name.capitalize() for col in self.table.sqlmeta.columnList]
        rta = self.ntEntryWindow(self.screen, self.title, self.text, columnas, self.table, record=self.registro, edit=True)
        if rta[0] == "save":
            campos = [col.name for col in self.table.sqlmeta.columnList]
            dict_campos = {}
            for x in range(len(campos)):
                dict_campos[campos[x]] = rta[1][x]
            self.registro.set(**dict_campos)
            #print dict_campos
        #return rta
        #print dir(self.registro)
        #print self.registro._SO_getValue("ip")

    def deleteWorkstation(self, screen, table, registro):
        self.screen = screen
        self.table = table
        self.registro = registro
        confirmation = ButtonChoiceWindow(self.screen,
                                    gettext.gettext('Confirm'),
                                    gettext.gettext('are you sure to remove'),
                                    [gettext.gettext('Ok'),
                                    gettext.gettext('Cancel')], 60)
        if (confirmation == 'ok'):
            self.table.delete(self.registro.id)
