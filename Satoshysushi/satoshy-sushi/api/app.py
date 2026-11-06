from flask import Flask, jsonify, request
from flask_cors import CORS
from database import Conexao, CAMINHO_BANCO

app = Flask(__name__)
CORS(app)  # Libera requisições do front-end em outra origem.

conexao = Conexao()

# Cria o banco automaticamente na primeira execução.
if not CAMINHO_BANCO.exists():
    conexao.criar_banco()

SQL_PRATOS = """
    SELECT p.id_prato AS id, p.nome, c.nome AS categoria, p.descricao, p.preco
    FROM prato p JOIN categoria c ON c.id_categoria = p.id_categoria
    WHERE p.disponivel = 1
"""

@app.route("/api/pratos", methods=["GET"])
def listar_pratos():
    # Busca opcional por nome, categoria ou descrição.
    busca = request.args.get("busca", "").strip()
    con = conexao.conectar()
    try:
        if busca:
            termo = f"%{busca.casefold()}%"
            linhas = con.execute(
                SQL_PRATOS + " AND (casefold(p.nome) LIKE ? OR casefold(c.nome) LIKE ? OR casefold(p.descricao) LIKE ?)"
                " ORDER BY p.id_prato", (termo, termo, termo)).fetchall()
        else:
            linhas = con.execute(SQL_PRATOS + " ORDER BY p.id_prato").fetchall()
    finally:
        con.close()
    return jsonify([dict(l) for l in linhas])

@app.route("/api/pratos/<int:prato_id>", methods=["GET"])
def buscar_prato(prato_id):
    # Consulta um prato pelo ID.
    con = conexao.conectar()
    try:
        linha = con.execute(SQL_PRATOS + " AND p.id_prato = ?", (prato_id,)).fetchone()
    finally:
        con.close()
    if linha is None:
        return jsonify({"erro": "Prato não encontrado"}), 404
    return jsonify(dict(linha))

@app.route("/api/status", methods=["GET"])
def status():
    # Verifica se a API consegue falar com o banco.
    return jsonify({"banco": "conectado" if conexao.testar() else "erro"})

@app.route("/")
def inicio():
    return jsonify({"mensagem": "API do Restaurante Satoshy",
                    "rotas": ["/api/pratos", "/api/pratos?busca=salmão", "/api/pratos/1"]})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
