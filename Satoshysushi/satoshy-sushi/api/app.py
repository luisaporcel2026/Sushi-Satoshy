CÓDIGO
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import Conexao, CAMINHO_BANCO
from models import Categoria, Prato, Cliente, Pedido, ItemPedido, MensagemContato
from dao import CategoriaDAO, PratoDAO, ClienteDAO, PedidoDAO,
MensagemContatoDAO
app = Flask(__name__)
CORS(app)
conexao = Conexao()
if not CAMINHO_BANCO.exists():
conexao.criar_banco()
categoria_dao = CategoriaDAO(conexao)
prato_dao = PratoDAO(conexao)
cliente_dao = ClienteDAO(conexao)
pedido_dao = PedidoDAO(conexao)
contato_dao = MensagemContatoDAO(conexao)
@app.route("/api/status", methods=["GET"])
def status():
return jsonify({"banco": "conectado" if conexao.testar() else "erro"})
@app.route("/api/categorias", methods=["GET"])
def listar_categorias():
categorias = categoria_dao.buscar_todas()
return jsonify([c.to_dict() for c in categorias])
# ===== PRATOS =====
@app.route("/api/pratos", methods=["GET"])
def listar_pratos():
busca = request.args.get("busca", "").strip()
pratos = prato_dao.buscar_todos(busca)
return jsonify([p.to_dict() for p in pratos])
@app.route("/api/pratos/<int:prato_id>", methods=["GET"])
def buscar_prato(prato_id):
prato = prato_dao.buscar_por_id(prato_id)
if not prato:
return jsonify({"erro": "Prato não encontrado"}), 404
return jsonify(prato.to_dict())
@app.route("/api/pratos", methods=["POST"])
def criar_prato():
dados = request.get_json(silent=True) or {}
if not all(k in dados for k in ("nome", "descricao", "preco", "id_categoria")):
return jsonify({"erro": "Campos obrigatórios: nome, descricao, preco,
id_categoria"}), 400
try:
prato = Prato(
None,
dados["nome"].strip(),
dados["descricao"].strip(),
float(dados["preco"]),
int(dados["id_categoria"]),
dados.get("disponivel", True),
)
novo_id = prato_dao.inserir(prato)
return jsonify({"id": novo_id, "mensagem": "Prato cadastrado com sucesso!"}),
201
except (ValueError, sqlite3.IntegrityError) as e:
return jsonify({"erro": f"Dados inválidos: {e}"}), 400
@app.route("/api/pratos/<int:prato_id>", methods=["PUT"])
def atualizar_prato(prato_id):
if not prato_dao.buscar_por_id(prato_id):
return jsonify({"erro": "Prato não encontrado"}), 404
dados = request.get_json(silent=True) or {}
try:
prato = Prato(
prato_id,
dados["nome"].strip(),
dados["descricao"].strip(),
float(dados["preco"]),
int(dados["id_categoria"]),
dados.get("disponivel", True),
)
prato_dao.atualizar(prato_id, prato)
return jsonify({"mensagem": "Prato atualizado com sucesso!"})
except (KeyError, ValueError, sqlite3.IntegrityError) as e:
return jsonify({"erro": f"Dados inválidos: {e}"}), 400
@app.route("/api/pratos/<int:prato_id>", methods=["DELETE"])
def remover_prato(prato_id):
try:
if not prato_dao.remover(prato_id):
return jsonify({"erro": "Prato não encontrado"}), 404
return jsonify({"mensagem": "Prato removido com sucesso!"})
except sqlite3.IntegrityError:
return jsonify({"erro": "Não é possível excluir um prato que já possui pedidos."}),
400
# ===== CLIENTES =====
@app.route("/api/clientes", methods=["GET"])
def listar_clientes():
clientes = cliente_dao.buscar_todos()
return jsonify([c.to_dict() for c in clientes])
@app.route("/api/clientes/<int:id_cliente>", methods=["GET"])
def buscar_cliente(id_cliente):
cliente = cliente_dao.buscar_por_id(id_cliente)
if not cliente:
return jsonify({"erro": "Cliente não encontrado"}), 404
return jsonify(cliente.to_dict())
@app.route("/api/clientes", methods=["POST"])
def criar_cliente():
dados = request.get_json(silent=True) or {}
nome = dados.get("nome", "").strip()
email = dados.get("email", "").strip()
telefone = dados.get("telefone", "").strip() or None
if not nome or not email:
return jsonify({"erro": "Nome e e-mail são obrigatórios."}), 400
existente = cliente_dao.buscar_por_email(email)
if existente:
return jsonify({"id": existente.id_cliente, "cliente": existente.to_dict(),
"mensagem": "Cliente já cadastrado."}), 200
cliente = Cliente(None, nome, email, telefone)
novo_id = cliente_dao.inserir(cliente)
cliente.id_cliente = novo_id
return jsonify({"id": novo_id, "cliente": cliente.to_dict(), "mensagem": "Cliente
cadastrado com sucesso!"}), 201
@app.route("/api/clientes/<int:id_cliente>", methods=["PUT"])
def atualizar_cliente(id_cliente):
if not cliente_dao.buscar_por_id(id_cliente):
return jsonify({"erro": "Cliente não encontrado"}), 404
dados = request.get_json(silent=True) or {}
try:
cliente = Cliente(id_cliente, dados["nome"].strip(), dados["email"].strip(),
dados.get("telefone"))
cliente_dao.atualizar(id_cliente, cliente)
return jsonify({"mensagem": "Cliente atualizado com sucesso!"})
except (KeyError, sqlite3.IntegrityError) as e:
return jsonify({"erro": f"Erro ao atualizar cliente: {e}"}), 400
@app.route("/api/clientes/<int:id_cliente>", methods=["DELETE"])
def remover_cliente(id_cliente):
try:
if not cliente_dao.remover(id_cliente):
return jsonify({"erro": "Cliente não encontrado"}), 404
return jsonify({"mensagem": "Cliente removido com sucesso!"})
except sqlite3.IntegrityError:
return jsonify({"erro": "Cliente possui pedidos vinculados."}), 400
# ===== PEDIDOS =====
@app.route("/api/pedidos", methods=["GET"])
def listar_pedidos():
pedidos = pedido_dao.buscar_todos()
return jsonify([p.to_dict() for p in pedidos])
@app.route("/api/pedidos/<int:id_pedido>", methods=["GET"])
def buscar_pedido(id_pedido):
pedido = pedido_dao.buscar_por_id(id_pedido)
if not pedido:
return jsonify({"erro": "Pedido não encontrado"}), 404
return jsonify(pedido.to_dict())
@app.route("/api/pedidos", methods=["POST"])
def criar_pedido():
dados = request.get_json(silent=True) or {}
itens_dados = dados.get("itens", [])
if not itens_dados:
return jsonify({"erro": "O pedido deve conter pelo menos 1 item."}), 400
cliente = None
if "id_cliente" in dados and dados["id_cliente"]:
cliente = cliente_dao.buscar_por_id(int(dados["id_cliente"]))
elif "cliente" in dados:
c_dados = dados["cliente"]
email = c_dados.get("email", "").strip()
nome = c_dados.get("nome", "").strip()
telefone = c_dados.get("telefone", "").strip() or None
if not nome or not email:
return jsonify({"erro": "Informe nome e e-mail do cliente."}), 400
cliente = cliente_dao.buscar_por_email(email)
if not cliente:
novo_cid = cliente_dao.inserir(Cliente(None, nome, email, telefone))
cliente = Cliente(novo_cid, nome, email, telefone)
if not cliente:
return jsonify({"erro": "Cliente válido não encontrado."}), 400
pedido = Pedido(None, cliente)
for item_raw in itens_dados:
prato = prato_dao.buscar_por_id(int(item_raw["id_prato"]))
qtd = int(item_raw.get("quantidade", 1))
if not prato or qtd <= 0:
return jsonify({"erro": f"Item inválido: {item_raw}"}), 400
pedido.adicionar_item(ItemPedido(None, prato, qtd, prato.preco))
novo_id = pedido_dao.inserir(pedido)
pedido_salvo = pedido_dao.buscar_por_id(novo_id)
return jsonify({"id": novo_id, "pedido": pedido_salvo.to_dict(), "mensagem":
"Pedido registrado com sucesso!"}), 201
@app.route("/api/pedidos/<int:id_pedido>", methods=["PUT"])
def atualizar_status_pedido(id_pedido):
dados = request.get_json(silent=True) or {}
novo_status = dados.get("status", "").upper()
if novo_status not in Pedido.STATUS:
return jsonify({"erro": f"Status inválido. Use: {', '.join(Pedido.STATUS)}"}), 400
if not pedido_dao.atualizar_status(id_pedido, novo_status):
return jsonify({"erro": "Pedido não encontrado"}), 404
return jsonify({"mensagem": f"Status atualizado para {novo_status}!"})
@app.route("/api/pedidos/<int:id_pedido>", methods=["DELETE"])
def remover_pedido(id_pedido):
if not pedido_dao.remover(id_pedido):
return jsonify({"erro": "Pedido não encontrado"}), 404
return jsonify({"mensagem": "Pedido excluído com sucesso!"})
# ===== CONTATO =====
@app.route("/api/contato", methods=["GET"])
def listar_mensagens():
mensagens = contato_dao.buscar_todas()
return jsonify([m.to_dict() for m in mensagens])
@app.route("/api/contato", methods=["POST"])
def enviar_mensagem():
dados = request.get_json(silent=True) or {}
nome = dados.get("nome", "").strip()
email = dados.get("email", "").strip()
texto = dados.get("texto", "").strip()
if not nome or not email or not texto:
return jsonify({"erro": "Preencha nome, e-mail e mensagem."}), 400
msg = MensagemContato(None, nome, email, texto)
novo_id = contato_dao.inserir(msg)
return jsonify({"id": novo_id, "mensagem": "Mensagem enviada e salva no banco
com sucesso!"}), 201
@app.route("/api/contato/<int:id_mensagem>", methods=["DELETE"])
def remover_mensagem(id_mensagem):
if not contato_dao.remover(id_mensagem):
return jsonify({"erro": "Mensagem não encontrada"}), 404
return jsonify({"mensagem": "Mensagem removida!"})
@app.route("/")
def inicio():
return jsonify({
"mensagem": "API Completa do Restaurante Satoshy (Etapa 2)",
"rotas": [
"GET/POST /api/pratos",
"GET/PUT/DELETE /api/pratos/<id>",
"GET/POST /api/clientes",
"GET/PUT/DELETE /api/clientes/<id>",
"GET/POST /api/pedidos",
"GET/PUT/DELETE /api/pedidos/<id>",
"GET/POST /api/contato",
"DELETE /api/contato/<id>",
],
})
if __name__ == "__main__":
app.run(debug=True, port=5000)