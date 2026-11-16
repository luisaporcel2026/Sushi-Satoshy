// Endereço da API Flask que fornece os dados do Satoshy.
const API_BASE = "http://127.0.0.1:5000/api";
let carrinho = [];

function formatarMoeda(valor) {
    return Number(valor).toFixed(2).replace(".", ",");
}

async function lerResposta(resposta) {
    const dados = await resposta.json();
    if (!resposta.ok) {
        throw new Error(dados.erro || "Não foi possível concluir a solicitação.");
    }
    return dados;
}

// 1. CARDÁPIO: busca os pratos cadastrados no banco de dados.
const listaCardapio = document.querySelector("#listaCardapio");
const formularioPratos = document.querySelector("#formularioPratos");
const campoBusca = document.querySelector("#buscaPrato");
const mensagemBusca = document.querySelector("#mensagemBusca");
const botaoListarTodos = document.querySelector("#listarTodos");

async function carregarCardapio(busca = "") {
    if (!listaCardapio || !mensagemBusca) return;

    mensagemBusca.textContent = "Carregando cardápio...";
    listaCardapio.innerHTML = "";

    try {
        const termo = busca.trim();
        const url = termo
            ? `${API_BASE}/pratos?busca=${encodeURIComponent(termo)}`
            : `${API_BASE}/pratos`;

        const resposta = await fetch(url);
        const pratos = await lerResposta(resposta);

        if (!Array.isArray(pratos) || pratos.length === 0) {
            mensagemBusca.textContent = "Nenhum prato encontrado no cardápio.";
            return;
        }

        mensagemBusca.textContent = termo
            ? `${pratos.length} opção(ões) encontrada(s).`
            : `Exibindo ${pratos.length} pratos disponíveis.`;

        const porCategoria = {};
        pratos.forEach((prato) => {
            const categoria = prato.categoria || "Outros";
            if (!porCategoria[categoria]) porCategoria[categoria] = [];
            porCategoria[categoria].push(prato);
        });

        Object.entries(porCategoria).forEach(([categoria, itens]) => {
            const secao = document.createElement("section");
            secao.className = "categoria-cardapio";

            const titulo = document.createElement("h3");
            titulo.textContent = categoria;
            secao.appendChild(titulo);

            itens.forEach((prato) => {
                const card = document.createElement("div");
                card.className = "item-cardapio";

                const informacoes = document.createElement("div");
                const nome = document.createElement("h4");
                nome.textContent = prato.nome;
                const descricao = document.createElement("p");
                descricao.textContent = prato.descricao;
                informacoes.append(nome, descricao);

                const acoes = document.createElement("div");
                acoes.className = "item-acoes";
                const preco = document.createElement("strong");
                preco.textContent = `R$ ${formatarMoeda(prato.preco)}`;

                const botaoAdicionar = document.createElement("button");
                botaoAdicionar.type = "button";
                botaoAdicionar.className = "btn-pequeno";
                botaoAdicionar.textContent = "+ Adicionar";
                botaoAdicionar.addEventListener("click", () => adicionarAoCarrinho(prato));

                acoes.append(preco, botaoAdicionar);
                card.append(informacoes, acoes);
                secao.appendChild(card);
            });

            listaCardapio.appendChild(secao);
        });
    } catch (erro) {
        console.error("Erro ao carregar o cardápio:", erro);
        mensagemBusca.textContent =
            "Não foi possível carregar o cardápio. Inicie a API Flask e atualize esta página.";
    }
}

if (formularioPratos) {
    formularioPratos.addEventListener("submit", (event) => {
        event.preventDefault();
        carregarCardapio(campoBusca ? campoBusca.value : "");
    });
}

if (botaoListarTodos) {
    botaoListarTodos.addEventListener("click", () => {
        if (campoBusca) campoBusca.value = "";
        carregarCardapio();
    });
}

// 2. CARRINHO E FINALIZAÇÃO DO PEDIDO.
const listaCarrinhoEl = document.querySelector("#listaCarrinho");
const totalCarrinhoEl = document.querySelector("#totalCarrinho");
const formularioPedido = document.querySelector("#formularioPedido");
const mensagemPedido = document.querySelector("#mensagemPedido");

