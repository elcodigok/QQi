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

config = ConfigParser.RawConfigParser()
config.read('/home/dmaldonado/Proyectos/QQi/qqi.cnf')
internal_network = config.get('Lan', 'internal_network')
external_network = config.get('Lan', 'external_network')
internal_ip = config.get('Lan', 'internal_ip')
external_ip = config.get('Lan', 'external_ip')
iface_lan = config.get('Lan', 'iface_lan')
iface_wan = config.get('Lan', 'iface_wan')
admin_ip = config.get('Lan', 'admin_ip')
total_upload = config.get('Bandwidht', 'total_upload')
total_download = config.get('Bandwidht', 'total_download')
low_ceil = config.get('Bandwidht', 'low_ceil')
medium_ceil = config.get('Bandwidht', 'medium_ceil')
high_ceil = config.get('Bandwidht', 'high_ceil')
full_ceil = config.get('Bandwidht', 'full_ceil')
rate_percentage = config.get('Bandwidht', 'rate_percentage')
priorized_ports = config.get('Bandwidht', 'priorized_ports')


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


def configuration_firewall():
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
    os.system("iptables -t filter -P INPUT DROP")
    os.system("iptables -t filter -P FORWARD DROP")
    os.system("iptables -t filter -A INPUT -p icmp -j ACCEPT")
    os.system("iptables -t nat -A POSTROUTING -o " + iface_wan +
                " -j MASQUERADE")
    os.system("iptables -t filter -A FORWARD -d " + internal_network +
                " -j ACCEPT")
    os.system("iptables -t filter -A FORWARD -p tcp -m tcp --tcp-flags " +
                "SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu")
    os.system("iptables -t filter -A INPUT -p ALL -m state --state " +
                "ESTABLISHED,RELATED -j ACCEPT")
    os.system("iptables -t filter -A INPUT -s " + admin_ip +
                " -j ACCEPT")
    os.system("iptables -t filter -A INPUT -s 127.0.0.1 -j ACCEPT")
    os.system("iptables -t filter -A INPUT -s " + internal_ip +
                " -j ACCEPT")
    os.system("iptables -t filter -A INPUT -m udp -p udp --dport 53 -j ACCEPT")
    os.system("iptables -t filter -A INPUT -m tcp -p tcp --dport 53 -j ACCEPT")
    os.system("iptables -t filter -A INPUT -i " + iface_lan +
                " -p udp --sport 67:68 -j ACCEPT")
#    os.system("iptables -t mangle -N DOWNLOAD")
#    os.system("iptables -t mangle -A FORWARD -o " + iface_lan +
#                " -j DOWNLOAD")
#    os.system("iptables -t mangle -N UPLOAD")
#    os.system("iptables -t mangle -A FORWARD -o " + iface_wan +
#                " -j UPLOAD")
    for workstation in Puesto.select():
        if (workstation.politica):
            os.system("iptables -t filter -A FORWARD -s " + workstation.ip +
                        " -p icmp -m icmp -m mac --mac-source " +
                        workstation.mac + " -j ACCEPT")
            if (workstation.tipo == "proxy"):
                os.system("iptables -t nat -A PREROUTING -s " +
                        workstation.ip + " -m tcp -p tcp --dport 80 " +
                        "-j REDIRECT --to-port 3128")
                os.system("iptables -t filter -I INPUT -s " + workstation.ip +
                        " -m tcp -p tcp --dport 3128 -j ACCEPT")
            elif (workstation.tipo == "control"):
                os.system("iptables -t nat -A PREROUTING -s " +
                        workstation.ip + " -m tcp -p tcp --dport 80 " +
                        "-j REDIRECT --to-port 8080")
                os.system("iptables -t filter -A INPUT -s " + workstation.ip +
                        " -m tcp -p tcp --dport 8080 -j ACCEPT")
            elif (workstation.tipo == "port"):
                os.system("iptables -t filter -A FORWARD -s " + workstation.ip +
                        " -m mac --mac-source " + workstation.mac +
                        " -m tcp -p tcp -m multiport --dports 80,443 -j ACCEPT")

configuration_firewall()
