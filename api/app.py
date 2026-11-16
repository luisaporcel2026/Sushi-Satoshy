"""API REST do restaurante Satoshy."""

import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

from database import Conexao, CAMINHO_BANCO
from models import Prato, Cliente, Pedido, ItemPedido, MensagemContato
from Dao import (
    CategoriaDAO,
    PratoDAO,
    ClienteDAO,
    PedidoDAO,
    MensagemContatoDAO,
)

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
    return jsonify([categoria.to_dict() for categoria in categoria_dao.buscar_todas()])


# PRATOS
@app.route("/api/pratos", methods=["GET"])
def listar_pratos():
    busca = request.args.get("busca", "").strip()
    pratos = prato_dao.buscar_todos(busca)
    return jsonify([prato.to_dict() for prato in pratos])


@app.route("/api/pratos/<int:prato_id>", methods=["GET"])
def buscar_prato(prato_id):
    prato = prato_dao.buscar_por_id(prato_id)
    if not prato:
        return jsonify({"erro": "Prato não encontrado."}), 404
    return jsonify(prato.to_dict())


@app.route("/api/pratos", methods=["POST"])
def criar_prato():
    dados = request.get_json(silent=True) or {}
    campos = ("nome", "descricao", "preco", "id_categoria")
    if not all(campo in dados for campo in campos):
        return jsonify({"erro": "Informe nome, descrição, preço e categoria."}), 400
    try:
        prato = Prato(
            None,
            str(dados["nome"]).strip(),
            str(dados["descricao"]).strip(),
            float(dados["preco"]),
            int(dados["id_categoria"]),
            dados.get("disponivel", True),
        )
        if not prato.nome or not prato.descricao or prato.preco < 0:
            raise ValueError("Confira os dados do prato.")
        novo_id = prato_dao.inserir(prato)
        return jsonify({"id": novo_id, "mensagem": "Prato cadastrado com sucesso!"}), 201
    except (ValueError, TypeError, sqlite3.IntegrityError) as erro:
        return jsonify({"erro": f"Dados inválidos: {erro}"}), 400


@app.route("/api/pratos/<int:prato_id>", methods=["PUT"])
def atualizar_prato(prato_id):
    if not prato_dao.buscar_por_id(prato_id):
        return jsonify({"erro": "Prato não encontrado."}), 404
    dados = request.get_json(silent=True) or {}
    try:
        prato = Prato(
            prato_id,
            str(dados["nome"]).strip(),
            str(dados["descricao"]).strip(),
            float(dados["preco"]),
            int(dados["id_categoria"]),
            dados.get("disponivel", True),
        )
        if not prato.nome or not prato.descricao or prato.preco < 0:
            raise ValueError("Confira os dados do prato.")
        prato_dao.atualizar(prato_id, prato)
        return jsonify({"mensagem": "Prato atualizado com sucesso!"})
    except (KeyError, ValueError, TypeError, sqlite3.IntegrityError) as erro:
        return jsonify({"erro": f"Dados inválidos: {erro}"}), 400


@app.route("/api/pratos/<int:prato_id>", methods=["DELETE"])
def remover_prato(prato_id):
    try:
        if not prato_dao.remover(prato_id):
            return jsonify({"erro": "Prato não encontrado."}), 404
        return jsonify({"mensagem": "Prato removido com sucesso!"})
    except sqlite3.IntegrityError:
        return jsonify({"erro": "Não é possível excluir um prato que já possui pedidos."}), 400


# CLIENTES
@app.route("/api/clientes", methods=["GET"])
def listar_clientes():
    return jsonify([cliente.to_dict() for cliente in cliente_dao.buscar_todos()])


@app.route("/api/clientes/<int:id_cliente>", methods=["GET"])
def buscar_cliente(id_cliente):
    cliente = cliente_dao.buscar_por_id(id_cliente)
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado."}), 404
    return jsonify(cliente.to_dict())


@app.route("/api/clientes", methods=["POST"])
def criar_cliente():
    dados = request.get_json(silent=True) or {}
    nome = str(dados.get("nome", "")).strip()
    email = str(dados.get("email", "")).strip()
    telefone = str(dados.get("telefone", "")).strip() or None
    if not nome or not email:
        return jsonify({"erro": "Nome e e-mail são obrigatórios."}), 400
    existente = cliente_dao.buscar_por_email(email)
    if existente:
        return jsonify({"id": existente.id_cliente, "cliente": existente.to_dict(), "mensagem": "Cliente já cadastrado."}), 200
    try:
        cliente = Cliente(None, nome, email, telefone)
        novo_id = cliente_dao.inserir(cliente)
        cliente.id_cliente = novo_id
        return jsonify({"id": novo_id, "cliente": cliente.to_dict(), "mensagem": "Cliente cadastrado com sucesso!"}), 201
    except sqlite3.IntegrityError as erro:
        return jsonify({"erro": f"Não foi possível cadastrar o cliente: {erro}"}), 400


@app.route("/api/clientes/<int:id_cliente>", methods=["PUT"])
def atualizar_cliente(id_cliente):
    if not cliente_dao.buscar_por_id(id_cliente):
        return jsonify({"erro": "Cliente não encontrado."}), 404
    dados = request.get_json(silent=True) or {}
    nome = str(dados.get("nome", "")).strip()
    email = str(dados.get("email", "")).strip()
    telefone = str(dados.get("telefone", "")).strip() or None
    if not nome or not email:
        return jsonify({"erro": "Nome e e-mail são obrigatórios."}), 400
    try:
        cliente_dao.atualizar(id_cliente, Cliente(id_cliente, nome, email, telefone))
        return jsonify({"mensagem": "Cliente atualizado com sucesso!"})
    except sqlite3.IntegrityError as erro:
        return jsonify({"erro": f"Não foi possível atualizar o cliente: {erro}"}), 400


