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
        self.categoria = categoria          # objeto Categoria
        self.disponivel = disponivel

    def to_dict(self):
        # Mantém o mesmo formato JSON que o front-end já consome.
        return {"id": self.id_prato, "nome": self.nome,
                "categoria": self.categoria.nome,
                "descricao": self.descricao, "preco": self.preco}


class Cliente:
    def __init__(self, id_cliente, nome, email, telefone=None):
        self.id_cliente = id_cliente
        self.nome = nome
        self.email = email
        self.telefone = telefone

    def to_dict(self):
        return {"id": self.id_cliente, "nome": self.nome,
                "email": self.email, "telefone": self.telefone}


class ItemPedido:
    def __init__(self, id_item, prato, quantidade, preco_unitario):
        self.id_item = id_item
        self.prato = prato
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario

    def calcular_subtotal(self):
        return self.quantidade * self.preco_unitario


class Pedido:
    STATUS = ("ABERTO", "EM_PREPARO", "ENTREGUE", "CANCELADO")

    def __init__(self, id_pedido, cliente, data_hora=None, status="ABERTO"):
        self.id_pedido = id_pedido
        self.cliente = cliente
        self.data_hora = data_hora
        self.status = status
        self.itens = []

    def adicionar_item(self, item):
        self.itens.append(item)

    def calcular_total(self):
        return sum(i.calcular_subtotal() for i in self.itens)


class MensagemContato:
    def __init__(self, id_mensagem, nome, email, texto, data_envio=None):
        self.id_mensagem = id_mensagem
        self.nome = nome
        self.email = email
        self.texto = texto
        self.data_envio = data_envio
