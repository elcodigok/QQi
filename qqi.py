#!/usr/bin/env python
""" Sistema de control de acceso wifi """
# -*- coding: utf-8 -*-

import commands
import gettext
import os
import ConfigParser
import form.configuration as conf
import form.menu as menu
import form.workstation as works
import form.user as users
import form.group as groups


try:
	import snack
except ImportError:
	raise ImportError, gettext.gettext('newt library not installed')

try:
	import sqlobject as sql
except ImportError:
	raise ImportError, gettext.gettext('SQLObject library not installed')

__connection__ = 'sqlite:///etc/qqi/qqi.db'


# Definicion de los puestos de trabajo
class Puesto(sql.SQLObject):
	ip = sql.StringCol(length=15)
	mac = sql.StringCol(length=17)
	nombre = sql.StringCol(alternateID=True, length=15)
	usuario = sql.StringCol(length=15)
	#tipo = sql.IntCol()
	tipo = sql.EnumCol(enumValues=('proxy', 'control', 'port', 'no'))
	politica = sql.BoolCol()
	grupos = sql.RelatedJoin('Grupo')
	direcciones = sql.RelatedJoin('Direccion')
	servicios = sql.RelatedJoin('Servicio')


# Definicion de los grupos
class Grupo(sql.SQLObject):
	nombre = sql.StringCol(alternateID=True, length=15)
	descripcion = sql.StringCol(length=25)
	tipo = sql.EnumCol(enumValues=('low', 'medium', 'high', 'full'))
	web = sql.EnumCol(enumValues=('proxy', 'control', 'port', 'no'))
	tcp = sql.StringCol(length=50)
	udp = sql.StringCol(length=50)
	puestos = sql.RelatedJoin('Puesto')
	usuarios = sql.RelatedJoin('Usuario')
	direcciones = sql.RelatedJoin('Direccion')


# Definicion de las URL
class Direccion(sql.SQLObject):
	nombre = sql.StringCol(length=15)
	dominio = sql.StringCol(length=30)
	puestos = sql.RelatedJoin('Puesto')
	grupos = sql.RelatedJoin('Grupo')
	usuarios = sql.RelatedJoin('Usuario')


# Definicion de los usuarios
class Usuario(sql.SQLObject):
	nombre = sql.StringCol(length=15)
	nombrecompleto = sql.StringCol(length=30)
	clave = sql.StringCol(length=15)
	activo = sql.BoolCol()
	politica = sql.BoolCol()
	grupos = sql.RelatedJoin('Grupo')
	direcciones = sql.RelatedJoin('Direccion')


# Definicion de los Servicios
class Servicio(sql.SQLObject):
	nombre = sql.StringCol(length=15)
	descripcion = sql.StringCol(length=15)
	puerto_desde = sql.IntCol()
	puerto_hasta = sql.IntCol()
	protocolos = sql.StringCol(length=3)
	puestos = sql.RelatedJoin('Puesto')


def reset():
	""" Resetar la base de datos """
	Puesto.dropTable(ifExists=True)
	Puesto.createTable()
	Grupo.dropTable(ifExists=True)
	Grupo.createTable()
	Direccion.dropTable(ifExists=True)
	Direccion.createTable()
	Usuario.dropTable(ifExists=True)
	Usuario.createTable()
	Servicio.dropTable(ifExists=True)
	Servicio.createTable()


