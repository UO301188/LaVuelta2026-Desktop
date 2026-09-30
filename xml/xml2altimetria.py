# xml2altimetria.py
# -*- coding: utf-8 -*-
"""
Genera el archivo altimetria.svg (perfil altimétrico de la etapa) a partir de
etapaEsquema.xml usando expresiones XPath.

@version 1.1
@author: Adrián Pérez Menéndez (UO301188)
"""

import math
import os
import xml.etree.ElementTree as ET


class Svg(object):
    """
    Genera archivos SVG con rectángulos, círculos, líneas, polilíneas y texto
    """
    def __init__(self, ancho, alto):
        """
        Crea el elemento raíz, el espacio de nombres y la versión
        """
        self.raiz = ET.Element('svg',
                               xmlns="http://www.w3.org/2000/svg",
                               version="1.1",
                               width=str(ancho),
                               height=str(alto),
                               viewBox="0 0 {} {}".format(ancho, alto))

    def addRect(self, x, y, width, height, fill, strokeWidth, stroke):
        """
        Añade un elemento rect
        """
        ET.SubElement(self.raiz, 'rect', {'x': x, 'y': y,
                                          'width': width, 'height': height,
                                          'fill': fill,
                                          'stroke-width': strokeWidth,
                                          'stroke': stroke})

    def addCircle(self, cx, cy, r, fill):
        """
        Añade un elemento circle
        """
        ET.SubElement(self.raiz, 'circle', cx=cx, cy=cy, r=r, fill=fill)

    def addLine(self, x1, y1, x2, y2, stroke, strokeWidth):
        """
        Añade un elemento line
        """
        ET.SubElement(self.raiz, 'line', {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                                          'stroke': stroke,
                                          'stroke-width': strokeWidth})

    def addPolyline(self, points, stroke, strokeWidth, fill):
        """
        Añade un elemento polyline
        """
        ET.SubElement(self.raiz, 'polyline', {'points': points,
                                              'stroke': stroke,
                                              'stroke-width': strokeWidth,
                                              'fill': fill})

    def addText(self, texto, x, y, fontFamily, fontSize, style, transform=None):
        """
        Añade un elemento texto (con rotación opcional)
        """
        atributos = {'x': x, 'y': y,
                     'font-family': fontFamily,
                     'font-size': fontSize,
                     'style': style}
        if transform is not None:
            atributos['transform'] = transform
        ET.SubElement(self.raiz, 'text', atributos).text = texto

    def escribir(self, nombreArchivoSVG):
        """
        Escribe el archivo SVG con declaración y codificación
        """
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(nombreArchivoSVG, encoding='utf-8', xml_declaration=True)

    def ver(self):
        """
        Muestra el archivo SVG. Se utiliza para depurar
        """
        print("\nElemento raiz = ", self.raiz.tag)

        if self.raiz.text != None:
            print("Contenido = ", self.raiz.text.strip('\n'))
        else:
            print("Contenido = ", self.raiz.text)

        print("Atributos = ", self.raiz.attrib)

        # Recorrido de los elementos del árbol
        for hijo in self.raiz.findall('.//'):  # Expresión XPath
            print("\nElemento = ", hijo.tag)
            if hijo.text != None:
                print("Contenido = ", hijo.text.strip('\n'))
            else:
                print("Contenido = ", hijo.text)
            print("Atributos = ", hijo.attrib)


