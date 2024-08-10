-- DimProduto:
CREATE TABLE DimProduto (
    sk_produto SERIAL PRIMARY KEY,
    idproduto INTEGER NOT NULL,
    nome_produto VARCHAR(255) NOT NULL,
    tipo_produto VARCHAR(100) NOT NULL,
    valor_minimo DECIMAL(10, 2) NOT NULL,
    valor_maximo DECIMAL (10, 2) NOT NULL,
    numero_parcelas_maximo INTEGER NOT NULL,
    condicoes_especiais TEXT
);
