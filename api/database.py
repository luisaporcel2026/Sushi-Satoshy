"""Conexão do sistema com o banco de dados SQLite."""
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CAMINHO_BANCO = BASE / "banco" / "satoshy.db"
CAMINHO_SCHEMA = BASE / "banco" / "schema.sql"
CAMINHO_SEED = BASE / "banco" / "seed.sql"


class Conexao:
    """Responsável por abrir/fechar a conexão e criar o banco."""

    def __init__(self, caminho=CAMINHO_BANCO):
        self.caminho = str(caminho)

    def conectar(self):
        con = sqlite3.connect(self.caminho)
        con.row_factory = sqlite3.Row          # permite acessar colunas pelo nome
        con.execute("PRAGMA foreign_keys = ON")
        # LIKE do SQLite só ignora maiúsculas em ASCII; esta função cobre acentos.
        con.create_function("casefold", 1, lambda t: t.casefold() if t else "")
        return con

    def criar_banco(self, com_dados=True):
        """Executa schema.sql (e seed.sql) para criar as tabelas."""
        con = self.conectar()
        try:
            con.executescript(CAMINHO_SCHEMA.read_text(encoding="utf-8"))
            if com_dados:
                con.executescript(CAMINHO_SEED.read_text(encoding="utf-8"))
            con.commit()
        finally:
            con.close()

    def testar(self):
        """Retorna True se a conexão responde."""
        try:
            con = self.conectar()
            con.execute("SELECT 1")
            con.close()
            return True
        except sqlite3.Error:
            return False
