"""Cria o banco satoshy.db com as tabelas e o cardápio inicial.
Uso:  python criar_banco.py
"""
from database import Conexao, CAMINHO_BANCO

if __name__ == "__main__":
    Conexao().criar_banco()
    con = Conexao().conectar()
    for tabela in ("categoria", "prato", "cliente", "pedido", "item_pedido", "mensagem_contato"):
        total = con.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        print(f"{tabela:18} {total} registro(s)")
    con.close()
    print(f"\nBanco criado em: {CAMINHO_BANCO}")