@app.route("/api/clientes/<int:id_cliente>", methods=["DELETE"])
def remover_cliente(id_cliente):
    try:
        if not cliente_dao.remover(id_cliente):
            return jsonify({"erro": "Cliente não encontrado."}), 404
        return jsonify({"mensagem": "Cliente removido com sucesso!"})
    except sqlite3.IntegrityError:
        return jsonify({"erro": "Este cliente possui pedidos vinculados."}), 400


# PEDIDOS
@app.route("/api/pedidos", methods=["GET"])
def listar_pedidos():
    return jsonify([pedido.to_dict() for pedido in pedido_dao.buscar_todos()])


@app.route("/api/pedidos/<int:id_pedido>", methods=["GET"])
def buscar_pedido(id_pedido):
    pedido = pedido_dao.buscar_por_id(id_pedido)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado."}), 404
    return jsonify(pedido.to_dict())


@app.route("/api/pedidos", methods=["POST"])
def criar_pedido():
    dados = request.get_json(silent=True) or {}
    itens_dados = dados.get("itens", [])
    if not isinstance(itens_dados, list) or not itens_dados:
        return jsonify({"erro": "O pedido deve conter pelo menos um prato."}), 400

    cliente = None
    try:
        if dados.get("id_cliente"):
            cliente = cliente_dao.buscar_por_id(int(dados["id_cliente"]))
        elif isinstance(dados.get("cliente"), dict):
            dados_cliente = dados["cliente"]
            nome = str(dados_cliente.get("nome", "")).strip()
            email = str(dados_cliente.get("email", "")).strip()
            telefone = str(dados_cliente.get("telefone", "")).strip() or None
            if not nome or not email:
                return jsonify({"erro": "Informe o nome e o e-mail do cliente."}), 400
            cliente = cliente_dao.buscar_por_email(email)
            if not cliente:
                id_cliente = cliente_dao.inserir(Cliente(None, nome, email, telefone))
                cliente = cliente_dao.buscar_por_id(id_cliente)

        if not cliente:
            return jsonify({"erro": "Cliente válido não encontrado."}), 400

        pedido = Pedido(None, cliente)
        for item_dados in itens_dados:
            id_prato = int(item_dados.get("id_prato", 0))
            quantidade = int(item_dados.get("quantidade", 1))
            prato = prato_dao.buscar_por_id(id_prato)
            if not prato or not prato.disponivel or quantidade <= 0:
                return jsonify({"erro": "Um dos pratos ou quantidades do pedido é inválido."}), 400
            pedido.adicionar_item(ItemPedido(None, prato, quantidade, prato.preco))

        novo_id = pedido_dao.inserir(pedido)
        pedido_salvo = pedido_dao.buscar_por_id(novo_id)
        return jsonify({"id": novo_id, "pedido": pedido_salvo.to_dict(), "mensagem": "Pedido registrado com sucesso!"}), 201
    except (ValueError, TypeError, sqlite3.IntegrityError) as erro:
        return jsonify({"erro": f"Não foi possível registrar o pedido: {erro}"}), 400


@app.route("/api/pedidos/<int:id_pedido>", methods=["PUT"])
def atualizar_status_pedido(id_pedido):
    dados = request.get_json(silent=True) or {}
    novo_status = str(dados.get("status", "")).upper()
    if novo_status not in Pedido.STATUS:
        return jsonify({"erro": f"Status inválido. Use: {', '.join(Pedido.STATUS)}"}), 400
    if not pedido_dao.atualizar_status(id_pedido, novo_status):
        return jsonify({"erro": "Pedido não encontrado."}), 404
    return jsonify({"mensagem": f"Status atualizado para {novo_status}!"})


@app.route("/api/pedidos/<int:id_pedido>", methods=["DELETE"])
def remover_pedido(id_pedido):
    if not pedido_dao.remover(id_pedido):
        return jsonify({"erro": "Pedido não encontrado."}), 404
    return jsonify({"mensagem": "Pedido excluído com sucesso!"})


# CONTATO
@app.route("/api/contato", methods=["GET"])
def listar_mensagens():
    return jsonify([mensagem.to_dict() for mensagem in contato_dao.buscar_todas()])


@app.route("/api/contato", methods=["POST"])
def enviar_mensagem():
    dados = request.get_json(silent=True) or {}
    nome = str(dados.get("nome", "")).strip()
    email = str(dados.get("email", "")).strip()
    texto = str(dados.get("texto", "")).strip()
    if not nome or not email or len(texto) < 5:
        return jsonify({"erro": "Preencha nome, e-mail e uma mensagem com pelo menos 5 caracteres."}), 400
    mensagem = MensagemContato(None, nome, email, texto)
    novo_id = contato_dao.inserir(mensagem)
    return jsonify({"id": novo_id, "mensagem": "Mensagem enviada com sucesso!"}), 201


@app.route("/api/contato/<int:id_mensagem>", methods=["DELETE"])
def remover_mensagem(id_mensagem):
    if not contato_dao.remover(id_mensagem):
        return jsonify({"erro": "Mensagem não encontrada."}), 404
    return jsonify({"mensagem": "Mensagem removida!"})


@app.route("/", methods=["GET"])
def inicio():
    return jsonify({
        "mensagem": "API do Restaurante Satoshy",
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
    app.run(host="127.0.0.1", port=5000, debug=True)