class Xml2Altimetria(object):
    """
    Lee etapaEsquema.xml, extrae distancias y altitudes con expresiones XPath
    y genera el perfil altimétrico altimetria.svg mediante la clase Svg
    """
    # Los elementos de etapaEsquema.xml llevan el prefijo del espacio de nombres
    # con el formato {http://www.uniovi.es}elemento
    NS = '{http://www.uniovi.es}'

    ANCHO = 1200
    ALTO = 700
    MARGEN_IZQ = 80
    MARGEN_DER = 40
    MARGEN_SUP = 340
    MARGEN_INF = 80
    SEPARACION_MINIMA = 2.5   # km mínimos entre etiquetas
    PASO_ALTITUD = 200        # metros entre líneas horizontales

    COLORES = {'salida': 'red', 'meta': 'red', 'puerto': 'green',
               'sprint': 'blue', 'anonimo': 'gold'}

    def __init__(self, archivoXML, archivoSVG):
        self.carpeta = os.path.dirname(os.path.abspath(__file__))
        self.archivoXML = archivoXML
        self.archivoSVG = archivoSVG
        self.raiz = None
        self.puntos = []
        self.svg = Svg(self.ANCHO, self.ALTO)

    def leerXML(self):
        """
        Lee el archivo XML y genera en memoria el árbol DOM
        """
        try:
            arbol = ET.parse(self.archivoXML)
        except IOError:
            print('No se encuentra el archivo ', self.archivoXML)
            exit()
        except ET.ParseError:
            print("Error procesando en el archivo XML = ", self.archivoXML)
            exit()

        self.raiz = arbol.getroot()

    def ruta(self, *nombres):
        """
        Construye una expresión XPath con el prefijo {http://www.uniovi.es}
        en cada nombre de elemento (el comodín * no lleva prefijo)
        Ejemplo: ruta('hitos', 'puerto') -> {http://www.uniovi.es}hitos/{http://www.uniovi.es}puerto
        """
        return '/'.join(n if n == '*' else self.NS + n for n in nombres)

    def buscarNodos(self, nodo, *nombres):
        """
        Devuelve la lista de nodos que cumplen la expresión XPath (findall)
        """
        return nodo.findall(self.ruta(*nombres))

    def buscarNodo(self, nodo, *nombres):
        """
        Devuelve el primer nodo que cumple la expresión XPath (findall)
        """
        return nodo.findall(self.ruta(*nombres))[0]

    def buscarTexto(self, nodo, *nombres):
        """
        Devuelve el contenido del primer nodo que cumple la expresión XPath
        """
        return self.buscarNodo(nodo, *nombres).text.strip()

    def crearPunto(self, nombre, distancia, altitud, tipo):
        """
        Crea un diccionario con los datos de un punto del perfil
        """
        return {'nombre': nombre, 'dist': distancia, 'alt': altitud,
                'tipo': tipo, 'etiqueta': False}

    def leerNodo(self, nodo, tipo):
        """
        Extrae con XPath nombre, distancia y altitud de un puerto, sprint o punto
        """
        if tipo == 'anonimo':
            nombre = nodo.get('nombre')
        else:
            nombre = self.buscarTexto(nodo, 'nombre')
        distancia = float(self.buscarTexto(nodo, 'distanciaSalida'))
        altitud = float(self.buscarTexto(nodo, 'coordenadas', 'altitud'))
        return self.crearPunto(nombre, distancia, altitud, tipo)

    def extraerDatos(self):
        """
        Extrae del árbol DOM, mediante expresiones XPath, los datos de la etapa
        """
        self.nombreEtapa = self.buscarTexto(self.raiz, 'nombre')
        self.desnivel = self.buscarTexto(self.raiz, 'desnivel')
        self.longitud = float(self.buscarTexto(self.raiz, 'longitud'))
        origen = self.buscarTexto(self.raiz, 'origen')
        destino = self.buscarTexto(self.raiz, 'destino')

        altSalida = float(self.buscarTexto(self.raiz, 'ubicaciones', 'salida', 'coordenadas', 'altitud'))
        altMeta = float(self.buscarTexto(self.raiz, 'ubicaciones', 'meta', 'coordenadas', 'altitud'))

        self.puntos.append(self.crearPunto(origen, 0.0, altSalida, 'salida'))
        self.puntos.append(self.crearPunto(destino, self.longitud, altMeta, 'meta'))

        for puerto in self.buscarNodos(self.raiz, 'hitos', 'puerto'):
            self.puntos.append(self.leerNodo(puerto, 'puerto'))
        for sprint in self.buscarNodos(self.raiz, 'hitos', 'sprint'):
            self.puntos.append(self.leerNodo(sprint, 'sprint'))
        for punto in self.buscarNodos(self.raiz, 'puntosAnonimos', 'punto'):
            self.puntos.append(self.leerNodo(punto, 'anonimo'))

        self.puntos.sort(key=lambda p: p['dist'])

    def marcarEtiquetas(self):
        """
        Decide qué puntos llevan etiqueta (por prioridad y sin solaparse)
        """
        prioridad = ['puerto', 'sprint', 'salida', 'meta', 'anonimo']
        etiquetados = []
        for tipo in prioridad:
            for p in self.puntos:
                if p['tipo'] != tipo or p['nombre'] is None:
                    continue
                if all(abs(p['dist'] - e['dist']) >= self.SEPARACION_MINIMA for e in etiquetados):
                    p['etiqueta'] = True
                    etiquetados.append(p)

    def calcularEscalas(self):
        """
        Calcula las escalas horizontal (km) y vertical (m)
        """
        self.distMax = max(p['dist'] for p in self.puntos)
        altMaxima = max(p['alt'] for p in self.puntos)
        self.altMax = math.ceil(altMaxima / self.PASO_ALTITUD) * self.PASO_ALTITUD
        self.anchoGrafico = self.ANCHO - self.MARGEN_IZQ - self.MARGEN_DER
        self.altoGrafico = self.ALTO - self.MARGEN_SUP - self.MARGEN_INF
        self.base = self.ALTO - self.MARGEN_INF

    def coordX(self, distancia):
        return self.MARGEN_IZQ + distancia / self.distMax * self.anchoGrafico

    def coordY(self, altitud):
        return self.base - altitud / self.altMax * self.altoGrafico

    def cadena(self, valor):
        return '{:.1f}'.format(valor)

    def dibujarFondoYEscalas(self):
        """
        Dibuja el fondo, el título, las líneas horizontales (m) y la escala de km
        """
        self.svg.addRect('0', '0', str(self.ANCHO), str(self.ALTO), 'white', '0', 'white')
        self.svg.addText(self.nombreEtapa, '80', '25', 'Verdana', '18',
                         'font-weight:bold; fill:black')
        self.svg.addText('Altitud (m)', '25', self.cadena(self.base - 10), 'Verdana', '12',
                         'fill:#555', 'rotate(-90 25 {})'.format(self.cadena(self.base - 10)))

        for alt in range(0, int(self.altMax) + 1, self.PASO_ALTITUD):
            y = self.cadena(self.coordY(alt))
            self.svg.addLine(str(self.MARGEN_IZQ), y,
                             str(self.ANCHO - self.MARGEN_DER), y, 'lightgray', '1')
            self.svg.addText(str(alt), str(self.MARGEN_IZQ - 8), self.cadena(self.coordY(alt) + 4),
                             'Verdana', '11', 'text-anchor:end; fill:#555')

        for km in range(0, int(self.distMax) + 1, 20):
            x = self.cadena(self.coordX(km))
            self.svg.addLine(x, str(self.base), x, str(self.base + 6), 'black', '1')
            self.svg.addText(str(km), x, str(self.base + 22), 'Verdana', '11',
                             'text-anchor:middle; fill:#333')
        self.svg.addText('km', str(self.ANCHO - self.MARGEN_DER + 5), str(self.base + 22),
                         'Verdana', '11', 'fill:#333')

    def dibujarPerfil(self):
        """
        Dibuja la polilínea rellena con el perfil de la etapa (cerrada por el suelo)
        """
        vertices = ['{},{}'.format(self.cadena(self.coordX(0)), self.cadena(self.base))]
        for p in self.puntos:
            vertices.append('{},{}'.format(self.cadena(self.coordX(p['dist'])),
                                           self.cadena(self.coordY(p['alt']))))
        vertices.append('{},{}'.format(self.cadena(self.coordX(self.distMax)), self.cadena(self.base)))
        self.svg.addPolyline(' '.join(vertices), '#7a1a10', '1.5', '#e8412c')

    def dibujarHitos(self):
        """
        Dibuja líneas verticales, marcadores y textos verticales de los puntos etiquetados
        """
        for p in self.puntos:
            if not p['etiqueta']:
                continue
            x = self.coordX(p['dist'])
            y = self.coordY(p['alt'])
            self.svg.addLine(self.cadena(x), str(self.MARGEN_SUP - 10),
                             self.cadena(x), self.cadena(y), 'gray', '1')
            self.svg.addCircle(self.cadena(x), self.cadena(y), '4', self.COLORES[p['tipo']])

            texto = '{} / {} m'.format(p['nombre'], int(p['alt']))
            xt = self.cadena(x + 4)
            yt = str(self.MARGEN_SUP - 15)
            self.svg.addText(texto, xt, yt, 'Verdana', '11', 'fill:black',
                             'rotate(-90 {} {})'.format(xt, yt))

    def dibujarPie(self):
        """
        Dibuja el texto con el desnivel positivo
        """
        self.svg.addText('Desnivel positivo: {} m'.format(self.desnivel),
                         str(self.ANCHO // 2), str(self.ALTO - 15), 'Verdana', '14',
                         'font-weight:bold; text-anchor:middle; fill:black')

    def ejecutar(self):
        """Genera el archivo altimetria.svg"""
        print(Xml2Altimetria.__doc__)

        nombreXML = input('Introduzca el archivo XML [etapaEsquema.xml] = ')
        if nombreXML.strip() != '':
            self.archivoXML = nombreXML.strip()
        self.archivoXML = os.path.join(self.carpeta, self.archivoXML)
        self.archivoSVG = os.path.join(self.carpeta, self.archivoSVG)

        self.leerXML()
        self.extraerDatos()
        self.marcarEtiquetas()
        self.calcularEscalas()
        self.dibujarFondoYEscalas()
        self.dibujarPerfil()
        self.dibujarHitos()
        self.dibujarPie()

        self.svg.ver()
        self.svg.escribir(self.archivoSVG)
        print("Creado el archivo: ", self.archivoSVG)


if __name__ == "__main__":
    Xml2Altimetria("etapaEsquema.xml", "altimetria.svg").ejecutar()