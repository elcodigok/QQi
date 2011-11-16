from snack import *
import gettext
import os
import ConfigParser

class Configuracion():
	""" Clase para la configuracion de los parametros basicos del sistem """
	def __init__(self, pantalla, archivo):
		if not archivo:
			#self.archivo = "parametros.conf"
			self.archivo = "qqi.cnf"
		else:
			self.archivo = archivo
		if not pantalla:
			pantalla = snack.SnackScreen()
		else:
			self.pantalla = pantalla

	def modificar(self):
		""" Funcion para modificacion de parametros de configuracion"""
		config = ConfigParser.RawConfigParser()
		config.read(self.archivo)
		red_interna = config.get('Lan', 'red_interna')
		red_externa = config.get('Lan', 'red_externa')
		ip_interno = config.get('Lan', 'ip_interno')
		ip_externo = config.get('Lan', 'ip_externo')
		interface_lan = config.get('Lan', 'interface_lan')
		interface_externa = config.get('Lan', 'interface_externa')
		ip_administrador = config.get('Lan', 'ip_administrador')
		total_subida = config.get('Bandwidht', 'total_subida')
		total_bajada = config.get('Bandwidht', 'total_bajada')
		low_ceil = config.get('Bandwidht', 'low_ceil')
		medium_ceil = config.get('Bandwidht', 'medium_ceil')
		high_ceil = config.get('Bandwidht', 'high_ceil')
		full_ceil = config.get('Bandwidht', 'full_ceil')
		porcentaje_rate = config.get('Bandwidht', 'porcentaje_rate')
		puertos_priorizados = config.get('Bandwidht', 'puertos_priorizados')
		
		(boton, valores) = EntryWindow(self.pantalla,
			gettext.gettext("Configuration"), 
			gettext.gettext("Input here the basic parameter for the system"),
			[(gettext.gettext('Internal network:'), red_interna), 
			(gettext.gettext('External network:'), red_externa), 
			(gettext.gettext('Internal IP:'), ip_interno),
			(gettext.gettext('External IP:'), ip_externo),
			(gettext.gettext('Internal interface:'), interface_lan),
			(gettext.gettext('External interface:'), interface_externa),
			(gettext.gettext('Administrative IP:'), ip_administrador),
			(gettext.gettext('Upload bandwidht:'), total_subida),
			(gettext.gettext('Download bandwidht:'), total_bajada),
			(gettext.gettext('Ceil for low class:'), low_ceil),
			(gettext.gettext('Ceil for medium class:'), medium_ceil),
			(gettext.gettext('Ceil for high class:'), high_ceil),
			(gettext.gettext('Ceil for full class:'), full_ceil),
			(gettext.gettext('Rate pecent guaranty:'), porcentaje_rate),
			(gettext.gettext('Priorized ports:'), puertos_priorizados)])
		config = ConfigParser.RawConfigParser()
		config.add_section('Lan')
		config.set('Lan', 'red_interna', valores[0])
		config.set('Lan', 'red_externa', valores[1])
		config.set('Lan', 'ip_interno', valores[2])
		config.set('Lan', 'ip_externo', valores[3])
		config.set('Lan', 'interface_lan', valores[4])
		config.set('Lan', 'interface_externa', valores[5])
		config.set('Lan', 'ip_administrador', valores[6])
		config.add_section('Bandwidht')
		config.set('Bandwidht', 'total_subida', valores[7])
		config.set('Bandwidht', 'total_bajada', valores[8])
		config.set('Bandwidht', 'low_ceil', valores[9])
		config.set('Bandwidht', 'medium_ceil', valores[10])
		config.set('Bandwidht', 'high_ceil', valores[11])
		config.set('Bandwidht', 'full_ceil', valores[12])
		config.set('Bandwidht', 'porcentaje_rate', valores[13])
		config.set('Bandwidht', 'puertos_priorizados', valores[14])
		if boton == 'ok':
			configfile = open(self.archivo, 'wb')
			config.write(configfile)


	def crear(self):
		""" Funcion para creacion de Configuracion de parametros """
		(boton, valores) = snack.EntryWindow(self.pantalla,
			gettext.gettext("Configuration"), 
			gettext.gettext("Input here the basic parameter for the system"),
			[gettext.Catalog('Internal network:'), 
			gettext.Catalog('External network:'), 
			gettext.Catalog('Internal IP:'),
			gettext.Catalog('External IP:'),
			gettext.Catalog('Internal interface:'),
			gettext.Catalog('External interface:'),
			gettext.Catalog('Administrative IP:'),
			gettext.Catalog('Upload bandwidht:'),
			gettext.Catalog('Download bandwidht:'),
			gettext.Catalog('Ceil for low class:'),
			gettext.Catalog('Ceil for medium class:'),
			gettext.Catalog('Ceil for high class:'),
			gettext.Catalog('Ceil for full class:'),
			gettext.Catalog('Rate pecent guaranty:'),
			gettext.Catalog('Priorized ports:')])
		config = ConfigParser.RawConfigParser()
		config.add_section('Lan')
		config.set('Lan', 'red_interna', valores[0])
		config.set('Lan', 'red_externa', valores[1])
		config.set('Lan', 'ip_interno', valores[2])
		config.set('Lan', 'ip_externo', valores[3])
		config.set('Lan', 'interface_lan', valores[4])
		config.set('Lan', 'interface_externa', valores[5])
		config.set('Lan', 'ip_administrador', valores[6])
		config.add_section('Bandwidht')
		config.set('Bandwidht', 'total_subida', valores[7])
		config.set('Bandwidht', 'total_bajada', valores[8])
		config.set('Bandwidht', 'low_ceil', valores[9])
		config.set('Bandwidht', 'medium_ceil', valores[10])
		config.set('Bandwidht', 'high_ceil', valores[11])
		config.set('Bandwidht', 'full_ceil', valores[12])
		config.set('Bandwidht', 'porcentaje_rate', valores[13])
		config.set('Bandwidht', 'puertos_priorizados', valores[14])
		if boton == 'ok':
			configfile = open(self.archivo, 'wb') 
			config.write(configfile)

	def configurar(self):
		""" Creacion o modificacion de archivo de Configuracion """
		if os.path.exists(self.archivo):
			self.modificar()
		else:
			self.crear()
