class Ciudad {

    constructor(nombre, pais, gentilicio) {
        this.nombre = nombre;
        this.pais = pais;
        this.gentilicio = gentilicio;
        this.poblacion = 0;
        this.longitud = 0;
        this.latitud = 0;
        this.altitud = 0;
    }

    rellenarAtributos() {
        this.poblacion = 3218;
        this.longitud = -0.0344063;
        this.latitud = 40.1730083;
        this.altitud = 185;
    }

    getCiudad() {
        return this.nombre;
    }

    getPais() {
        return this.pais;
    }

    getInformacionSecundaria() {
        const habitantes = this.poblacion.toLocaleString("es-ES", { useGrouping: "always" });
        return "<ul>" +
                   "<li>Gentilicio: " + this.gentilicio + "</li>" +
                   "<li>Población: " + habitantes + " habitantes</li>" +
               "</ul>";
    }

    escribeCoordenadas() {
        const parrafo = document.createElement("p");
        parrafo.textContent = "Coordenadas del punto central: longitud " + this.longitud +
                              ", latitud " + this.latitud +
                              ", altitud " + this.altitud + " m.";
        const primeraSeccion = document.querySelector("main section");
        primeraSeccion.appendChild(parrafo);
    }
}

const ciudad = new Ciudad("Vall d'Alba", "España", "albense");
ciudad.rellenarAtributos();

const seccion = document.createElement("section");

const encabezado = document.createElement("h3");
encabezado.textContent = ciudad.getCiudad() + " (" + ciudad.getPais() + ")";
seccion.appendChild(encabezado);

seccion.insertAdjacentHTML("beforeend", ciudad.getInformacionSecundaria());

document.querySelector("main h2").insertAdjacentElement("afterend", seccion);

ciudad.escribeCoordenadas();