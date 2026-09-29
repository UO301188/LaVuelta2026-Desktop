# xml2kml.py
# -*- coding: utf-8 -*-
"""
Genera el archivo etapa.kml (planimetría de la etapa) a partir de etapaEsquema.xml
usando expresiones XPath.

@version 1.0
@author: Adrián Pérez Menéndez
"""

import xml.etree.ElementTree as ET


class Kml(object):
    """
    Genera archivo KML con puntos y líneas
    """
    def __init__(self):
        """
        Crea el elemento raíz y el espacio de nombres
        """
        self.raiz = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        self.doc = ET.SubElement(self.raiz, 'Document')

    def addEstilo(self, idEstilo, color):
        """
        Añade un elemento <Style> con un icono de color (formato KML: aabbggrr)
        """
        estilo = ET.SubElement(self.doc, 'Style', id=idEstilo)
        icono = ET.SubElement(estilo, 'IconStyle')
        ET.SubElement(icono, 'color').text = color
        ET.SubElement(icono, 'scale').text = '1.1'
        icon = ET.SubElement(icono, 'Icon')
        ET.SubElement(icon, 'href').text = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'

    def addPlacemark(self, nombre, descripcion, long, lat, alt, modoAltitud, estilo):
        """
        Añade un elemento <Placemark> con puntos <Point>
        """
        pm = ET.SubElement(self.doc, 'Placemark')
        ET.SubElement(pm, 'name').text = nombre
        ET.SubElement(pm, 'description').text = descripcion
        ET.SubElement(pm, 'styleUrl').text = '#' + estilo
        punto = ET.SubElement(pm, 'Point')
        ET.SubElement(punto, 'altitudeMode').text = modoAltitud
        ET.SubElement(punto, 'coordinates').text = '{},{},{}'.format(long, lat, alt)

    def addLineString(self, nombre, extrude, tesela, listaCoordenadas, modoAltitud, color, ancho):
        """
        Añade un elemento <Placemark> con líneas <LineString>
        """
        pm = ET.SubElement(self.doc, 'Placemark')
        ET.SubElement(pm, 'name').text = nombre

        estilo = ET.SubElement(pm, 'Style')
        linea = ET.SubElement(estilo, 'LineStyle')
        ET.SubElement(linea, 'color').text = color
        ET.SubElement(linea, 'width').text = ancho

        ls = ET.SubElement(pm, 'LineString')
        ET.SubElement(ls, 'extrude').text = extrude
        ET.SubElement(ls, 'tessellate').text = tesela
        ET.SubElement(ls, 'altitudeMode').text = modoAltitud
        ET.SubElement(ls, 'coordinates').text = listaCoordenadas

    def escribir(self, nombreArchivoKML):
        """
        Escribe el archivo KML con declaración y codificación
        """
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(nombreArchivoKML, encoding='utf-8', xml_declaration=True)

    def ver(self):
        """
        Muestra el archivo KML. Se utiliza para depurar
        """
        print("\nElemento raiz = ", self.raiz.tag)

        if self.raiz.text != None:
            print("Contenido = ", self.raiz.text.strip('\n'))
        else:
            print("Contenido = ", self.raiz.text)

        print("Atributos = ", self.raiz.attrib)

        for hijo in self.raiz.findall('.//*'):
            print("\nElemento = ", hijo.tag)
            if hijo.text != None:
                print("Contenido = ", hijo.text.strip('\n'))
            else:
                print("Contenido = ", hijo.text)
            print("Atributos = ", hijo.attrib)


