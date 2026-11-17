const API_BASE = "http://localhost:5000/api";
let carrinho = [];

function moeda(valor) {
  return Number(valor || 0).toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

async function requisitar(url, opcoes = {}) {
  const resposta = await fetch(url, opcoes);
  const tipo = resposta.headers.get("content-type") || "";
  const dados = tipo.includes("application/json")
    ? await resposta.json()
    : {};

  if (!resposta.ok) {
    throw new Error(dados.erro || `Erro na requisição (${resposta.status}).`);
  }

  return dados;
}

// CARDÁPIO: GET /api/pratos
const listaCardapio = document.querySelector("#listaCardapio");
const formularioPratos = document.querySelector("#formularioPratos");
const campoBusca = document.querySelector("#buscaPrato");
const mensagemBusca = document.querySelector("#mensagemBusca");

async function carregarCardapio(busca = "") {
  if (!listaCardapio) return;

  mensagemBusca.textContent = "Carregando cardápio...";

  try {
    const url = busca
      ? `${API_BASE}/pratos?busca=${encodeURIComponent(busca)}`
      : `${API_BASE}/pratos`;

    const pratos = await requisitar(url);
    listaCardapio.replaceChildren();

    if (pratos.length === 0) {
      mensagemBusca.textContent = "Nenhum prato encontrado.";
      return;
    }

    mensagemBusca.textContent = `${pratos.length} prato(s) disponível(is).`;

    const grupos = new Map();

    pratos.forEach((prato) => {
      const categoria = prato.categoria || "Outros";

      if (!grupos.has(categoria)) {
        grupos.set(categoria, []);
      }

      grupos.get(categoria).push(prato);
    });

    grupos.forEach((itens, categoria) => {
      const secao = document.createElement("section");
      secao.className = "categoria-cardapio";

      const titulo = document.createElement("h3");
      titulo.textContent = categoria;
      secao.append(titulo);

      itens.forEach((prato) => {
        const card = document.createElement("article");
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
        preco.textContent = `R$ ${moeda(prato.preco)}`;

        const botao = document.createElement("button");
        botao.type = "button";
        botao.className = "btn-pequeno";
        botao.textContent = "Adicionar ao pedido";
        botao.addEventListener("click", () => adicionarAoCarrinho(prato));

        acoes.append(preco, botao);
        card.append(informacoes, acoes);
        secao.append(card);
      });

      listaCardapio.append(secao);
    });
  } catch (erro) {
    console.error(erro);
    mensagemBusca.textContent =
      `Não foi possível carregar o cardápio. ${erro.message} ` +
      "Confira se a API Flask está iniciada.";
  }
}

if (formularioPratos) {
  formularioPratos.addEventListener("submit", (evento) => {
    evento.preventDefault();
    carregarCardapio(campoBusca.value.trim());
  });

  document.querySelector("#listarTodos")?.addEventListener("click", () => {
    campoBusca.value = "";
    carregarCardapio();
  });
}

// CARRINHO E PEDIDOS: POST /api/pedidos
const listaCarrinho = document.querySelector("#listaCarrinho");
const totalCarrinho = document.querySelector("#totalCarrinho");
const formularioPedido = document.querySelector("#formularioPedido");
const mensagemPedido = document.querySelector("#mensagemPedido");

function atualizarCarrinho() {
  if (!listaCarrinho) return;

  listaCarrinho.replaceChildren();

  if (carrinho.length === 0) {
    const vazio = document.createElement("li");
    vazio.textContent = "Nenhum item adicionado ao pedido ainda.";
    listaCarrinho.append(vazio);
    totalCarrinho.textContent = "0,00";
    return;
  }

  let total = 0;

  carrinho.forEach((item) => {
    const subtotal = item.preco * item.quantidade;
    total += subtotal;

    const li = document.createElement("li");
    const texto = document.createElement("span");
    texto.textContent =
      `${item.quantidade}x ${item.nome} — R$ ${moeda(subtotal)}`;

    const botaoRemover = document.createElement("button");
    botaoRemover.type = "button";
    botaoRemover.className = "btn-pequeno btn-excluir";
    botaoRemover.textContent = "Remover";

    botaoRemover.addEventListener("click", () => {
      carrinho = carrinho.filter((produto) => produto.id !== item.id);
      atualizarCarrinho();
    });

    li.append(texto, botaoRemover);
    listaCarrinho.append(li);
  });

  totalCarrinho.textContent = moeda(total);
}

function adicionarAoCarrinho(prato) {
  const itemExistente = carrinho.find((item) => item.id === prato.id);

  if (itemExistente) {
    itemExistente.quantidade += 1;
  } else {
    carrinho.push({
      id: prato.id,
      nome: prato.nome,
      preco: Number(prato.preco),
      quantidade: 1,
    });
  }

  atualizarCarrinho();

  if (mensagemPedido) {
    mensagemPedido.textContent = `${prato.nome} adicionado ao pedido.`;
  }
}

if (formularioPedido) {
  formularioPedido.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    if (carrinho.length === 0) {
      mensagemPedido.textContent =
        "Adicione pelo menos um prato antes de finalizar.";
      return;
    }

    const botao = document.querySelector("#btnEnviarPedido");
    botao.disabled = true;
    mensagemPedido.textContent = "Enviando pedido...";

    const dadosPedido = {
      cliente: {
        nome: document.querySelector("#clienteNome").value.trim(),
        email: document.querySelector("#clienteEmail").value.trim(),
        telefone: document.querySelector("#clienteTelefone").value.trim(),
      },
      itens: carrinho.map((item) => ({
        id_prato: item.id,
        quantidade: item.quantidade,
      })),
    };

    try {
      const dados = await requisitar(`${API_BASE}/pedidos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dadosPedido),
      });

      mensagemPedido.textContent =
        `Pedido #${dados.id} registrado com sucesso.`;

      carrinho = [];
      atualizarCarrinho();
      formularioPedido.reset();
      await carregarPedidos();
    } catch (erro) {
      mensagemPedido.textContent =
        `Não foi possível enviar o pedido: ${erro.message}`;
    } finally {
      botao.disabled = false;
    }
  });
}

