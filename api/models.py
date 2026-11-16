CÓDIGO
"""Classes de domínio (POO) do sistema Satoshy Sushi.
Correspondem ao Diagrama de Classes em docs/diagrama_classes.png.
"""
class Categoria:
def __init__(self, id_categoria, nome):
self.id_categoria = id_categoria
self.nome = nome
def to_dict(self):
return {"id": self.id_categoria, "nome": self.nome}
class Prato:
def __init__(self, id_prato, nome, descricao, preco, categoria, disponivel=True):
self.id_prato = id_prato
self.nome = nome
self.descricao = descricao
self.preco = preco
self.categoria = categoria # objeto Categoria
self.disponivel = bool(disponivel)
def to_dict(self):
return {
"id": self.id_prato,
"nome": self.nome,
"categoria": self.categoria.nome if isinstance(self.categoria, Categoria) else
self.categoria,
"id_categoria": self.categoria.id_categoria if isinstance(self.categoria,
Categoria) else None,
"descricao": self.descricao,
"preco": self.preco,
"disponivel": self.disponivel,
}
class Cliente:
def __init__(self, id_cliente, nome, email, telefone=None):
self.id_cliente = id_cliente
self.nome = nome
self.email = email
self.telefone = telefone
def to_dict(self):
return {
"id": self.id_cliente,
"nome": self.nome,
"email": self.email,
"telefone": self.telefone,
}
class ItemPedido:
def __init__(self, id_item, prato, quantidade, preco_unitario):
self.id_item = id_item
self.prato = prato # objeto Prato
self.quantidade = quantidade
self.preco_unitario = preco_unitario
def calcular_subtotal(self):
return round(self.quantidade * self.preco_unitario, 2)
def to_dict(self):
return {
"id": self.id_item,
"id_prato": self.prato.id_prato if isinstance(self.prato, Prato) else self.prato,
"nome_prato": self.prato.nome if isinstance(self.prato, Prato) else None,
"quantidade": self.quantidade,
"preco_unitario": self.preco_unitario,
"subtotal": self.calcular_subtotal(),
}
class Pedido:
STATUS = ("ABERTO", "EM_PREPARO", "ENTREGUE", "CANCELADO")
def __init__(self, id_pedido, cliente, data_hora=None, status="ABERTO",
valor_total=0.0):
self.id_pedido = id_pedido
self.cliente = cliente # objeto Cliente
self.data_hora = data_hora
self.status = status
self.valor_total = valor_total
self.itens = []
def adicionar_item(self, item):
self.itens.append(item)
self.valor_total = self.calcular_total()
def calcular_total(self):
return round(sum(i.calcular_subtotal() for i in self.itens), 2)
def to_dict(self):
total = self.calcular_total() if self.itens else self.valor_total
return {
"id": self.id_pedido,
"cliente": self.cliente.to_dict() if isinstance(self.cliente, Cliente) else {"id":
self.cliente},
"data_hora": self.data_hora,
"status": self.status,
"valor_total": total,
"itens": [i.to_dict() for i in self.itens],
}
class MensagemContato:
def __init__(self, id_mensagem, nome, email, texto, data_envio=None):
self.id_mensagem = id_mensagem
self.nome = nome
self.email = email
self.texto = texto
self.data_envio = data_envio
def to_dict(self):
return {
"id": self.id_mensagem,
"nome": self.nome,
"email": self.email,
"texto": self.texto,
"data_envio": self.data_envio,
}