function adicionarAoCarrinho(prato) {
    const idPrato = prato.id;
    const existente = carrinho.find((item) => item.id_prato === idPrato);

    if (existente) {
        existente.quantidade += 1;
    } else {
        carrinho.push({
            id_prato: idPrato,
            nome: prato.nome,
            preco: Number(prato.preco),
            quantidade: 1,
        });
    }

    atualizarCarrinhoDOM();
}

function removerDoCarrinho(idPrato) {
    carrinho = carrinho.filter((item) => item.id_prato !== idPrato);
    atualizarCarrinhoDOM();
}

function atualizarCarrinhoDOM() {
    if (!listaCarrinhoEl || !totalCarrinhoEl) return;

    listaCarrinhoEl.innerHTML = "";
    if (carrinho.length === 0) {
        const itemVazio = document.createElement("li");
        itemVazio.textContent = "Nenhum item adicionado ao pedido ainda.";
        listaCarrinhoEl.appendChild(itemVazio);
        totalCarrinhoEl.textContent = "0,00";
        return;
    }

    let total = 0;
    carrinho.forEach((item) => {
        const subtotal = item.preco * item.quantidade;
        total += subtotal;

        const li = document.createElement("li");
        const texto = document.createElement("span");
        texto.textContent = `${item.quantidade}x ${item.nome} (R$ ${formatarMoeda(subtotal)})`;

        const botaoRemover = document.createElement("button");
        botaoRemover.type = "button";
        botaoRemover.className = "btn-pequeno btn-excluir";
        botaoRemover.textContent = "Remover";
        botaoRemover.addEventListener("click", () => removerDoCarrinho(item.id_prato));

        li.append(texto, botaoRemover);
        listaCarrinhoEl.appendChild(li);
    });

    totalCarrinhoEl.textContent = formatarMoeda(total);
}

if (formularioPedido) {
    formularioPedido.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!mensagemPedido) return;
        if (carrinho.length === 0) {
            mensagemPedido.textContent = "Adicione pelo menos um prato antes de finalizar o pedido.";
            return;
        }

        const botao = document.querySelector("#btnEnviarPedido");
        if (botao) botao.disabled = true;
        mensagemPedido.textContent = "Enviando pedido...";

        const payload = {
            cliente: {
                nome: document.querySelector("#clienteNome").value.trim(),
                email: document.querySelector("#clienteEmail").value.trim(),
                telefone: document.querySelector("#clienteTelefone").value.trim(),
            },
            itens: carrinho.map((item) => ({
                id_prato: item.id_prato,
                quantidade: item.quantidade,
            })),
        };

        try {
            const resposta = await fetch(`${API_BASE}/pedidos`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const dados = await lerResposta(resposta);
            mensagemPedido.textContent = `Pedido #${dados.id} registrado com sucesso!`;
            mensagemPedido.classList.add("mensagem-atualizada");
            carrinho = [];
            atualizarCarrinhoDOM();
            formularioPedido.reset();
            await carregarPedidos();
        } catch (erro) {
            mensagemPedido.textContent = `Falha ao enviar pedido: ${erro.message}`;
        } finally {
            if (botao) botao.disabled = false;
        }
    });
}

// 3. LISTAGEM, ATUALIZAÇÃO E EXCLUSÃO DE PEDIDOS.
const listaPedidosEl = document.querySelector("#listaPedidos");

