CREATE TABLE produto (
    idproduto SERIAL PRIMARY KEY NOT NULL,
    nome_produto VARCHAR(255) NOT NULL,
    descricao VARCHAR(100),
    tipo_produto VARCHAR(100) NOT NULL,
    valor_minimo DECIMAL(10, 2) NOT NULL,
    valor_maximo DECIMAL(10, 2) NOT NULL,
    numero_parcelas_maximo INTEGER NOT NULL,
    condicoes_especiais TEXT
);