// PEDIDOS: GET, PUT e DELETE /api/pedidos
const listaPedidos = document.querySelector("#listaPedidos");
const statusDisponiveis = [
  "ABERTO",
  "EM_PREPARO",
  "ENTREGUE",
  "CANCELADO",
];

async function carregarPedidos() {
  if (!listaPedidos) return;

  listaPedidos.textContent = "Carregando pedidos...";

  try {
    const pedidos = await requisitar(`${API_BASE}/pedidos`);
    listaPedidos.replaceChildren();

    if (pedidos.length === 0) {
      listaPedidos.textContent = "Nenhum pedido registrado ainda.";
      return;
    }

    pedidos.forEach((pedido) => {
      const card = document.createElement("article");
      card.className = "card-pedido";

      const titulo = document.createElement("h4");
      titulo.textContent =
        `Pedido #${pedido.id} — ${pedido.cliente?.nome || "Cliente"} ` +
        `(${pedido.status})`;

      const itens = document.createElement("p");
      itens.textContent =
        "Itens: " +
        (pedido.itens || [])
          .map((item) => `${item.quantidade}x ${item.nome_prato}`)
          .join(", ");

      const total = document.createElement("p");
      total.textContent = `Total: R$ ${moeda(pedido.valor_total)}`;

      const acoes = document.createElement("div");
      acoes.className = "card-pedido-acoes";

      const seletorStatus = document.createElement("select");
      seletorStatus.setAttribute(
        "aria-label",
        `Status do pedido ${pedido.id}`
      );

      statusDisponiveis.forEach((status) => {
        const opcao = document.createElement("option");
        opcao.value = status;
        opcao.textContent = status.replace("_", " ");
        opcao.selected = status === pedido.status;
        seletorStatus.append(opcao);
      });

      const botaoAtualizar = document.createElement("button");
      botaoAtualizar.type = "button";
      botaoAtualizar.className = "btn-pequeno btn-salvar-status";
      botaoAtualizar.textContent = "Atualizar status";
      botaoAtualizar.addEventListener("click", () => {
        atualizarStatusPedido(pedido.id, seletorStatus.value);
      });

      const botaoExcluir = document.createElement("button");
      botaoExcluir.type = "button";
      botaoExcluir.className = "btn-pequeno btn-excluir";
      botaoExcluir.textContent = "Excluir pedido";
      botaoExcluir.addEventListener("click", () => excluirPedido(pedido.id));

      acoes.append(seletorStatus, botaoAtualizar, botaoExcluir);
      card.append(titulo, itens, total, acoes);
      listaPedidos.append(card);
    });
  } catch (erro) {
    listaPedidos.textContent = `Erro ao carregar pedidos: ${erro.message}`;
  }
}

async function atualizarStatusPedido(id, status) {
  try {
    await requisitar(`${API_BASE}/pedidos/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });

    await carregarPedidos();
  } catch (erro) {
    alert(`Não foi possível atualizar o pedido: ${erro.message}`);
  }
}

async function excluirPedido(id) {
  if (!confirm(`Deseja excluir o pedido #${id}?`)) return;

  try {
    await requisitar(`${API_BASE}/pedidos/${id}`, {
      method: "DELETE",
    });

    await carregarPedidos();
  } catch (erro) {
    alert(`Não foi possível excluir o pedido: ${erro.message}`);
  }
}

// CONTATO: POST /api/contato
const formularioContato = document.querySelector("#formularioContato");

if (formularioContato) {
  formularioContato.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    const mensagem = document.querySelector("#mensagemContato");
    const botao = document.querySelector("#botaoMensagem");

    botao.disabled = true;
    mensagem.textContent = "Enviando mensagem...";

    const dadosContato = {
      nome: document.querySelector("#nome").value.trim(),
      email: document.querySelector("#email").value.trim(),
      texto: document.querySelector("#textoMensagem").value.trim(),
    };

    try {
      const dados = await requisitar(`${API_BASE}/contato`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dadosContato),
      });

      mensagem.textContent = dados.mensagem;
      formularioContato.reset();
    } catch (erro) {
      mensagem.textContent = `Não foi possível enviar: ${erro.message}`;
    } finally {
      botao.disabled = false;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  carregarCardapio();
  carregarPedidos();
  atualizarCarrinho();
});