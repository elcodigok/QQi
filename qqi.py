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

try:
	import snack
except ImportError: 
	raise ImportError, gettext.gettext("newt library not installed")
try:
	import sqlobject as sql
except ImportError:
	raise ImportError, gettext.gettext("SQLObject library not installed")

__connection__ = 'sqlite:///etc/qqi/qqi.db'

#class Usuario(sql.SQLObject):
	#"""Definicion de clase para usuarios"""
	#ip = sql.StringCol(length=15)
	#mac = sql.StringCol(length=17)
	#usuario = sql.StringCol(length=30)
	#clave = sql.StringCol(length=30)
	#habilitado = sql.BoolCol()
	#tipo = sql.EnumCol(enumValues=('low', 'medium', 'high', 'full')) 
	#web = sql.EnumCol(enumValues=('proxy', 'control', 'port', 'no'))
	#tcp = sql.StringCol(length=50)
	#udp = sql.StringCol(length=50)

# Definicion de los puestos de trabajo
class Puesto(sql.SQLObject):
	ip = sql.StringCol(length=15)
	mac = sql.StringCol(length=17)
	nombre = sql.StringCol(alternateID=True,length=15)
	usuario = sql.StringCol(length=15)
	#tipo = sql.IntCol()
	tipo = sql.EnumCol(enumValues=('proxy', 'control', 'port', 'no'))
	politica = sql.BoolCol()
	grupos = sql.RelatedJoin('Grupo')
	direcciones = sql.RelatedJoin('Direccion')
	servicios = sql.RelatedJoin('Servicio')

# Definicion de los grupos
class Grupo(sql.SQLObject):
	nombre = sql.StringCol(alternateID=True,length=15)
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
			workstationMenu = menu.Menu(gettext.gettext('Workstation Admin'),
					 columnas -40, lineas -24,
					 opciones=(
						gettext.gettext('List Workstation'),
						gettext.gettext('Add Workstation'),
						gettext.gettext('Remove Workstation'),
						gettext.gettext('Exit'),),
					titulo="Administration Workstations", screen=principal, posicion=0)
			workstationOption = workstationMenu.showMenu()
			if (workstationOption == 0):
				workstationQuery = Puesto.select()
				workstationList = works.WorkstationAdmin(principal)
				listOption = workstationList.showList(workstationQuery)
			elif (workstationOption == 1):
				workstationList = works.WorkstationAdmin(principal)
				#options = ['nombre'.capitalize(), 'usuario'.capitalize()]
				workstationAdd = workstationList.addWorkstation('Add Worwstation', 'New Workstation', principal, table=Puesto)
				#print workstationAdd
		elif opcion == 1:
			userMenu = menu.Menu(gettext.gettext('Users Admin'),
					 columnas -40, lineas -24,
					 opciones=(
						gettext.gettext('List Users'),
						gettext.gettext('Add Users'),
						gettext.gettext('Remove Users'),
						gettext.gettext('Exit'),),
					titulo="Administration Users", screen=principal, posicion=0)
			userOption = userMenu.showMenu()
		elif opcion == 2:
			groupMenu = menu.Menu(gettext.gettext('Groups Admin'),
					 columnas -40, lineas -24,
					 opciones=(
						gettext.gettext('List Groups'),
						gettext.gettext('Add Groups'),
						gettext.gettext('Remove Groups'),
						gettext.gettext('Exit'),),
					titulo="Administration Groups", screen=principal, posicion=0)
			groupOption = groupMenu.showMenu()
		elif opcion == 3:
			serviceMenu = menu.Menu(gettext.gettext('Services Admin'),
					 columnas -40, lineas -24,
					 opciones=(
						gettext.gettext('List Services'),
						gettext.gettext('Add Services'),
						gettext.gettext('Remove Services'),
						gettext.gettext('Exit'),),
					titulo="Administration Services", screen=principal, posicion=0)
			serviceOption = serviceMenu.showMenu()
		elif opcion == 4:
			domainMenu = menu.Menu(gettext.gettext('Domain Admin'),
					 columnas -40, lineas -24,
					 opciones=(
						gettext.gettext('List Domain'),
						gettext.gettext('Add Domain'),
						gettext.gettext('Remove Domain'),
						gettext.gettext('Exit'),),
					titulo="Administration Domain", screen=principal, posicion=0)
			domainOption = domainMenu.showMenu()
		elif opcion == 5:
			config = conf.Configuracion(principal, '/home/dmaldonado/Proyectos/QQi/qqi.cnf')
			config.configurar()
		elif opcion == 6:
			salida = os.system('tar cvfz /var/backups/qqi-0.1.tar.gz ' + 
							'/usr/local/sbin/thaya.py ' + 
							'/usr/local/sbin/firewall.py ' + 
							'/etc/init.d/thaya ' +
							'/usr/share/locale/es/LC_MESSAGES/thaya.mo ' +
							'/usr/local/etc/thaya/*')
		elif opcion == 7:
			salida = os.system('/usr/local/sbin/firewall.py')
			salida = os.system('/etc/init.d/freeradius restart')
			salida = os.system('/etc/init.d/dnsmasq restart')
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
	lineas, comlumnas  = lineas or 24,  columnas or 79
	nombre = 'QQinternet'
	version = '0.1'
	principal = snack.SnackScreen()
	#reset()
	menu_principal()