-- =====================================================
-- Satoshy Sushi - Esquema do banco de dados (SQLite)
-- Etapa 1 - Projeto Integrado DWS + POO + BD
-- =====================================================
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS item_pedido;
DROP TABLE IF EXISTS pedido;
DROP TABLE IF EXISTS mensagem_contato;
DROP TABLE IF EXISTS cliente;
DROP TABLE IF EXISTS prato;
DROP TABLE IF EXISTS categoria;

CREATE TABLE categoria (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT NOT NULL UNIQUE
);

CREATE TABLE prato (
    id_prato     INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT NOT NULL,
    descricao    TEXT NOT NULL,
    preco        REAL NOT NULL CHECK (preco >= 0),
    disponivel   INTEGER NOT NULL DEFAULT 1 CHECK (disponivel IN (0, 1)),
    id_categoria INTEGER NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria)
);

CREATE TABLE cliente (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    telefone   TEXT
);

CREATE TABLE pedido (
    id_pedido   INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente  INTEGER NOT NULL,
    data_hora   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status      TEXT NOT NULL DEFAULT 'ABERTO'
                CHECK (status IN ('ABERTO', 'EM_PREPARO', 'ENTREGUE', 'CANCELADO')),
    valor_total REAL NOT NULL DEFAULT 0 CHECK (valor_total >= 0),
    FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente)
);

CREATE TABLE item_pedido (
    id_item        INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pedido      INTEGER NOT NULL,
    id_prato       INTEGER NOT NULL,
    quantidade     INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario REAL NOT NULL CHECK (preco_unitario >= 0),
    FOREIGN KEY (id_pedido) REFERENCES pedido (id_pedido) ON DELETE CASCADE,
    FOREIGN KEY (id_prato)  REFERENCES prato (id_prato)
);

-- Mensagens enviadas pelo formulário da página "Contato"
CREATE TABLE mensagem_contato (
    id_mensagem INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT NOT NULL,
    email       TEXT NOT NULL,
    texto       TEXT NOT NULL,
    data_envio  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_prato_categoria ON prato (id_categoria);
CREATE INDEX idx_pedido_cliente  ON pedido (id_cliente);
CREATE INDEX idx_item_pedido     ON item_pedido (id_pedido);