class Xml2Kml(object):
    """
    Lee etapaEsquema.xml, extrae los datos con expresiones XPath
    y genera el archivo etapa.kml mediante la clase Kml
    """
    NS = {'u': 'http://www.uniovi.es'}

    def __init__(self, archivoXML, archivoKML):
        self.archivoXML = archivoXML
        self.archivoKML = archivoKML
        self.raiz = None
        self.kml = Kml()

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

    def extraerCoordenadas(self, nodo):
        """
        Devuelve (longitud, latitud, altitud) de un nodo que contiene <coordenadas>
        """
        lon = nodo.find('u:coordenadas/u:longitudGeo', self.NS).text.strip()
        lat = nodo.find('u:coordenadas/u:latitudGeo', self.NS).text.strip()
        alt = nodo.find('u:coordenadas/u:altitud', self.NS).text.strip()
        return lon, lat, alt

    def extraerDistancia(self, nodo):
        """
        Devuelve la distancia desde la salida (float) de un nodo
        """
        return float(nodo.find('u:distanciaSalida', self.NS).text.strip())

    def crearEstilos(self):
        """
        Rojo: salida y meta. Verde: puertos. Azul: sprints. Amarillo: puntos anónimos
        Colores en formato KML aabbggrr
        """
        self.kml.addEstilo('estiloRojo', 'ff0000ff')
        self.kml.addEstilo('estiloVerde', 'ff00ff00')
        self.kml.addEstilo('estiloAzul', 'ffff0000')
        self.kml.addEstilo('estiloAmarillo', 'ff00ffff')

    def addSalidaMeta(self):
        """
        Añade los placemarks rojos de salida y meta
        """
        salida = self.raiz.find('u:ubicaciones/u:salida', self.NS)
        origen = self.raiz.find('u:origen', self.NS).text.strip()
        lon, lat, alt = self.extraerCoordenadas(salida)
        self.kml.addPlacemark('Salida: ' + origen, 'Punto de salida de la etapa',
                              lon, lat, alt, 'clampToGround', 'estiloRojo')

        meta = self.raiz.find('u:ubicaciones/u:meta', self.NS)
        destino = self.raiz.find('u:destino', self.NS).text.strip()
        lon, lat, alt = self.extraerCoordenadas(meta)
        self.kml.addPlacemark('Meta: ' + destino, 'Punto de meta de la etapa',
                              lon, lat, alt, 'clampToGround', 'estiloRojo')

    def addHitos(self):
        """
        Añade los puertos (verde) y los sprints (azul)
        """
        for puerto in self.raiz.findall('u:hitos/u:puerto', self.NS):
            nombre = puerto.find('u:nombre', self.NS).text.strip()
            lon, lat, alt = self.extraerCoordenadas(puerto)
            descripcion = 'Puerto de categoría {} - km {}'.format(
                puerto.get('categoria'), self.extraerDistancia(puerto))
            self.kml.addPlacemark(nombre, descripcion, lon, lat, alt,
                                  'clampToGround', 'estiloVerde')

        for sprint in self.raiz.findall('u:hitos/u:sprint', self.NS):
            nombre = sprint.find('u:nombre', self.NS).text.strip()
            lon, lat, alt = self.extraerCoordenadas(sprint)
            descripcion = 'Sprint {} - km {}'.format(
                sprint.get('tipo'), self.extraerDistancia(sprint))
            self.kml.addPlacemark(nombre, descripcion, lon, lat, alt,
                                  'clampToGround', 'estiloAzul')

    def addPuntosAnonimos(self):
        """
        Añade los puntos anónimos (amarillo)
        """
        for punto in self.raiz.findall('u:puntosAnonimos/u:punto', self.NS):
            distancia = self.extraerDistancia(punto)
            nombre = punto.get('nombre')
            if nombre is None:
                nombre = 'Punto km {}'.format(distancia)
            lon, lat, alt = self.extraerCoordenadas(punto)
            self.kml.addPlacemark(nombre, 'Punto anónimo - km {}'.format(distancia),
                                  lon, lat, alt, 'clampToGround', 'estiloAmarillo')

    def obtenerCoordenadasRuta(self):
        """
        Construye la cadena de coordenadas de la línea: salida, hitos y puntos
        anónimos ordenados por distancia, y meta al final
        """
        lista = []
        for nodo in self.raiz.findall('u:hitos/*', self.NS):
            lon, lat, alt = self.extraerCoordenadas(nodo)
            lista.append((self.extraerDistancia(nodo), '{},{},{}'.format(lon, lat, alt)))
        for nodo in self.raiz.findall('u:puntosAnonimos/u:punto', self.NS):
            lon, lat, alt = self.extraerCoordenadas(nodo)
            lista.append((self.extraerDistancia(nodo), '{},{},{}'.format(lon, lat, alt)))
        lista.sort(key=lambda elemento: elemento[0])

        salida = self.raiz.find('u:ubicaciones/u:salida', self.NS)
        lon, lat, alt = self.extraerCoordenadas(salida)
        coordenadas = ['{},{},{}'.format(lon, lat, alt)]
        coordenadas += [c for (d, c) in lista]

        meta = self.raiz.find('u:ubicaciones/u:meta', self.NS)
        lon, lat, alt = self.extraerCoordenadas(meta)
        coordenadas.append('{},{},{}'.format(lon, lat, alt))

        return "\n".join(coordenadas)

    def addRuta(self):
        """
        Añade la línea con el recorrido de la etapa
        """
        nombre = self.raiz.find('u:nombre', self.NS).text.strip()
        self.kml.addLineString('Ruta ' + nombre, '0', '1',
                               self.obtenerCoordenadasRuta(),
                               'clampToGround', 'ff0000ff', '4')

    def ejecutar(self):
        """Genera el archivo etapa.kml"""
        print(Xml2Kml.__doc__)

        nombreXML = input('Introduzca el archivo XML [etapaEsquema.xml] = ')
        if nombreXML.strip() != '':
            self.archivoXML = nombreXML.strip()

        self.leerXML()
        self.crearEstilos()
        self.addRuta()
        self.addHitos()
        self.addPuntosAnonimos()
        self.addSalidaMeta()

        self.kml.ver()
        self.kml.escribir(self.archivoKML)
        print("Creado el archivo: ", self.archivoKML)


if __name__ == "__main__":
    Xml2Kml("etapaEsquema.xml", "etapa.kml").ejecutar()