async function carregarPedidos() {
    if (!listaPedidosEl) return;

    try {
        const resposta = await fetch(`${API_BASE}/pedidos`);
        const pedidos = await lerResposta(resposta);
        listaPedidosEl.innerHTML = "";

        if (pedidos.length === 0) {
            listaPedidosEl.textContent = "Nenhum pedido registrado ainda.";
            return;
        }

        pedidos.forEach((pedido) => {
            const card = document.createElement("div");
            card.className = "card-pedido";

            const titulo = document.createElement("h4");
            titulo.textContent = `Pedido #${pedido.id} — ${pedido.cliente.nome} (${pedido.status})`;

            const itens = document.createElement("p");
            const resumo = (pedido.itens || [])
                .map((item) => `${item.quantidade}x ${item.nome_prato}`)
                .join(", ");
            itens.textContent = `Itens: ${resumo || "Nenhum item"}`;

            const total = document.createElement("p");
            total.textContent = `Total: R$ ${formatarMoeda(pedido.valor_total)}`;

            const acoes = document.createElement("div");
            acoes.className = "card-pedido-acoes";

            const selectStatus = document.createElement("select");
            selectStatus.setAttribute("aria-label", `Status do pedido ${pedido.id}`);
            ["ABERTO", "EM_PREPARO", "ENTREGUE", "CANCELADO"].forEach((status) => {
                const opcao = document.createElement("option");
                opcao.value = status;
                opcao.textContent = status;
                opcao.selected = pedido.status === status;
                selectStatus.appendChild(opcao);
            });

            const botaoAtualizar = document.createElement("button");
            botaoAtualizar.type = "button";
            botaoAtualizar.className = "btn-pequeno btn-salvar-status";
            botaoAtualizar.textContent = "Atualizar status";
            botaoAtualizar.addEventListener("click", () => {
                atualizarStatusPedido(pedido.id, selectStatus.value);
            });

            const botaoExcluir = document.createElement("button");
            botaoExcluir.type = "button";
            botaoExcluir.className = "btn-pequeno btn-excluir";
            botaoExcluir.textContent = "Excluir pedido";
            botaoExcluir.addEventListener("click", () => excluirPedido(pedido.id));

            acoes.append(selectStatus, botaoAtualizar, botaoExcluir);
            card.append(titulo, itens, total, acoes);
            listaPedidosEl.appendChild(card);
        });
    } catch (erro) {
        console.error("Erro ao carregar pedidos:", erro);
        listaPedidosEl.textContent = "Não foi possível carregar os pedidos. Verifique se a API está ligada.";
    }
}

async function atualizarStatusPedido(idPedido, novoStatus) {
    try {
        const resposta = await fetch(`${API_BASE}/pedidos/${idPedido}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: novoStatus }),
        });
        await lerResposta(resposta);
        await carregarPedidos();
    } catch (erro) {
        alert(erro.message);
    }
}

async function excluirPedido(idPedido) {
    if (!confirm(`Deseja realmente excluir o pedido #${idPedido}?`)) return;

    try {
        const resposta = await fetch(`${API_BASE}/pedidos/${idPedido}`, {
            method: "DELETE",
        });
        await lerResposta(resposta);
        await carregarPedidos();
    } catch (erro) {
        alert(erro.message);
    }
}

// 4. ENVIO DO FORMULÁRIO DE CONTATO.
const formularioContato = document.querySelector("#formularioContato");

if (formularioContato) {
    formularioContato.addEventListener("submit", async (event) => {
        event.preventDefault();

        const mensagemContato = document.querySelector("#mensagemContato");
        const botao = document.querySelector("#botaoMensagem");
        if (botao) botao.disabled = true;
        mensagemContato.textContent = "Enviando mensagem...";

        const payload = {
            nome: document.querySelector("#nome").value.trim(),
            email: document.querySelector("#email").value.trim(),
            texto: document.querySelector("#textoMensagem").value.trim(),
        };

        try {
            const resposta = await fetch(`${API_BASE}/contato`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const dados = await lerResposta(resposta);
            mensagemContato.textContent = dados.mensagem;
            mensagemContato.classList.add("mensagem-atualizada");
            formularioContato.reset();
        } catch (erro) {
            mensagemContato.textContent = `Erro: ${erro.message}`;
        } finally {
            if (botao) botao.disabled = false;
        }
    });
}

// Carrega automaticamente os dados quando a página abre.
document.addEventListener("DOMContentLoaded", () => {
    if (listaCardapio) carregarCardapio();
    if (listaPedidosEl) carregarPedidos();
    if (listaCarrinhoEl) atualizarCarrinhoDOM();
});
