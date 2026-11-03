class Equipo {

    constructor(nombre, codigoUCI, pais) {
        this.nombre = nombre;
        this.codigoUCI = codigoUCI;
        this.pais = pais;
        this.director = "";
        this.categoria = "";
        this.paginaWeb = "";
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