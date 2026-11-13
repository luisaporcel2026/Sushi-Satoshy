"""Camada de acesso a dados (Padrão DAO) do sistema Satoshy Sushi."""
from database import Conexao
from models import Categoria, Prato, Cliente, Pedido, ItemPedido, MensagemContato
class CategoriaDAO:
def __init__(self, conexao=None):
self.conexao = conexao or Conexao()
def buscar_todas(self):
con = self.conexao.conectar()
try:
linhas = con.execute(
"SELECT id_categoria, nome FROM categoria ORDER BY id_categoria"
).fetchall()
return [Categoria(l["id_categoria"], l["nome"]) for l in linhas]
finally:
con.close()
class PratoDAO:
def __init__(self, conexao=None):
self.conexao = conexao or Conexao()
def _montar_prato(self, linha):
cat = Categoria(linha["id_categoria"], linha["categoria_nome"])
return Prato(
linha["id_prato"],
linha["nome"],
linha["descricao"],
linha["preco"],
cat,
bool(linha["disponivel"]),
)
def buscar_todos(self, busca=""):
sql = """
SELECT p.id_prato, p.nome, p.descricao, p.preco, p.disponivel,
c.id_categoria, c.nome AS categoria_nome
FROM prato p
JOIN categoria c ON c.id_categoria = p.id_categoria
WHERE p.disponivel = 1
"""
con = self.conexao.conectar()
try:
if busca:
termo = f"%{busca.casefold()}%"
linhas = con.execute(
sql + " AND (casefold(p.nome) LIKE ? OR casefold(c.nome) LIKE ? OR
casefold(p.descricao) LIKE ?)"
" ORDER BY p.id_prato",
(termo, termo, termo),
).fetchall()
else:
linhas = con.execute(sql + " ORDER BY p.id_prato").fetchall()
return [self._montar_prato(l) for l in linhas]
finally:
con.close()
def buscar_por_id(self, id_prato):
sql = """
SELECT p.id_prato, p.nome, p.descricao, p.preco, p.disponivel,
c.id_categoria, c.nome AS categoria_nome
FROM prato p
JOIN categoria c ON c.id_categoria = p.id_categoria
WHERE p.id_prato = ?
"""
con = self.conexao.conectar()
try:
linha = con.execute(sql, (id_prato,)).fetchone()
return self._montar_prato(linha) if linha else None
finally:
con.close()
def inserir(self, prato):
con = self.conexao.conectar()
try:
id_cat = (
prato.categoria.id_categoria
if isinstance(prato.categoria, Categoria)
else prato.categoria
)
cursor = con.execute(
"INSERT INTO prato (nome, descricao, preco, disponivel, id_categoria)
VALUES (?, ?, ?, ?, ?)",
(prato.nome, prato.descricao, prato.preco, int(prato.disponivel), id_cat),
)
con.commit()
return cursor.lastrowid
finally:
con.close()
def atualizar(self, id_prato, prato):
con = self.conexao.conectar()
try:
id_cat = (
prato.categoria.id_categoria
if isinstance(prato.categoria, Categoria)
else prato.categoria
)
cursor = con.execute(
"""UPDATE prato
SET nome = ?, descricao = ?, preco = ?, disponivel = ?, id_categoria = ?
WHERE id_prato = ?""",
(prato.nome, prato.descricao, prato.preco, int(prato.disponivel), id_cat,
id_prato),
)
con.commit()
return cursor.rowcount > 0
finally:
con.close()
def remover(self, id_prato):
con = self.conexao.conectar()
try:
cursor = con.execute("DELETE FROM prato WHERE id_prato = ?", (id_prato,))
con.commit()
return cursor.rowcount > 0
finally:
con.close()
class ClienteDAO:
def __init__(self, conexao=None):
self.conexao = conexao or Conexao()
def buscar_todos(self):
con = self.conexao.conectar()
try:
linhas = con.execute(
"SELECT id_cliente, nome, email, telefone FROM cliente ORDER BY
id_cliente"
).fetchall()
return [Cliente(l["id_cliente"], l["nome"], l["email"], l["telefone"]) for l in linhas]
finally:
con.close()
def buscar_por_id(self, id_cliente):
con = self.conexao.conectar()
try:
l = con.execute(
"SELECT id_cliente, nome, email, telefone FROM cliente WHERE id_cliente =
?",
(id_cliente,),
).fetchone()
return Cliente(l["id_cliente"], l["nome"], l["email"], l["telefone"]) if l else None
finally:
con.close()
def buscar_por_email(self, email):
con = self.conexao.conectar()
try:
l = con.execute(
"SELECT id_cliente, nome, email, telefone FROM cliente WHERE email = ?",
(email,),
).fetchone()
return Cliente(l["id_cliente"], l["nome"], l["email"], l["telefone"]) if l else None
finally:
con.close()
def inserir(self, cliente):
con = self.conexao.conectar()
try:
cursor = con.execute(
"INSERT INTO cliente (nome, email, telefone) VALUES (?, ?, ?)",
(cliente.nome, cliente.email, cliente.telefone),
)
con.commit()
return cursor.lastrowid
finally:
con.close()
def atualizar(self, id_cliente, cliente):
con = self.conexao.conectar()
try:
cursor = con.execute(
"UPDATE cliente SET nome = ?, email = ?, telefone = ? WHERE id_cliente =
?",
(cliente.nome, cliente.email, cliente.telefone, id_cliente),
)
con.commit()
return cursor.rowcount > 0
finally:
con.close()
def remover(self, id_cliente):
con = self.conexao.conectar()
try:
cursor = con.execute("DELETE FROM cliente WHERE id_cliente = ?",
(id_cliente,))
con.commit()
return cursor.rowcount > 0
finally:
con.close()
class PedidoDAO:
def __init__(self, conexao=None):
self.conexao = conexao or Conexao()
def _carregar_itens(self, con, pedido):
linhas_itens = con.execute(
"""SELECT ip.id_item, ip.quantidade, ip.preco_unitario,
p.id_prato, p.nome, p.descricao, p.preco, p.disponivel,
c.id_categoria, c.nome AS categoria_nome
FROM item_pedido ip
JOIN prato p ON p.id_prato = ip.id_prato
JOIN categoria c ON c.id_categoria = p.id_categoria
WHERE ip.id_pedido = ?""",
(pedido.id_pedido,),
).fetchall()
for li in linhas_itens:
cat = Categoria(li["id_categoria"], li["categoria_nome"])
prato = Prato(li["id_prato"], li["nome"], li["descricao"], li["preco"], cat,
li["disponivel"])
item = ItemPedido(li["id_item"], prato, li["quantidade"], li["preco_unitario"])
pedido.adicionar_item(item)
def buscar_todos(self):
con = self.conexao.conectar()
try:
linhas = con.execute(
"""SELECT pe.id_pedido, pe.data_hora, pe.status, pe.valor_total,
cl.id_cliente, cl.nome, cl.email, cl.telefone
FROM pedido pe
JOIN cliente cl ON cl.id_cliente = pe.id_cliente
ORDER BY pe.id_pedido DESC"""
).fetchall()
pedidos = []
for l in linhas:
cliente = Cliente(l["id_cliente"], l["nome"], l["email"], l["telefone"])
pedido = Pedido(l["id_pedido"], cliente, l["data_hora"], l["status"],
l["valor_total"])
self._carregar_itens(con, pedido)
pedidos.append(pedido)
return pedidos
finally:
con.close()
def buscar_por_id(self, id_pedido):
con = self.conexao.conectar()
try:
l = con.execute(
"""SELECT pe.id_pedido, pe.data_hora, pe.status, pe.valor_total,
cl.id_cliente, cl.nome, cl.email, cl.telefone
FROM pedido pe
JOIN cliente cl ON cl.id_cliente = pe.id_cliente
WHERE pe.id_pedido = ?""",
(id_pedido,),
).fetchone()
if not l:
return None
cliente = Cliente(l["id_cliente"], l["nome"], l["email"], l["telefone"])
pedido = Pedido(l["id_pedido"], cliente, l["data_hora"], l["status"],
l["valor_total"])
self._carregar_itens(con, pedido)
return pedido
finally:
con.close()
def inserir(self, pedido):
con = self.conexao.conectar()
try:
total = pedido.calcular_total()
cursor = con.execute(
"INSERT INTO pedido (id_cliente, status, valor_total) VALUES (?, ?, ?)",
(pedido.cliente.id_cliente, pedido.status, total),
)
id_pedido = cursor.lastrowid
for item in pedido.itens:
con.execute(
"""INSERT INTO item_pedido (id_pedido, id_prato, quantidade,
preco_unitario)
VALUES (?, ?, ?, ?)""",
(id_pedido, item.prato.id_prato, item.quantidade, item.preco_unitario),
)
con.commit()
return id_pedido
finally:
con.close()
def atualizar_status(self, id_pedido, novo_status):
con = self.conexao.conectar()
try:
cursor = con.execute(
"UPDATE pedido SET status = ? WHERE id_pedido = ?",
(novo_status, id_pedido),
)
con.commit()
return cursor.rowcount > 0
finally:
con.close()
def remover(self, id_pedido):
con = self.conexao.conectar()
try:
cursor = con.execute("DELETE FROM pedido WHERE id_pedido = ?",
(id_pedido,))
con.commit()
return cursor.rowcount > 0
finally:
con.close()
class MensagemContatoDAO:
def __init__(self, conexao=None):
self.conexao = conexao or Conexao()
def buscar_todas(self):
con = self.conexao.conectar()
try:
linhas = con.execute(
"SELECT id_mensagem, nome, email, texto, data_envio FROM
mensagem_contato ORDER BY id_mensagem DESC"
).fetchall()
return [
MensagemContato(l["id_mensagem"], l["nome"], l["email"], l["texto"],
l["data_envio"])
for l in linhas
]
finally:
con.close()
def inserir(self, mensagem):
con = self.conexao.conectar()
try:
cursor = con.execute(
"INSERT INTO mensagem_contato (nome, email, texto) VALUES (?, ?, ?)",
(mensagem.nome, mensagem.email, mensagem.texto),
)
con.commit()
return cursor.lastrowid
finally:
con.close()
def remover(self, id_mensagem):
con = self.conexao.conectar()
try:
cursor = con.execute("DELETE FROM mensagem_contato WHERE
id_mensagem = ?", (id_mensagem,))
con.commit()
return cursor.rowcount > 0
finally:
con.close()
