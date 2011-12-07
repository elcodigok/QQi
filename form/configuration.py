from snack import *
import gettext
import os
import ConfigParser
import logging


class Configuracion():

    def __init__(self, pantalla, archivo, filelog):
        if not archivo:
            #self.archivo = "parametros.conf"
            self.archivo = "qqi.cnf"
        else:
            self.archivo = archivo
        if not pantalla:
            pantalla = snack.SnackScreen()
        else:
            self.pantalla = pantalla
        self.logger = logging.getLogger(filelog)

    def modificar(self):
        config = ConfigParser.RawConfigParser()
        config.read(self.archivo)
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
        (boton, valores) = EntryWindow(self.pantalla,
                    gettext.gettext("Configuration"),
                    gettext.gettext("Input here the basic parameter" +
                                    " for the system"),
                    [(gettext.gettext('Internal network:'), internal_network),
                    (gettext.gettext('External network:'), external_network),
                    (gettext.gettext('Internal IP:'), internal_ip),
                    (gettext.gettext('External IP:'), external_ip),
                    (gettext.gettext('Internal interface:'), iface_lan),
                    (gettext.gettext('External interface:'), iface_wan),
                    (gettext.gettext('Administrative IP:'), admin_ip),
                    (gettext.gettext('Upload bandwidht:'), total_upload),
                    (gettext.gettext('Download bandwidht:'), total_download),
                    (gettext.gettext('Ceil for low class:'), low_ceil),
                    (gettext.gettext('Ceil for medium class:'), medium_ceil),
                    (gettext.gettext('Ceil for high class:'), high_ceil),
                    (gettext.gettext('Ceil for full class:'), full_ceil),
                    (gettext.gettext('Rate pecent guaranty:'), rate_percentage),
                    (gettext.gettext('Priorized ports:'), priorized_ports)])
        config = ConfigParser.RawConfigParser()
        config.add_section('Lan')
        config.set('Lan', 'internal_network', valores[0])
        config.set('Lan', 'external_network', valores[1])
        config.set('Lan', 'internal_ip', valores[2])
        config.set('Lan', 'external_ip', valores[3])
        config.set('Lan', 'iface_lan', valores[4])
        config.set('Lan', 'iface_wan', valores[5])
        config.set('Lan', 'admin_ip', valores[6])
        config.add_section('Bandwidht')
        config.set('Bandwidht', 'total_upload', valores[7])
        config.set('Bandwidht', 'total_download', valores[8])
        config.set('Bandwidht', 'low_ceil', valores[9])
        config.set('Bandwidht', 'medium_ceil', valores[10])
        config.set('Bandwidht', 'high_ceil', valores[11])
        config.set('Bandwidht', 'full_ceil', valores[12])
        config.set('Bandwidht', 'rate_percentage', valores[13])
        config.set('Bandwidht', 'priorized_ports', valores[14])
        if boton == 'ok':
            self.logger.info(gettext.gettext('Save the new configuration'))
            configfile = open(self.archivo, 'wb')
            config.write(configfile)

    def crear(self):
        """ Funcion para creacion de Configuracion de parametros """
        (boton, valores) = snack.EntryWindow(self.pantalla,
                        gettext.gettext("Configuration"),
                        gettext.gettext("Input here the basic parameter for" +
                                        " the system"),
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
        config.set('Lan', 'internal_network', valores[0])
        config.set('Lan', 'external_network', valores[1])
        config.set('Lan', 'internal_ip', valores[2])
        config.set('Lan', 'external_ip', valores[3])
        config.set('Lan', 'iface_lan', valores[4])
        config.set('Lan', 'iface_wan', valores[5])
        config.set('Lan', 'admin_ip', valores[6])
        config.add_section('Bandwidht')
        config.set('Bandwidht', 'total_upload', valores[7])
        config.set('Bandwidht', 'total_download', valores[8])
        config.set('Bandwidht', 'low_ceil', valores[9])
        config.set('Bandwidht', 'medium_ceil', valores[10])
        config.set('Bandwidht', 'high_ceil', valores[11])
        config.set('Bandwidht', 'full_ceil', valores[12])
        config.set('Bandwidht', 'rate_percentage', valores[13])
        config.set('Bandwidht', 'priorized_ports', valores[14])
        if boton == 'ok':
            self.logger.info(gettext.gettext('Create the new configuration'))
            configfile = open(self.archivo, 'wb')
            config.write(configfile)

    def configurar(self):
        """ Creacion o modificacion de archivo de Configuracion """
        if os.path.exists(self.archivo):
            self.modificar()
        else:
            self.crear()
