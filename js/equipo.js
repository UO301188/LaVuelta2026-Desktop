const RUTA_JSON = "js/recursos/lavuelta.json";

class Ciclista {

    constructor(dorsal, nombre, apellidos, fechaNacimiento, nacionalidad, codigoNacionalidad) {
        this.dorsal = dorsal;
        this.nombre = nombre;
        this.apellidos = apellidos;
        this.fechaNacimiento = fechaNacimiento;
        this.nacionalidad = nacionalidad;
        this.codigoNacionalidad = codigoNacionalidad;
    }

    getNombreCompleto() {
        return this.nombre + " – " + this.apellidos;
    }

    getDorsal() {
        return this.dorsal;
    }

    getInformacionAdicional() {
        return this.fechaNacimiento + ", " + this.nacionalidad;
    }
}

class Equipo {

    constructor(nombre, codigoUCI, pais) {
        this.nombre = nombre;
        this.codigoUCI = codigoUCI;
        this.pais = pais;
        this.director = "";
        this.categoria = "";
        this.paginaWeb = "";
        this.alineacion = [];
    }

    rellenarAtributos() {
        this.director = "Kurt Van de Wouwer";
        this.categoria = "UCI WorldTeam";
        this.paginaWeb = "https://www.lavuelta.es/es/equipo/LOI/lotto-intermarche";
    }

    datosBasicos() {
        return this.nombre + " (" + this.codigoUCI + ")";
    }

    getPais() {
        return this.pais;
    }

    getInformacionSecundaria() {
        return "<ul>" +
                   "<li>Director: " + this.director + "</li>" +
                   "<li>Categoría: " + this.categoria + "</li>" +
               "</ul>";
    }

    getPaginaWeb() {
        const enlace = document.createElement("a");
        enlace.setAttribute("href", this.paginaWeb);
        enlace.setAttribute("title", "Ficha del equipo " + this.nombre + " en lavuelta.es");
        enlace.textContent = "Ficha oficial de " + this.nombre;

        const parrafo = document.createElement("p");
        parrafo.appendChild(enlace);

        const primeraSeccion = document.querySelector("main section");
        primeraSeccion.appendChild(parrafo);
    }

    async leerEquipo() {
        const respuesta = await fetch(RUTA_JSON);
        if (!respuesta.ok) {
            console.error("No se pudo leer " + RUTA_JSON + " (" + respuesta.status + ")");
            return;
        }
        const datos = await respuesta.json();
        const lista = Array.isArray(datos) ? datos : datos.equipos;

        const miEquipo = lista.find(equipo => equipo.codigo_uci === this.codigoUCI);
        if (miEquipo === undefined) {
            console.error("No se encontró el equipo " + this.codigoUCI + " en el JSON");
            return;
        }
        this.alinearCiclistas(miEquipo);
    }

    alinearCiclistas(datosEquipo) {
        datosEquipo.corredores.forEach(corredor => {
            const ciclista = new Ciclista(
                corredor.dorsal,
                corredor.nombre,
                corredor.apellidos,
                corredor.fecha_nacimiento,
                corredor.nacionalidad,
                corredor.nacionalidad_codigo
            );
            this.alineacion.push(ciclista);
        });
    }

    mostrarAlineacion() {
        const seccion = document.querySelector("main > section:last-of-type");

        const ordenados = this.alineacion.slice().sort((a, b) => a.getDorsal() - b.getDorsal());

        ordenados.forEach(ciclista => {
            const tarjeta = document.createElement("article");

            const nombre = document.createElement("h4");
            nombre.textContent = ciclista.getNombreCompleto();
            tarjeta.appendChild(nombre);

            const icono = document.createElement("img");
            icono.setAttribute("src", "multimedia/ciclista-generico.png");
            icono.setAttribute("width", "128");
            icono.setAttribute("height", "128");
            icono.setAttribute("alt", "Icono genérico de un ciclista");
            tarjeta.appendChild(icono);

            const dorsal = document.createElement("p");
            dorsal.textContent = "Dorsal: " + ciclista.getDorsal();
            tarjeta.appendChild(dorsal);

            const informacion = document.createElement("p");
            informacion.textContent = ciclista.getInformacionAdicional();
            tarjeta.appendChild(informacion);

            seccion.appendChild(tarjeta);
        });
    }
}

const equipo = new Equipo("Lotto-Intermarché", "LOI", "Bélgica");
equipo.rellenarAtributos();

const seccion = document.createElement("section");

const encabezado = document.createElement("h3");
encabezado.textContent = equipo.datosBasicos() + " - " + equipo.getPais();
seccion.appendChild(encabezado);

seccion.insertAdjacentHTML("beforeend", equipo.getInformacionSecundaria());

document.querySelector("main h2").insertAdjacentElement("afterend", seccion);

equipo.getPaginaWeb();
equipo.leerEquipo().then(() => equipo.mostrarAlineacion());