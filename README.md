# Satoshy Sushi — Projeto Integrado (DWS + POO + BD)

Site de restaurante japonês: front-end (HTML/CSS/JS) + API Flask (Python/POO) + banco de dados SQLite.

## Etapa 1 — Modelagem e criação do banco (entrega 09/11/2026)

| Item exigido | Onde está |
|---|---|
| Diagrama de Classes / UML revisado | `docs/diagrama_classes.png` |
| Modelo das tabelas do BD | `docs/diagrama_banco.png` |
| Estrutura das tabelas criada e funcionando | `banco/schema.sql` + `banco/seed.sql` |
| Conexão inicial do sistema com o banco | `api/database.py`, `api/app.py` |
| Classes (POO) | `api/models.py` |

### Tabelas
`categoria`, `prato`, `cliente`, `pedido`, `item_pedido`, `mensagem_contato`
(o cardápio com 33 pratos / 9 categorias já vem carregado pelo `seed.sql`).

### Como executar
```bash
cd api
python -m pip install -r requirements.txt
python criar_banco.py     # cria banco/satoshy.db com tabelas e cardápio
python app.py             # inicia a API em http://localhost:5000
```
Testes rápidos no navegador:
- `http://localhost:5000/api/status` → `{"banco": "conectado"}`
- `http://localhost:5000/api/pratos` → lista vinda do banco
- `http://localhost:5000/api/pratos?busca=salmão`
- `http://localhost:5000/api/pratos/1`

Depois abra `index.html` com o Live Server: a busca de pratos já usa o banco.

## Próximas etapas
- **Etapa 2 (13/11):** DAOs e rotas Flask completas (cadastro/consulta de clientes, pedidos, contato).
- **Entrega final (17/11):** front-end integrado via Fetch.
