const API_BASE = "http://localhost:5000/api";
let carrinho = [];
function formatarMoeda(valor) {
return Number(valor).toFixed(2).replace(".", ",");
}
// =====================================================
// 1. CARDÁPIO DINÂMICO (GET /api/pratos)
// =====================================================
const listaCardapio = document.querySelector("#listaCardapio");
const formularioPratos = document.querySelector("#formularioPratos");
const campoBusca = document.querySelector("#buscaPrato");
const mensagemBusca = document.querySelector("#mensagemBusca");
const botaoListarTodos = document.querySelector("#listarTodos");
async function carregarCardapio(busca = "") {
if (!listaCardapio) return;
mensagemBusca.textContent = "Buscando pratos no servidor...";
try {
const url = busca
? `𝐴𝑃𝐼 {encodeURIComponent(busca)}`
𝐵
𝐴𝑆𝐸/𝑝𝑟𝑎𝑡𝑜𝑠? 𝑏𝑢𝑠𝑐𝑎 =
: `${API_BASE}/pratos`;
const resposta = await fetch(url);
if (!resposta.ok) throw new Error("Erro ao consultar a API de pratos.");
const pratos = await resposta.json();
listaCardapio.innerHTML = "";
if (pratos.length === 0) {
mensagemBusca.textContent = "Nenhum prato encontrado no cardápio.";
return;
}
mensagemBusca.textContent = busca
? `${pratos.length} opção(ões) encontrada(s).`
: `Exibindo ${pratos.length} pratos disponíveis.`;
const porCategoria = {};
pratos.forEach((prato) => {
if (!porCategoria[prato.categoria]) {
porCategoria[prato.categoria] = [];
}
porCategoria[prato.categoria].push(prato);
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
card.innerHTML = `
<div>
<h4>${prato.nome}</h4>
<p>${prato.descricao}</p>
</div>
<div class="item-acoes">
<strong>R$ ${formatarMoeda(prato.preco)}</strong>
<button type="button" class="btn-pequeno">+ Adicionar</button>
</div>
`;
card.querySelector("button").addEventListener("click", () => {
adicionarAoCarrinho(prato);
});
secao.appendChild(card);
});
listaCardapio.appendChild(secao);
});
} catch (erro) {
console.error(erro);
mensagemBusca.textContent = "Não foi possível conectar à API Flask. Verifique se
python app.py está rodando.";
}
}
if (formularioPratos) {
formularioPratos.addEventListener("submit", (event) => {
event.preventDefault();
carregarCardapio(campoBusca.value.trim());
});
}
if (botaoListarTodos) {
botaoListarTodos.addEventListener("click", () => {
campoBusca.value = "";
carregarCardapio("");
});
}
// =====================================================
// 2. CARRINHO E CRIAÇÃO DE PEDIDO (POST /api/pedidos)
// =====================================================
const listaCarrinhoEl = document.querySelector("#listaCarrinho");
const totalCarrinhoEl = document.querySelector("#totalCarrinho");
const formularioPedido = document.querySelector("#formularioPedido");
const mensagemPedido = document.querySelector("#mensagemPedido");
function adicionarAoCarrinho(prato) {
const existente = carrinho.find((item) => item.id_prato === prato.id);
if (existente) {
existente.quantidade += 1;
} else {
carrinho.push({
id_prato: prato.id,
nome: prato.nome,
preco: prato.preco,
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
if (!listaCarrinhoEl) return;
listaCarrinhoEl.innerHTML = "";
if (carrinho.length === 0) {
listaCarrinhoEl.innerHTML = "<li>Nenhum item adicionado ao pedido ainda.</li>";
totalCarrinhoEl.textContent = "0,00";
return;
}
let total = 0;
carrinho.forEach((item) => {
const subtotal = item.preco * item.quantidade;
total += subtotal;
const li = document.createElement("li");
li.innerHTML = `
<span>${item.quantidade}x 𝑖𝑡𝑒𝑚. 𝑛𝑜𝑚𝑒(𝑅 ${formatarMoeda(subtotal)})</span>
<button type="button" class="btn-pequeno btn-excluir">Remover</button>
`;
li.querySelector("button").addEventListener("click", () =>
removerDoCarrinho(item.id_prato));
listaCarrinhoEl.appendChild(li);
});
totalCarrinhoEl.textContent = formatarMoeda(total);
}
if (formularioPedido) {
formularioPedido.addEventListener("submit", async (event) => {
event.preventDefault();
if (carrinho.length === 0) {
mensagemPedido.textContent = "Adicione pelo menos um prato ao pedido antes de
finalizar.";
return;
}
const btn = document.querySelector("#btnEnviarPedido");
btn.disabled = true;
mensagemPedido.textContent = "Enviando pedido...";
const payload = {
cliente: {
nome: document.querySelector("#clienteNome").value.trim(),
email: document.querySelector("#clienteEmail").value.trim(),
telefone: document.querySelector("#clienteTelefone").value.trim(),
},
itens: carrinho.map((i) => ({
id_prato: i.id_prato,
quantidade: i.quantidade,
})),
};
try {
const resposta = await fetch(`${API_BASE}/pedidos`, {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify(payload),
});
const dados = await resposta.json();
if (!resposta.ok) throw new Error(dados.erro || "Erro ao registrar pedido.");
mensagemPedido.textContent = `Pedido #${dados.id} registrado com sucesso!`;
mensagemPedido.classList.add("mensagem-atualizada");
carrinho = [];
atualizarCarrinhoDOM();
formularioPedido.reset();
await carregarPedidos();
} catch (erro) {
mensagemPedido.textContent = `Falha ao enviar pedido: ${erro.message}`;
} finally {
btn.disabled = false;
}
});
}
// =====================================================
// 3. LISTAR, ATUALIZAR E EXCLUIR PEDIDOS (GET / PUT / DELETE)
// =====================================================
const listaPedidosEl = document.querySelector("#listaPedidos");
async function carregarPedidos() {
if (!listaPedidosEl) return;
try {
const resposta = await fetch(`${API_BASE}/pedidos`);
if (!resposta.ok) throw new Error("Erro ao listar pedidos.");
const pedidos = await resposta.json();
listaPedidosEl.innerHTML = "";
if (pedidos.length === 0) {
listaPedidosEl.innerHTML = "<p>Nenhum pedido registrado ainda.</p>";
return;
}
pedidos.forEach((pedido) => {
const div = document.createElement("div");
div.className = "card-pedido";
const resumoItens = pedido.itens
.map((i) => `${i.quantidade}x ${i.nome_prato}`)
.join(", ");
div.innerHTML = `
<h4>Pedido #${pedido.id} — 𝑝𝑒𝑑𝑖𝑑𝑜. 𝑐𝑙𝑖𝑒𝑛𝑡𝑒. 𝑛𝑜𝑚𝑒({pedido.status})</h4>
<p><strong>Itens:</strong> ${resumoItens}</p>
<p><strong>Total:</strong> R$ ${formatarMoeda(pedido.valor_total)}</p>
<div class="card-pedido-acoes">
<select aria-label="Status do pedido ${pedido.id}">
<option value="ABERTO" ${pedido.status === "ABERTO" ? "selected" :
""}>ABERTO</option>
<option value="EM_PREPARO" ${pedido.status === "EM_PREPARO" ?
"selected" : ""}>EM_PREPARO</option>
<option value="ENTREGUE" ${pedido.status === "ENTREGUE" ? "selected"
: ""}>ENTREGUE</option>
<option value="CANCELADO" ${pedido.status === "CANCELADO" ?
"selected" : ""}>CANCELADO</option>
</select>
<button type="button" class="btn-pequeno btn-salvar-status">Atualizar
Status</button>
<button type="button" class="btn-pequeno btn-excluir">Excluir Pedido</button>
</div>
`;
const selectStatus = div.querySelector("select");
div.querySelector(".btn-salvar-status").addEventListener("click", () => {
atualizarStatusPedido(pedido.id, selectStatus.value);
});
div.querySelector(".btn-excluir").addEventListener("click", () => {
excluirPedido(pedido.id);
});
listaPedidosEl.appendChild(div);
});
} catch (erro) {
listaPedidosEl.innerHTML = "<p>Erro ao carregar pedidos do servidor.</p>";
}
}
async function atualizarStatusPedido(idPedido, novoStatus) {
try {
const resposta = await fetch(`𝐴𝑃𝐼 {idPedido}`, {
𝐵
𝐴𝑆𝐸/𝑝𝑒𝑑𝑖𝑑𝑜𝑠/
method: "PUT",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ status: novoStatus }),
});
if (!resposta.ok) throw new Error("Não foi possível atualizar o status.");
await carregarPedidos();
} catch (erro) {
alert(erro.message);
}
}
async function excluirPedido(idPedido) {
if (!confirm(`Deseja realmente excluir o Pedido #${idPedido}?`)) return;
try {
const resposta = await fetch(`𝐴𝑃𝐼 {idPedido}`, {
𝐵
𝐴𝑆𝐸/𝑝𝑒𝑑𝑖𝑑𝑜𝑠/
method: "DELETE",
});
if (!resposta.ok) throw new Error("Não foi possível excluir o pedido.");
await carregarPedidos();
} catch (erro) {
alert(erro.message);
}
}
// =====================================================
// 4. FORMULÁRIO DE CONTATO (POST /api/contato)
// =====================================================
const formularioContato = document.querySelector("#formularioContato");
if (formularioContato) {
formularioContato.addEventListener("submit", async (event) => {
event.preventDefault();
const mensagemContato = document.querySelector("#mensagemContato");
const botao = document.querySelector("#botaoMensagem");
botao.disabled = true;
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
const dados = await resposta.json();
if (!resposta.ok) throw new Error(dados.erro || "Erro ao enviar mensagem.");
mensagemContato.textContent = dados.mensagem;
mensagemContato.classList.add("mensagem-atualizada");
formularioContato.reset();
} catch (erro) {
mensagemContato.textContent = `Erro: ${erro.message}`;
} finally {
botao.disabled = false;
}
});
}
document.addEventListener("DOMContentLoaded", () => {
carregarCardapio();
carregarPedidos();
});