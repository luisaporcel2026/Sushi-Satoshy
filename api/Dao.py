"""Camada de acesso a dados (DAO) do sistema Satoshy Sushi."""

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
            return [Categoria(linha["id_categoria"], linha["nome"]) for linha in linhas]
        finally:
            con.close()


class PratoDAO:
    CONSULTA_BASE = """
        SELECT p.id_prato, p.nome, p.descricao, p.preco, p.disponivel,
               c.id_categoria, c.nome AS categoria_nome
        FROM prato p
        JOIN categoria c ON c.id_categoria = p.id_categoria
    """

    def __init__(self, conexao=None):
        self.conexao = conexao or Conexao()

    def _montar_prato(self, linha):
        categoria = Categoria(linha["id_categoria"], linha["categoria_nome"])
        return Prato(
            linha["id_prato"], linha["nome"], linha["descricao"],
            linha["preco"], categoria, linha["disponivel"]
        )

    def buscar_todos(self, busca=""):
        con = self.conexao.conectar()
        try:
            sql = self.CONSULTA_BASE + " WHERE p.disponivel = 1"
            parametros = ()
            if busca:
                termo = f"%{busca.casefold()}%"
                sql += " AND (casefold(p.nome) LIKE ? OR casefold(c.nome) LIKE ? OR casefold(p.descricao) LIKE ?)"
                parametros = (termo, termo, termo)
            sql += " ORDER BY c.id_categoria, p.id_prato"
            linhas = con.execute(sql, parametros).fetchall()
            return [self._montar_prato(linha) for linha in linhas]
        finally:
            con.close()

    def buscar_por_id(self, id_prato):
        con = self.conexao.conectar()
        try:
            linha = con.execute(
                self.CONSULTA_BASE + " WHERE p.id_prato = ?",
                (id_prato,),
            ).fetchone()
            return self._montar_prato(linha) if linha else None
        finally:
            con.close()

    def inserir(self, prato):
        id_categoria = (
            prato.categoria.id_categoria
            if isinstance(prato.categoria, Categoria)
            else prato.categoria
        )
        con = self.conexao.conectar()
        try:
            cursor = con.execute(
                """INSERT INTO prato (nome, descricao, preco, disponivel, id_categoria)
                   VALUES (?, ?, ?, ?, ?)""",
                (prato.nome, prato.descricao, prato.preco, int(prato.disponivel), id_categoria),
            )
            con.commit()
            return cursor.lastrowid
        finally:
            con.close()

    def atualizar(self, id_prato, prato):
        id_categoria = (
            prato.categoria.id_categoria
            if isinstance(prato.categoria, Categoria)
            else prato.categoria
        )
        con = self.conexao.conectar()
        try:
            cursor = con.execute(
                """UPDATE prato
                   SET nome = ?, descricao = ?, preco = ?, disponivel = ?, id_categoria = ?
                   WHERE id_prato = ?""",
                (prato.nome, prato.descricao, prato.preco, int(prato.disponivel), id_categoria, id_prato),
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

    def _montar_cliente(self, linha):
        return Cliente(linha["id_cliente"], linha["nome"], linha["email"], linha["telefone"])

    def buscar_todos(self):
        con = self.conexao.conectar()
        try:
            linhas = con.execute(
                "SELECT id_cliente, nome, email, telefone FROM cliente ORDER BY id_cliente"
            ).fetchall()
            return [self._montar_cliente(linha) for linha in linhas]
        finally:
            con.close()

    def buscar_por_id(self, id_cliente):
        con = self.conexao.conectar()
        try:
            linha = con.execute(
                "SELECT id_cliente, nome, email, telefone FROM cliente WHERE id_cliente = ?",
                (id_cliente,),
            ).fetchone()
            return self._montar_cliente(linha) if linha else None
        finally:
            con.close()

    def buscar_por_email(self, email):
        con = self.conexao.conectar()
        try:
            linha = con.execute(
                "SELECT id_cliente, nome, email, telefone FROM cliente WHERE email = ?",
                (email,),
            ).fetchone()
            return self._montar_cliente(linha) if linha else None
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
                "UPDATE cliente SET nome = ?, email = ?, telefone = ? WHERE id_cliente = ?",
                (cliente.nome, cliente.email, cliente.telefone, id_cliente),
            )
            con.commit()
            return cursor.rowcount > 0
        finally:
            con.close()

    def remover(self, id_cliente):
        con = self.conexao.conectar()
        try:
            cursor = con.execute("DELETE FROM cliente WHERE id_cliente = ?", (id_cliente,))
            con.commit()
            return cursor.rowcount > 0
        finally:
            con.close()


class PedidoDAO:
    def __init__(self, conexao=None):
        self.conexao = conexao or Conexao()

    def _montar_pedido(self, con, linha):
        cliente = Cliente(linha["id_cliente"], linha["nome"], linha["email"], linha["telefone"])
        pedido = Pedido(
            linha["id_pedido"], cliente, linha["data_hora"],
            linha["status"], linha["valor_total"]
        )
        itens = con.execute(
            """SELECT ip.id_item, ip.quantidade, ip.preco_unitario,
                      p.id_prato, p.nome, p.descricao, p.preco, p.disponivel,
                      c.id_categoria, c.nome AS categoria_nome
               FROM item_pedido ip
               JOIN prato p ON p.id_prato = ip.id_prato
               JOIN categoria c ON c.id_categoria = p.id_categoria
               WHERE ip.id_pedido = ? ORDER BY ip.id_item""",
            (pedido.id_pedido,),
        ).fetchall()
        for item in itens:
            categoria = Categoria(item["id_categoria"], item["categoria_nome"])
            prato = Prato(
                item["id_prato"], item["nome"], item["descricao"],
                item["preco"], categoria, item["disponivel"]
            )
            pedido.adicionar_item(
                ItemPedido(item["id_item"], prato, item["quantidade"], item["preco_unitario"])
            )
        return pedido

    def _consulta_pedidos(self):
        return """SELECT pe.id_pedido, pe.data_hora, pe.status, pe.valor_total,
                         cl.id_cliente, cl.nome, cl.email, cl.telefone
                  FROM pedido pe
                  JOIN cliente cl ON cl.id_cliente = pe.id_cliente"""

    def buscar_todos(self):
        con = self.conexao.conectar()
        try:
            linhas = con.execute(self._consulta_pedidos() + " ORDER BY pe.id_pedido DESC").fetchall()
            return [self._montar_pedido(con, linha) for linha in linhas]
        finally:
            con.close()

    def buscar_por_id(self, id_pedido):
        con = self.conexao.conectar()
        try:
            linha = con.execute(
                self._consulta_pedidos() + " WHERE pe.id_pedido = ?",
                (id_pedido,),
            ).fetchone()
            return self._montar_pedido(con, linha) if linha else None
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
                    """INSERT INTO item_pedido
                       (id_pedido, id_prato, quantidade, preco_unitario)
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
            cursor = con.execute("DELETE FROM pedido WHERE id_pedido = ?", (id_pedido,))
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
                """SELECT id_mensagem, nome, email, texto, data_envio
                   FROM mensagem_contato ORDER BY id_mensagem DESC"""
            ).fetchall()
            return [
                MensagemContato(linha["id_mensagem"], linha["nome"], linha["email"], linha["texto"], linha["data_envio"])
                for linha in linhas
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
            cursor = con.execute(
                "DELETE FROM mensagem_contato WHERE id_mensagem = ?",
                (id_mensagem,),
            )
            con.commit()
            return cursor.rowcount > 0
        finally:
            con.close()
