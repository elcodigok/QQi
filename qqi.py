#!/usr/bin/env python
# -*- coding: utf-8 -*-

import commands
import gettext
import os
import logging
import ConfigParser
import form.configuration as conf
import form.menu as menu
import form.workstation as works
import form.user as users
import form.group as groups
import form.url as urls
import form.service as services


try:
    import snack
except ImportError:
    print gettext.gettext('newt library not installed')

try:
    import sqlobject as sql
except ImportError:
    print gettext.gettext('SQLObject library not installed')

__connection__ = 'sqlite:///etc/qqi/qqi.db'
file_log = '/etc/qqi/qqi.log'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=file_log)

logger = logging.getLogger(file_log)


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
    logger.info(gettext.gettext('Init aplication QQi'))
    while not salir:
        firstMenu = menu.Menu(gettext.gettext('QQinternet'),
                                columnas - 40, lineas - 24,
                                opciones=(
                                    gettext.gettext('Workstation admin'),
                                    gettext.gettext('Users admin'),
                                    gettext.gettext('Groups admin'),
                                    gettext.gettext('Domain admin'),
                                    gettext.gettext('Services admin'),
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
            urlQuery = Direccion.select()
            urlList = urls.UrlAdmin(principal)
            listOption = urlList.showList(urlQuery)
            if (listOption[0] == "add"):
                urlList = urls.UrlAdmin(principal)
                urlAdd = urlList.addUrl(
                                gettext.gettext('Add URL'),
                                gettext.gettext('New URL or Domain'),
                                principal, table=Direccion)
            elif (listOption[0] == "modify"):
                record = listOption[1]
                urlList = urls.UrlAdmin(principal)
                urlModify = urlList.editUrl(
                                gettext.gettext('Modify URL'),
                                gettext.gettext('Edit URL or Domain'),
                                principal, Direccion, record)
            elif (listOption[0] == "delete"):
                record = listOption[1]
                urlList = urls.UrlAdmin(principal)
                urlDelete = urlList.deleteUrl(
                                principal,
                                Direccion,
                                record)
            else:
                print gettext.gettext("Invalid Options")
        elif opcion == 4:
            serviceQuery = Servicio.select()
            serviceList = services.ServiceAdmin(principal)
            listOption = serviceList.showList(serviceQuery)
            if (listOption[0] == "add"):
                serviceList = services.ServiceAdmin(principal)
                serviceAdd = serviceList.addService(
                                    gettext.gettext('Add Service'),
                                    gettext.gettext('New Service'),
                                    principal, table=Servicio)
            elif (listOption[0] == "modify"):
                record = listOption[1]
                serviceList = services.ServiceAdmin(principal)
                serviceModify = serviceList.editService(
                                    gettext.gettext('Modify Service'),
                                    gettext.gettext('Edit Service'),
                                    principal, Servicio, record)
            elif (listOption[0] == "delete"):
                record = listOption[1]
                serviceList = services.ServiceAdmin(principal)
                serviceDelete = serviceList.deleteService(
                                    principal,
                                    Servicio,
                                    record)
            else:
                print gettext.gettext("Invalid Options")
        elif opcion == 5:
            config = conf.Configuracion(principal,
                            '/home/dmaldonado/Proyectos/QQi/qqi.cnf',
                            '/etc/qqi/qqi.log')
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
            logger.info(gettext.gettext('Close QQi'))
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
