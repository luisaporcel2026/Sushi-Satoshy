# Satoshy Sushi — Restaurante Japonês

Projeto de site com HTML, CSS e JavaScript, integrado a uma API Flask e a um banco de dados SQLite.

## Como abrir o projeto

### 1. Instalar as dependências

Abra o terminal na pasta principal `SATOSHY-SUSHI` e execute:

```bash
python -m pip install -r requirements.txt
```

### 2. Iniciar a API e o banco de dados

No terminal, entre na pasta `api`:

```bash
cd api
python criar_banco.py   # execute na primeira utilização para criar o banco
python app.py
```

Atenção: `criar_banco.py` recria as tabelas e os dados iniciais. Não execute novamente se quiser manter pedidos já registrados.

A API ficará disponível em `http://127.0.0.1:5000`. Mantenha esse terminal aberto enquanto estiver usando o site.

O banco é criado na pasta `banco` e recebe automaticamente os dados iniciais: 33 pratos divididos em 9 categorias. O arquivo do banco não precisa ser criado manualmente.

### 3. Abrir o site

Abra a pasta principal no Visual Studio Code e inicie o **Live Server** pelo arquivo `index.html`. Depois, clique em **Cardápio** no menu do site.

A busca aceita o nome do prato, a categoria ou palavras da descrição. O botão **Mostrar todos** limpa a pesquisa e apresenta o cardápio completo.

## Testar a API

Com o servidor ligado, abra estes endereços no navegador:

- `http://127.0.0.1:5000/api/status` — verifica a conexão com o banco.
- `http://127.0.0.1:5000/api/pratos` — lista os pratos.
- `http://127.0.0.1:5000/api/pratos?busca=salmão` — pesquisa pratos.
- `http://127.0.0.1:5000/api/pedidos` — lista os pedidos registrados.

## Estrutura das pastas

- `index.html` — página inicial.
- `pages/` — cardápio, sobre nós e contato.
- `css/style.css` — estilos do site.
- `js/script.js` — busca do cardápio, carrinho, pedidos e formulário de contato.
- `api/` — API Flask, classes e DAOs.
- `banco/` — esquema e dados iniciais do SQLite.
- `docs/` — diagramas do projeto.

## Importante

O cardápio dinâmico depende da API Flask. Por isso, abrir somente o HTML não é suficiente: inicie `python app.py` antes de usar a página. No GitHub Pages, a API que roda em `localhost` não fica disponível para outras pessoas; a integração local funciona no computador em que o servidor estiver iniciado.
