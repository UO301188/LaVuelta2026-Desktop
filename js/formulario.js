class Formulario {

    constructor() {
        this.puntuacion = 0;
        this.dureza = "";
        this.descripcion = "";
        this.usuario = "";
        this.parrafoResultado = null;

        const boton = document.querySelector('form button[type="submit"]');
        boton.addEventListener("click", this.analizar.bind(this));
    }

    analizar(event) {
        event.preventDefault();

        const form = event.target.closest("form");
        this.puntuacion = 0;

        const numeroEtapa = form.querySelector('input[name="numero-etapa"]').value;
        if (Number(numeroEtapa) === 7) {
            this.puntuacion++;
        }

        const fecha = form.querySelector('input[name="fecha-etapa"]').value;
        if (fecha === "2026-08-28") {
            this.puntuacion++;
        }

        const salida = form.querySelector('select[name="salida"]').value;
        if (salida === "vall-d-alba") {
            this.puntuacion++;
        }

        const llegada = form.querySelector('select[name="llegada"]').value;
        if (llegada === "aramon-valdelinares") {
            this.puntuacion++;
        }

        const tipo = form.querySelector('input[name="tipo-etapa"]:checked');
        if (tipo !== null && tipo.value === "montana") {
            this.puntuacion++;
        }

        const hitos = Array.from(form.querySelectorAll('input[name="hitos"]:checked'))
            .map(hito => hito.value)
            .sort();
        if (hitos.length === 2 && hitos[0] === "bonificado" && hitos[1] === "puerto") {
            this.puntuacion++;
        }

        const longitud = form.querySelector('input[name="longitud"]').value;
        if (parseFloat(longitud) === 149.8) {
            this.puntuacion++;
        }

        const desnivel = form.querySelector('input[name="desnivel"]').value;
        if (Number(desnivel) === 3685) {
            this.puntuacion++;
        }

        this.dureza = form.querySelector('input[name="dureza"]').value;
        this.descripcion = form.querySelector('textarea[name="descripcion"]').value;
        this.usuario = form.querySelector('input[name="usuario"]').value.trim();

        this.calificar(form);
    }

    calificar(form) {
        if (this.parrafoResultado !== null) {
            this.parrafoResultado.remove();
        }

        const nombre = this.usuario === "" ? "Participante" : this.usuario;

        this.parrafoResultado = document.createElement("p");
        this.parrafoResultado.setAttribute("role", "status");
        this.parrafoResultado.textContent = nombre + " has obtenido " + this.puntuacion +
            " puntos, la dureza que has asignado a la etapa es " + this.dureza +
            " y tu descripción " + this.descripcion + ".";

        form.insertAdjacentElement("afterend", this.parrafoResultado);
    }
}

const formulario = new Formulario();