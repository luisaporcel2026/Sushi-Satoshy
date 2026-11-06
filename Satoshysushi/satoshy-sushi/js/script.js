// ===== Busca de pratos no cardápio =====
// Filtra somente os pratos que já estão listados na página do cardápio.
const formularioPratos = document.querySelector("#formularioPratos");
const campoBusca = document.querySelector("#buscaPrato");
const mensagemBusca = document.querySelector("#mensagemBusca");
const botaoListarTodos = document.querySelector("#listarTodos");

// Remove acentos e deixa em minúsculas: "Salmão" == "salmao".
function normalizar(texto) {
    return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function filtrarCardapio(busca = "") {
    const termo = normalizar(busca.trim());
    const categorias = document.querySelectorAll(".categoria-cardapio");
    let encontrados = 0;

    categorias.forEach(function(categoria) {
        const nomeCategoria = normalizar(categoria.querySelector("h3").textContent);
        const categoriaCoincide = nomeCategoria.includes(termo);
        let itensVisiveis = 0;

        categoria.querySelectorAll(".item-cardapio").forEach(function(item) {
            const nome = normalizar(item.querySelector("h4").textContent);
            const descricao = normalizar(item.querySelector("p").textContent);
            const coincide = !termo || categoriaCoincide
                || nome.includes(termo) || descricao.includes(termo);

            item.hidden = !coincide;
            if (coincide) itensVisiveis++;
        });

        categoria.hidden = itensVisiveis === 0;
        encontrados += itensVisiveis;
    });

    if (!termo) {
        mensagemBusca.textContent = "";
    } else if (encontrados === 0) {
        mensagemBusca.textContent = "Nenhum prato encontrado no cardápio.";
    } else {
        mensagemBusca.textContent = `${encontrados} opção(ões) encontrada(s).`;
    }
}

if (formularioPratos) {
    formularioPratos.addEventListener("submit", function(event) {
        event.preventDefault();
        filtrarCardapio(campoBusca.value);
    });

    // Filtra enquanto a pessoa digita.
    campoBusca.addEventListener("input", function() {
        filtrarCardapio(campoBusca.value);
    });
}

if (botaoListarTodos) {
    botaoListarTodos.addEventListener("click", function() {
        campoBusca.value = "";
        filtrarCardapio("");
    });
}

// Confirma o envio do formulário de contato na própria página.
const formularioContato = document.querySelector("#formularioContato");
if (formularioContato) {
    formularioContato.addEventListener("submit", function(event) {
        event.preventDefault();
        const mensagemContato = document.querySelector("#mensagemContato");
        mensagemContato.textContent = "Obrigado por entrar em contato com o Satoshy!";
        mensagemContato.classList.add("mensagem-atualizada");
        formularioContato.reset();
    });
}
