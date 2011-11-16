import sqlobject as sql

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
	ip   = sql.StringCol(length=15)
	mac = sql.StringCol(length=17)
	nombre = sql.StringCol(alternateID=True,length=15)
	usuario = sql.StringCol(length=15)
	tipo = sql.IntCol()
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