def menu_principal():
	""" Funcion de menu principal """
	salir = False
	while not salir:
		firstMenu = menu.Menu(gettext.gettext('QQinternet'),
					columnas - 40, lineas - 24,
					opciones=(
						gettext.gettext('Workstation admin'),
						gettext.gettext('Users admin'),
						gettext.gettext('Groups admin'),
						gettext.gettext('Services admin'),
						gettext.gettext('Domain admin'),
						gettext.gettext('Configuration'),
						gettext.gettext('Create backup'),
						gettext.gettext('Apply changes'),
						gettext.gettext('Disable system'),
						gettext.gettext('Exit'),),
					titulo='QQi 0.1', screen=principal, posicion=0)
		opcion = firstMenu.showMenu()
		if opcion == 0:
			workstationQuery = Puesto.select()
			workstationList = works.WorkstationAdmin(principal)
			listOption = workstationList.showList(workstationQuery)
			if (listOption[0] == "add"):
				workstationList = works.WorkstationAdmin(principal)
				workstationAdd = workstationList.addWorkstation(
								gettext.gettext('Add Worwstation'),
								gettext.gettext('New Workstation'),
								principal, table=Puesto)
			elif (listOption[0] == "modify"):
				record = listOption[1]
				workstationList = works.WorkstationAdmin(principal)
				workstationModify = workstationList.editWorkstation(
								gettext.gettext('Modify Workstation'),
								gettext.gettext('Edit Workstation'),
								principal, Puesto, record)
			elif (listOption[0] == "delete"):
				record = listOption[1]
				workstationList = works.WorkstationAdmin(principal)
				workstationDelete = workstationList.deleteWorkstation(
								principal,
								Puesto,
								record)
			else:
				print gettext.gettext("Invalid Options")
		elif opcion == 1:
			userQuery = Usuario.select()
			userList = users.UserAdmin(principal)
			listOption = userList.showList(userQuery)
			if (listOption[0] == "add"):
				userList = users.UserAdmin(principal)
				userAdd = userList.addUser(
								gettext.gettext('Add User'),
								gettext.gettext('New User'),
								principal, table=Usuario)
			elif (listOption[0] == "modify"):
				record = listOption[1]
				userList = users.UserAdmin(principal)
				userModify = userList.editUser(
								gettext.gettext('Modify Users'),
								gettext.gettext('Edit User'),
								principal, Usuario, record)
			elif (listOption[0] == "delete"):
				record = listOption[1]
				userList = users.UserAdmin(principal)
				userDelete = userList.deleteUser(
								principal,
								Usuario,
								record)
			else:
				print gettext.gettext("Invalid Options")
		elif opcion == 2:
			groupQuery = Grupo.select()
			groupList = groups.GroupAdmin(principal)
			listOption = groupList.showList(groupQuery)
			if (listOption[0] == "add"):
				groupList = groups.GroupAdmin(principal)
				groupAdd = groupList.addGroup(
								gettext.gettext('Add Group'),
								gettext.gettext('New Group'),
								principal, table=Grupo)
			elif (listOption[0] == "modify"):
				record = listOption[1]
				groupList = groups.GroupAdmin(principal)
				groupModify = groupList.editGroup(
								gettext.gettext('Modify Groups'),
								gettext.gettext('Edit Group'),
								principal, Grupo, record)
			elif (listOption[0] == "delete"):
				record = listOption[1]
				groupList = groups.GroupAdmin(principal)
				groupDelete = groupList.deleteGroup(
								principal,
								Grupo,
								record)
			else:
				print gettext.gettext("Invalid Options")
		elif opcion == 3:
			serviceMenu = menu.Menu(gettext.gettext('Services Admin'),
					columnas=(columnas - 40), lineas=(lineas - 24),
					opciones=(
						gettext.gettext('List Services'),
						gettext.gettext('Add Services'),
						gettext.gettext('Remove Services'),
						gettext.gettext('Exit'),),
					titulo="Administration Services", screen=principal, posicion=0)
			serviceOption = serviceMenu.showMenu()
		elif opcion == 4:
			domainMenu = menu.Menu(gettext.gettext('Domain Admin'),
					columnas=(columnas - 40), lineas=(lineas - 24),
					opciones=(
						gettext.gettext('List Domain'),
						gettext.gettext('Add Domain'),
						gettext.gettext('Remove Domain'),
						gettext.gettext('Exit'),),
					titulo="Administration Domain", screen=principal, posicion=0)
			domainOption = domainMenu.showMenu()
		elif opcion == 5:
			config = conf.Configuracion(principal,
					'/home/dmaldonado/Proyectos/QQi/qqi.cnf')
			config.configurar()
		elif opcion == 6:
			salida = os.system('tar cvfz /var/backups/qqi-0.1.tar.gz ' +
							'/usr/local/sbin/qqi.py ' +
							'/usr/local/sbin/firewall.py ' +
							'/etc/init.d/qqi ' +
							'/usr/share/locale/es/LC_MESSAGES/qqi.mo ' +
							'/usr/local/etc/qqi/*')
		elif opcion == 7:
			salida = os.system('/usr/local/sbin/firewall.py')
			#salida = os.system('/etc/init.d/freeradius restart')
			#salida = os.system('/etc/init.d/dnsmasq restart')
		elif opcion == 8:
			deshabilitar()
		elif opcion == 9:
			principal.finish()
			salir = True

if __name__ == '__main__':
	gettext.bindtextdomain('QQi')
	gettext.textdomain('QQi')
	(l, c) = str.split(commands.getoutput('stty size'))
	(lineas, columnas) = (int(l), int(c))
	lineas, comlumnas = lineas or 24, columnas or 79
	nombre = 'QQinternet'
	version = '0.1'
	principal = snack.SnackScreen()
	#reset()
	menu_principal()
