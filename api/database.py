"""Conexão do sistema com o banco de dados SQLite."""

import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CAMINHO_BANCO = BASE / "banco" / "satoshy.db"
CAMINHO_SCHEMA = BASE / "banco" / "schema.sql"
CAMINHO_SEED = BASE / "banco" / "seed.sql"


class Conexao:
    """Abre conexões e cria o banco quando necessário."""

    def __init__(self, caminho=CAMINHO_BANCO):
        self.caminho = str(caminho)

    def conectar(self):
        Path(self.caminho).parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(self.caminho)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        con.create_function("casefold", 1, lambda texto: texto.casefold() if texto else "")
        return con

    def criar_banco(self, com_dados=True):
        con = self.conectar()
        try:
            con.executescript(CAMINHO_SCHEMA.read_text(encoding="utf-8"))
            if com_dados:
                con.executescript(CAMINHO_SEED.read_text(encoding="utf-8"))
            con.commit()
        finally:
            con.close()

    def testar(self):
        try:
            con = self.conectar()
            con.execute("SELECT 1")
            con.close()
            return True
        except sqlite3.Error:
            return False
