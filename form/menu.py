from snack import *
import gettext
#import os


class Menu:

    def __init__(self, texto, ancho=60, altomenu=25, opciones=None, titulo='',
                                scroll=0, screen=None, posicion=0):
        self.texto = texto
        self.titulo = titulo
        self.screen = screen
        self.altomenu = altomenu
        self.scroll = scroll
        if (self.titulo == ""):
            self.titulo = gettext.gettext("No title")
        self.items = []
        for item in opciones:
            self.items.append(item)
        if (len(self.items) > self.altomenu):
            self.scroll = 1

    def showMenu(self):
        (self.button, rta) = ListboxChoiceWindow(self.screen,
                                                self.titulo,
                                                self.texto,
                                                self.items,
                                                width=65,
                                                height=17,
                                                help=None)
        if (self.button == 'cancel'):
            self.screen.finish()
            rta = None
        return rta
