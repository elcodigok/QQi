#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gettext
import os
import logging
import ConfigParser


try:
    import sqlobject as sql
except ImportError:
    print gettext.gettext('SQLObject library not installed')

__connection__ = 'sqlite:///etc/qqi/qqi.db'

config = ConfigParser.RawConfigParser()
config.read('/home/dmaldonado/Proyectos/QQi/qqi.cnf')
internal_network = config.get('Lan', 'internal_network')
external_network = config.get('Lan', 'external_network')
internal_ip = config.get('Lan', 'internal_ip')
external_ip = config.get('Lan', 'external_ip')
iface_lan = config.get('Lan', 'iface_lan')
iface_wan = config.get('Lan', 'iface_wan')
admin_ip = config.get('Lan', 'admin_ip')
total_upload = int(config.get('Bandwidht', 'total_upload'))
total_download = int(config.get('Bandwidht', 'total_download'))
low_ceil = int(config.get('Bandwidht', 'low_ceil'))
medium_ceil = int(config.get('Bandwidht', 'medium_ceil'))
high_ceil = int(config.get('Bandwidht', 'high_ceil'))
full_ceil = int(config.get('Bandwidht', 'full_ceil'))
rate_percentage = int(config.get('Bandwidht', 'rate_percentage'))
priorized_ports = config.get('Bandwidht', 'priorized_ports')
file_log = config.get('Configuration', 'log_file')

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


