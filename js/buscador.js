class Buscador {

    constructor() {
        this.lupa = document.querySelector("search label img");
        this.campo = document.querySelector("search input");

        this.lupa.addEventListener("click", this.buscar.bind(this));
        this.campo.addEventListener("keypress", this.teclaPulsada.bind(this));
    }

    teclaPulsada(evento) {
        if (evento.key === "Enter") {
            this.buscar();
        }
    }

    buscar() {
        this.limpiar_busqueda();

        const resultados = [];
        const texto = this.campo.value.trim();

        if (texto !== "") {
            const escapado = texto.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
            const regexp = new RegExp(escapado, "gi");

            const recorrido = document.createTreeWalker(document.querySelector("body"), NodeFilter.SHOW_TEXT);
            let nodo = recorrido.nextNode();

            while (nodo) {
                regexp.lastIndex = 0;
                if (regexp.test(nodo.textContent)) {
                    resultados.push(nodo);
                }
                nodo = recorrido.nextNode();
            }

            resultados.forEach(nodoTexto => {
                const contenido = nodoTexto.textContent;
                const fragmento = document.createDocumentFragment();
                let ultimo = 0;

                for (const coincidencia of contenido.matchAll(regexp)) {
                    fragmento.append(contenido.slice(ultimo, coincidencia.index));

                    const marca = document.createElement("mark");
                    marca.textContent = coincidencia[0];
                    fragmento.append(marca);

                    ultimo = coincidencia.index + coincidencia[0].length;
                }
                fragmento.append(contenido.slice(ultimo));

                nodoTexto.replaceWith(fragmento);
            });
        }
    }

    limpiar_busqueda() {
        document.querySelectorAll("mark").forEach(marca => {
            marca.replaceWith(document.createTextNode(marca.textContent));
        });
        document.body.normalize();
    }
}

const buscador = new Buscador();