def rule_tc(id_clase, ceil, numip, puertos=''):
    """ Funcion de creacion de regla para TC """
    # Reglas de control de ancho de banda bajada
    os.system("tc class add dev " + iface_lan +
          " parent 1:7000 classid 1:" + str(id_clase + 7002) +
          " htb rate " + str(ceil * rate_percentage / 100) +
          "kbit ceil " + str(ceil) + "kbit burst 24k quantum 1500")
    os.system("tc class add dev " + iface_lan +
          " parent 1:" + str(id_clase + 7002) + " classid 1:" +
          str(id_clase + 7003) + " htb rate " +
          str(ceil * 90 / 100) + "kbit ceil " +
          str(ceil) +
          "kbit burst 24k prio 1 quantum 1500")
    os.system("tc qdisc add dev " + iface_lan + " parent 1:" +
          str(id_clase + 7003) + " handle " + str(id_clase + 7003) +
          " sfq perturb 10")
    os.system("tc filter add dev " + iface_lan +
          " parent 1:0 protocol ip prio 200 handle " +
          str(id_clase + 7003) + " fw classid 1:" +
          str(id_clase + 7003))
    os.system("tc class add dev " + iface_lan +
          " parent 1:" + str(id_clase + 7002) + " classid 1:" +
          str(id_clase + 7004) + " htb rate " +
          str(ceil * rate_percentage / 100) + "kbit ceil " +
          str(ceil * rate_percentage / 100) +
          "kbit burst 12k prio 3 quantum 1500")
    os.system("tc qdisc add dev " + iface_lan + " parent 1:" +
          str(id_clase + 7004) + " handle " + str(id_clase + 7004) +
          " sfq perturb 10")
    os.system("tc filter add dev " + iface_lan +
          " parent 1:0 protocol ip prio 200 handle " +
          str(id_clase + 7004) + " fw classid 1:" +
          str(id_clase + 7004))
    # Reglas mangle de bajada
    os.system("iptables -t mangle -N DOWNLOAD-" + numip)
    os.system("iptables -t mangle -A DOWNLOAD -d " + numip + " -j DOWNLOAD-" +
              numip)
    os.system("iptables -t mangle -A DOWNLOAD-" + numip +
          " -m mark --mark 0 -m length --length 0:100 -j MARK --set-mark " +
          str(id_clase + 7003))
    os.system("iptables -t mangle -A DOWNLOAD-" + numip +
          " -m mark --mark 0 -p udp -j MARK --set-mark " + str(id_clase + 7003))
    os.system("iptables -t mangle -A DOWNLOAD-" + numip +
          " -m mark --mark 0 -p icmp -j MARK --set-mark " + str(id_clase + 7003))
    os.system("iptables -t mangle -A DOWNLOAD-" + numip +
          " -m mark --mark 0 -p tcp -m multiport --sports " +
          puertos + " -j MARK --set-mark " + str(id_clase + 7003))
    os.system("iptables -t mangle -A DOWNLOAD-" + numip +
          " -m mark --mark 0 -m helper --helper ftp -j MARK --set-mark " +
          str(id_clase + 7003))
    os.system("iptables -t mangle -A DOWNLOAD-" + numip +
          " -m mark --mark 0 -j MARK --set-mark " + str(id_clase + 7004))
    os.system("iptables -t mangle -A DOWNLOAD-" + numip + " -j ACCEPT")
    # Reglas de control de ancho de banda para subida
    os.system("tc class add dev " + iface_wan +
          " parent 1:7001 classid 1:" + str(id_clase + 7005) +
          " htb rate " + str(ceil * rate_percentage / 100) +
          "kbit ceil " + str(ceil) + "kbit burst 24k quantum 1500")
    os.system("tc class add dev " + iface_wan +
          " parent 1:" + str(id_clase + 7005) + " classid 1:" +
          str(id_clase + 7006) + " htb rate " +
          str(ceil * 90 / 100) + "kbit ceil " +
          str(ceil) +
          "kbit burst 24k prio 1 quantum 1500")
    os.system("tc qdisc add dev " + iface_wan + " parent 1:" +
          str(id_clase + 7006) + " handle " + str(id_clase + 7006) +
          " sfq perturb 10")
    os.system("tc filter add dev " + iface_wan +
          " parent 1:0 protocol ip prio 200 handle " +
          str(id_clase + 7006) + " fw classid 1:" +
          str(id_clase + 7006))
    os.system("tc class add dev " + iface_wan +
          " parent 1:" + str(id_clase + 7005) + " classid 1:" +
          str(id_clase + 7007) + " htb rate " +
          str(ceil * rate_percentage / 100) + "kbit ceil " +
          str(ceil * rate_percentage * 2 / 100) +
          "kbit burst 12k prio 3 quantum 1500")
    os.system("tc qdisc add dev " + iface_wan + " parent 1:" +
          str(id_clase + 7007) + " handle " + str(id_clase + 7007) +
          " sfq perturb 10")
    os.system("tc filter add dev " + iface_wan +
          " parent 1:0 protocol ip prio 200 handle " +
          str(id_clase + 7007) + " fw classid 1:" +
          str(id_clase + 7007))
    # Reglas mangle de subida
    os.system("iptables -t mangle -N UPLOAD-" + numip)
    os.system("iptables -t mangle -A UPLOAD -s " + numip +
          " -j UPLOAD-" + numip)
    os.system("iptables -t mangle -A UPLOAD-" + numip +
          " -m mark --mark 0 -m length --length 0:100 -j MARK --set-mark " +
          str(id_clase + 7006))
    os.system("iptables -t mangle -A UPLOAD-" + numip +
          " -m mark --mark 0 -p udp -j MARK --set-mark " + str(id_clase + 7006))
    os.system("iptables -t mangle -A UPLOAD-" + numip +
          " -m mark --mark 0 -p icmp -j MARK --set-mark " + str(id_clase + 7006))
    os.system("iptables -t mangle -A UPLOAD-" + numip +
          " -m mark --mark 0 -p tcp -m multiport --dports " + puertos +
          " -j MARK --set-mark " + str(id_clase + 7006))
    os.system("iptables -t mangle -A UPLOAD-" + numip +
          " -m mark --mark 0 -m helper --helper ftp -j MARK --set-mark " +
          str(id_clase + 7006))
    os.system("iptables -t mangle -A UPLOAD-" + numip +
          " -m mark --mark 0 -j MARK --set-mark " + str(id_clase + 7007))
    os.system("iptables -t mangle -A UPLOAD-" + numip + " -j ACCEPT")


def configuration_tc():
    os.system("tc qdisc del dev " + iface_lan + " root")
    os.system("tc qdisc add dev " + iface_lan + " root handle 1 htb default" +
                " 0 r2q 10")
    os.system("tc qdisc del dev " + iface_wan + " root")
    os.system("tc qdisc add dev " + iface_wan + " root handle 1 htb default" +
                " 0 r2q 10")
    os.system("tc class add dev " + iface_lan +
                " parent 1: classid 1:7000 htb rate " + str(total_download) +
                "kbit ceil " + str(total_download) + "kbit burst 12k" +
                " quantum 25907")
    os.system("tc class add dev " + iface_wan +
                " parent 1: classid 1:7000 htb rate " + str(total_download) +
                "kbit ceil " + str(total_download) + "kbit burst 12k" +
                " quantum 25907")
    id_clase = 0
    for workstation in Puesto.select():
        rule_tc(id_clase, full_ceil, workstation.ip, priorized_ports)
        id_clase += 6


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
    os.system("iptables -t mangle -N DOWNLOAD")
    os.system("iptables -t mangle -A FORWARD -o " + iface_lan +
                " -j DOWNLOAD")
    os.system("iptables -t mangle -N UPLOAD")
    os.system("iptables -t mangle -A FORWARD -o " + iface_wan +
                " -j UPLOAD")
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
configuration_tc()
