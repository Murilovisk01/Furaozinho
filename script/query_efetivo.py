
tmp_produto = """DROP TABLE IF EXISTS tmp_produtos;
WITH produtos AS (
	SELECT 
		split_part(estoque, '.000', 1)::NUMERIC(15,2) AS qtd,
		prod_estoque.cod_produto
	FROM prod_estoque
)
	SELECT DISTINCT ON (prod_analise.cod_produto)
		prod_analise.cod_produto
	INTO tmp_produtos
	FROM prod_analise
	JOIN produtos ON produtos.cod_produto = prod_analise.cod_produto 
	WHERE tipo_movimento = '0'
	AND produtos.qtd > 0
	OR prod_analise.data::TIMESTAMP >= now() - INTERVAL '360' DAY
"""

usuario = """INSERT INTO imp_usuario (
  ID,
  Login,
  Apelido,
  Senha)
SELECT distinct on (login)
	cod_usu AS id,
	COALESCE(NULLIF(login, ''), nome) AS login,
	SUBSTRING(nome, 1, 30) AS apelido,
	'123'
FROM funcionarios"""

unidadeNegocio = """INSERT INTO imp_unidadenegocio (ID, Codigo, Nome, CNPJ, estado)
SELECT
	cod_filial AS ID,
	'01' AS codigo,
	razao AS nome,
	cnpj AS CNPJ,
	uf AS estado
FROM filiais"""

grupoRemarcacao = """"""

principioAtivo = """INSERT INTO imp_principioativo (
  ID,
  Nome)
SELECT
	DISTINCT
	SUBSTRING(descr_principio, 1, 100) AS id,
	SUBSTRING(descr_principio, 1, 130) AS nome
FROM produtos
LEFT JOIN imp_principioativo ON imp_principioativo.id = SUBSTRING(produtos.descr_principio, 1, 100)
WHERE descr_principio <> ''
AND imp_principioativo.id IS NULL"""

fabricanteNaoInformado = """--INSERE UM CADASTRO DE FABRICANTE NÃO ENCONTRADO
INSERT INTO Imp_Fabricante(ID,Nome,Tipo) VALUES('0', 'FABRICANTE NÃO INFORMADO', 'J');"""

fabricante = """
--FABRICANTES
INSERT INTO imp_fabricante (
  id,
  nome,
  tipo,
  CNPJ)
SELECT 
	cod_fabricante AS id,
	fabricantes.nome AS nome,
	'J' AS tipo,
	regexp_replace(NULLIF(TRIM(fabricantes.cnpj),''),'[^0-9]', '', 'g') AS cnpj
FROM fabricantes
LEFT JOIN imp_fabricante ON imp_fabricante.id = fabricantes.cod_fabricante
WHERE imp_fabricante.id IS NULL"""

classficacao = """-- Classificacao Raiz.
INSERT INTO imp_classificacao (ID, Nome, Principal, Profundidade, Imp_ClassificacaoPaiID)
  SELECT 'Raiz' AS ID, 'PRINCIPAL' AS Nome, TRUE AS Principal, 0 AS Profundidade, NULL AS classificacaoPaiID;

-- Classificação "Não INFORMADA" para os produtos que possuem um folha tem tronco.
INSERT INTO imp_classificacao (ID, Nome, Principal, Profundidade, Imp_ClassificacaoPaiID) VALUES ('Raiz.NAOINFORMADA', 'NÃO INFORMADA', TRUE, 1, 'Raiz');

INSERT INTO imp_classificacao( 
	id,
	nome,
	profundidade,
	principal,
	imp_classificacaopaiid
)
SELECT
	cod_grupo AS ID,
	descricao AS nome,
	1 AS profundidade,
	TRUE AS principal,
	'Raiz' AS imp_classificacaopaiid
FROM grupos"""

produto = """-- NÃO IDENTIFICADO NA BASE A QUANTIDADE POR EMBALAGEM PARA EMBALAGENS MÃES, SOMENTE TEM A MEDIDA DO PRODUTO DIZENDO SE É UN, CX, ETC...
INSERT INTO imp_produto ( 
  id,
  descricao,
  imp_fabricanteid,
  codigobarras,
  tipoaliquota,
  valoraliquota,
  descontomaximo,
  precoreferencial,
  precovenda,
  listapis,
  tipopreco,
  registroMS,
  codigoNCM,
  imp_principioativoid,
  imp_classificacaoid
)
SELECT 
	produtos.cod_produto AS id,
	produtos.descricao AS descricao,
	COALESCE(imp_fabricante.id, '0') AS imp_fabricanteid,
	ean13_1 AS codigobarras,
	CASE
		WHEN prod_estoque.cst_icms IN ('0', '2','-1') THEN 'D' -- TRIBUTADO
		WHEN prod_estoque.cst_icms IN ('5') THEN 'C' -- NÃO TRIBUTADO
		WHEN prod_estoque.cst_icms IN ('4') THEN 'B' -- ISENTO
		WHEN prod_estoque.cst_icms IN ('9') THEN 'A' -- SUBSTITUIDO
	END AS tipoaliquota,
	prod_estoque.aliquota_icms::NUMERIC(15,2) AS valoraliquota,
	prod_estoque.desconto_max::NUMERIC(15,2) AS descontomaximo,
	prod_estoque.custo::NUMERIC(15,2) AS precoreferencial,
	prod_estoque.preco::NUMERIC(15,2) AS precovenda,
	CASE
		WHEN produtos.cod_lista = '1.000' THEN 'P'
		WHEN produtos.cod_lista = '2.000' THEN 'N'
		WHEN produtos.cod_lista = '3.000' THEN 'U'
		WHEN produtos.cod_lista = '4.000' THEN 'A'
		ELSE 'A' 	
	END AS listapis,
	CASE
		WHEN produtos.tipo_preco = '0' THEN 'M'
		WHEN produtos.tipo_preco = '1' THEN 'L'
		ELSE 'A'
	END AS tipopreco,
	produtos.cod_prod_anvisa AS registroMS,
	produtos.ncm AS codigoNCM,
	imp_principioativo.id AS imp_principioativoid,
	COALESCE(imp_classificacao.id, 'Raiz.NAOINFORMADA') AS imp_classificacaoid
FROM produtos
JOIN tmp_produtos ON tmp_produtos.cod_produto = produtos.cod_produto
JOIN prod_estoque ON prod_estoque.cod_produto = produtos.cod_produto
LEFT JOIN imp_fabricante ON imp_fabricante.id = produtos.cod_fabricante
LEFT JOIN imp_principioativo ON imp_principioativo.id = SUBSTRING(produtos.descr_principio, 1, 100)
LEFT JOIN imp_classificacao ON imp_classificacao.id = prod_estoque.cod_grupo
LEFT JOIN imp_produto ON imp_produto.id = produtos.cod_produto
WHERE imp_produto.id IS NULL"""

produtoMae = """select"""

codigoDeBarrasAdicional = """INSERT INTO imp_codigobarras (
  codigobarras,
  imp_produtoid
)
SELECT 
	produtos.ean13_2 AS codigobarras,
	imp_produto.id AS imp_produtoid
FROM produtos
JOIN imp_produto ON imp_produto.id = produtos.cod_produto
JOIN tmp_produtos ON tmp_produtos.cod_produto = produtos.cod_produto
LEFT JOIN imp_codigobarras ON imp_codigobarras.codigobarras = produtos.ean13_2
LEFT JOIN imp_produto imppro ON imppro.codigobarras = produtos.ean13_2
WHERE imp_codigobarras.codigobarras IS NULL
AND imppro.id IS NULL
AND produtos.ean13_2 IS NOT NULL"""

duploPerfilImcs = """select"""

impostoLucroPresumido = """select"""

impostoSimples = """select"""

fornencedor = """INSERT INTO imp_fornecedor (
  id,
  nome,
  tipo, 
  telefone,
  cnpj,
  inscricaoEstadual,
  estadoInscricaoEstadual
)
SELECT
	cod_fornecedor AS id,
	razao AS nome,
	'J' AS tipo,
	tel_1 AS telefone,
	cnpj_cpf AS cnpj,
	insc_estadual AS inscricaoestadual,
	(CASE
	  WHEN fornecedores.uf IN ('AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP') THEN fornecedores.uf
	  ELSE 'SP'
	END) AS estadoInscricaoEstadual
FROM fornecedores 
LEFT JOIN imp_fornecedor ON imp_fornecedor.id = fornecedores.cod_fornecedor
WHERE imp_fornecedor.id IS NULL;"""

planoPagamento = """-- PARTICULAR
INSERT INTO Imp_PlanoPagamento (ID, Nome, MinParcela, MaxParcela, TipoIntervaloEntrada, IntervaloEntrada, TipoIntervaloParcela, IntervaloParcela) VALUES ('0', '0.PARTICULAR', 1, 1, 'M', 1, 'M', 1);

-- Planos de Pagamento dos Crediários
INSERT INTO Imp_PlanoPagamento (
	ID, 
	Nome, 
	MinParcela, 
	MaxParcela, 
	TipoIntervaloEntrada, 
	IntervaloEntrada, 
	TipoIntervaloParcela, 
	IntervaloParcela
) 
SELECT 
	cod_convenio AS id,
	descricao AS nome,
	1 AS minparcela,
	1 AS maxparcela,
	'M' AS tipointervaloentrada,
	1 AS intervaloentrada,
	'M' AS tipointervaloparcela,
	1 AS intervaloparcela
FROM convenios 


-- Fechamentos dos Planos de Pagamento
INSERT INTO Imp_FechamentoPlanoPagamento ( 
  id,
  imp_planopagamentoid,
  diafechamento,
  diavencimento
)
SELECT
	cod_convenio AS id,
	imp_planopagamento.id AS imp_planopagamentoid,
	dia_vencimento::INT AS diafechamento,
	dia_vencimento::INT AS diavencimento
FROM convenios
JOIN imp_planopagamento ON imp_planopagamento.id = convenios.cod_convenio"""

cadernoDeOferta = """-- CADERNO DE OFERTAS POR PREÇO OFERTA
INSERT INTO IMP_CadernoOferta (ID, Nome) VALUES ('PRECOPROMOCAO', 'PREÇO PROMOÇÃO');
 
-- ITENS DO CADERNO DE OFERTAS POR PREÇO OFERTA
-- INSERE-SE PRIMEIRO QUEM TEM PROMOÇÃO PERMANENTE
INSERT INTO IMP_ItemCadernoOferta ( 
  IMP_CadernoOfertaID,
  IMP_ProdutoID,
  TipoOferta,
  PrecoOferta)
SELECT 
  'PRECOPROMOCAO' AS imp_cadernoofertaid,
  imp_produto.id AS imp_produtoid,
  'P' AS tipooferta,
  prod_estoque.preco_promocao::NUMERIC(15,2) AS PrecoOferta
FROM prod_estoque
JOIN imp_produto ON imp_produto.id = prod_estoque.cod_produto
WHERE preco_promocao::NUMERIC(15,2) > 0
  AND prod_estoque.preco_promocao::NUMERIC(15,2) > 0.01
  AND promo_permanente = 1
ORDER BY 4;
 
-- DEPOIS INSIRE-SE QUEM NÃO TEM PROMOÇÃO PERMANENTE MAS TEM DATA DE VALIDADE EM DIA AINDA
INSERT INTO IMP_ItemCadernoOferta ( 
  IMP_CadernoOfertaID,
  IMP_ProdutoID,
  TipoOferta,
  PrecoOferta)
SELECT 
  'PRECOPROMOCAO' AS imp_cadernoofertaid,
  imp_produto.id AS imp_produtoid,
  'P' AS tipooferta,
  prod_estoque.preco_promocao::NUMERIC(15,2) AS PrecoOferta
FROM prod_estoque
JOIN imp_produto ON imp_produto.id = prod_estoque.cod_produto
WHERE preco_promocao::NUMERIC(15,2) > 0
  AND prod_estoque.preco_promocao::NUMERIC(15,2) > 0.01
  AND promo_permanente = 0
  AND COALESCE(dt_venc_promocao, NOW() + INTERVAL '1' DAY) > NOW()
ORDER BY 4;"""

cadernoDeOfertaQuantidade = """select"""

cadernoDeOfertaLevePague = """select"""

cadernoDeOfertaClassificacao = """select"""

cadernoDeOfertaUnidade = """-- UNIDADES DE NEGÓCIO DO CADERNO DE OFERTAS POR PREÇO OFERTA
INSERT INTO imp_uncadernooferta (
  Imp_CadernoOfertaID,
  Imp_UnidadeNegocioID)
SELECT
  'PRECOPROMOCAO' AS ID,
  imp_unidadenegocio.id AS imp_unidadenegocioid
FROM imp_unidadenegocio;"""

crediario = """--CREDIÁRIO PARTICULAR
INSERT INTO Imp_Crediario (ID, NomeCrediario, LimitePadraoCliente, Imp_PlanoPagamentoID) VALUES ('0', 'PARTICULAR', 0, '0');

--CREDIÁRIOS
INSERT INTO imp_crediario ( 
  ID,
  NomeCrediario,
  LimitePadraoCliente,
  Imp_PlanoPagamentoID,
  TaxaJuros,
  TaxaMulta,
  TaxaConvenio,
  ToleranciaAtraso,
  TipoCrediario,
  Nome,
  Tipo,
  Telefone,
  Telefone2,
  Email,
  Cnpj,
  InscricaoEstadual,
  EstadoInscricaoEstadual,
  STATUS
) 
SELECT
	cod_convenio AS ID,
	descricao AS nomecrediario,
	(SPLIT_PART(limite_credito, '.', 1)||SPLIT_PART(limite_credito, '.', 2)||SPLIT_PART(limite_credito, '.', 3))::NUMERIC(15,2) AS limitepadraocliente,
	imp_planopagamento.id AS imp_planopagamentoid,
	0 AS taxajuros,
	0 AS taxamulta,
	0 AS taxaconvenio,
	0 AS toleranciaatraso,
	'C' AS tipocrediario,
	razao_social AS nome,
	'P' AS tipo,
	tel1 AS telefone,
	tel2 AS telefone2,
	email AS email,
	cnpj AS cnpj,
	insc_estadual AS inscricaoestadual,
	UF AS estadoinscricaoestadual, 
	'A' AS STATUS
FROM convenios
JOIN imp_planopagamento ON imp_planopagamento.id = convenios.cod_convenio;"""

cliente = """-- CLIENTE PADRÃO
INSERT INTO imp_cliente (
  ID,
  Imp_CrediarioID,
  TipoLimite,
  Limite,
  Nome,
  Tipo,
  Telefone,
  Telefone2,
  Email,
  CPF,
  DataNascimento,
  CNPJ,
  InscricaoEstadual,
  DataAberturaCrediario,
  STATUS
) 
SELECT 
	clientes.cod_cliente AS ID,
	COALESCE(imp_crediario.id, '0') AS imp_crediarioid,
	CASE
		WHEN (COALESCE(clientes.limite_credito, '0'))::NUMERIC(15,2) > 0 THEN 'P'
		WHEN (COALESCE(clientes.limite_credito, '0'))::NUMERIC(15,2) = 0 THEN 'C'
		WHEN clientes.limite_credito = '' THEN 'S'
	END AS tipolimite,
	(COALESCE(clientes.limite_credito, '0'))::NUMERIC(15,2) AS limite,
	clientes.nome AS nome,
	CASE
		WHEN clientes.cnpj IS NOT NULL THEN 'J'
		ELSE 'F'
	END AS tipo,
	clientes.tel_1 AS telefone,
	clientes.tel_2 AS telefone2,
	clientes.email AS email,
	clientes.cpf AS cpf,
	dt_nascimento::TIMESTAMP AS datanascimento,
	clientes.cnpj AS cnpj,
	clientes.insc_estadual AS inscricaoestadual,
	dt_admissao::TIMESTAMP AS dataaberturacrediario,
	'A' AS STATUS
FROM clientes
LEFT JOIN imp_crediario ON REPLACE(imp_crediario.id, '.', '') = clientes.cod_convenio
LEFT JOIN imp_cliente ON imp_cliente.id = clientes.cod_cliente
WHERE imp_cliente.id IS NULL;

-- CLIENTES PARTICULAR (NO REGISTRO DE CREDIARIO A RECEBER, VOCÊ NÃO PODE BATER POR NOME OU CPF, APARENTEMENTE O CADASTRO DESSES CLIENTES É SEPARADO DO CADASTRO DE FATO DOS CLIENTES DA TABELA 'clientes')
INSERT INTO Imp_Cliente (
  ID,
  Imp_CrediarioID,
  TipoLimite,
  Limite,
  Nome,
  Tipo,
  CPF
)
SELECT
	cod_contas_receber AS id,
	'0' AS imp_crediarioid,
	'C' AS tipolimite,
	'0' AS limite,
	nome_cli_fun AS nome,
	'F',
	contas_receber.cpf AS cpf
FROM contas_receber
LEFT JOIN imp_cliente ON imp_cliente.id = contas_receber.cod_contas_receber
WHERE cod_convenio IS NULL
AND imp_cliente.id IS NULL;

-- CLIENTES FUNCIONÁRIOS (CREDIARIO FUNCIONARIO)
INSERT INTO Imp_Cliente (
  ID,
  Imp_CrediarioID,
  TipoLimite,
  Limite,
  Nome,
  Tipo,
  Telefone,
  Telefone2,
  Email,
  CPF,
  DataNascimento,
  Identidade,
  Sexo,
  STATUS)
SELECT
	funcionarios.cod_usu||'.fun' AS id,
	imp_crediario.id AS imp_crediarioid,
	'C' AS tipolimite,
	'0' AS limite,
	funcionarios.nome AS nome,
	'F' AS tipo,
	tel1 AS telefone,
	tel2 AS telefone2,
	funcionarios.email AS email,
	funcionarios.cpf AS cpf,
	dt_nasc::TIMESTAMP AS datanascimento,
	funcionarios.rg AS identidade,
	CASE
		WHEN funcionarios.sexo = '0' THEN 'M'
		WHEN funcionarios.sexo = '1' THEN 'F'
		WHEN funcionarios.sexo = '0' THEN 'N'
	END AS sexo,
	'A' AS STATUS
FROM funcionarios 
JOIN imp_crediario ON imp_crediario.id = funcionarios.cod_convenio
LEFT JOIN imp_cliente ON imp_cliente.id = funcionarios.cod_usu||'.conv'
WHERE imp_cliente.id IS NULL;

-- ENDERECOS PADRÃO
INSERT INTO imp_cliente_endereco ( 
  ID,
  imp_clienteID,
  Endereco,
  Numero,
  Complemento,
  CEP,
  Bairro,
  Cidade,
  Estado
)
SELECT
	cod_cliente AS id,
	imp_cliente.id AS imp_clienteid,
	COALESCE(clientes.logradouro, '') AS endereco,
	SUBSTRING(COALESCE(clientes.numero, ''), 1, 6) AS numero,
	SUBSTRING(clientes.comple, 1, 30) AS complemento,
	regexp_replace(clientes.cep, '[^0-9]', '', 'g') AS cep,
	clientes.bairro AS bairro,
	clientes.cidade AS cidade,
	CASE
		WHEN clientes.uf NOT IN ('AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP') THEN NULL
		ELSE clientes.uf
	END AS estado
FROM clientes
JOIN imp_cliente ON imp_cliente.id = clientes.cod_cliente
LEFT JOIN imp_cliente_endereco ON imp_cliente_endereco.id = clientes.cod_cliente
WHERE imp_cliente_endereco IS NULL;

-- ENDERECOS CLIENTES FUNCIONARIOS
INSERT INTO imp_cliente_endereco ( 
  ID,
  imp_clienteID,
  Endereco,
  Numero,
  Complemento,
  CEP,
  Bairro,
  Cidade,
  Estado
)
SELECT
	cod_usu AS id,
	imp_cliente.id AS imp_clienteid,
	COALESCE(logradouro, '') AS endereco,
	COALESCE(funcionarios.numero, '') AS numero,
	comple AS complemento, 
	funcionarios.cep AS cep,
	funcionarios.bairro AS bairro,
	funcionarios.cidade AS cidade,
	uf AS estado
FROM funcionarios
JOIN imp_cliente ON imp_cliente.id = funcionarios.cod_usu||'.fun'
LEFT JOIN imp_cliente_endereco ON imp_cliente_endereco.id = funcionarios.cod_usu
WHERE imp_cliente_endereco.id IS NULL;"""

dependenteCliente = """select"""

planoRemuneracao = """-- PLANO REMUNERAÇÃO
INSERT INTO imp_planoremu (ID, Nome, DataInicial, DataFinal, ConsiderarDevolucao) VALUES ('PLANO DE REMUNERAÇÃO POR COMISSÃO', 'PLANO DE REMUNERAÇÃO POR COMISSÃO', NOW(), NOW() + INTERVAL '1 year', TRUE);

-- ITENS DO PLANO DE REMUNERAÇÃO POR COMISSÃO 
INSERT INTO imp_planoremucomissao (
  Imp_PlanoRemuID,
  Imp_ProdutoID,
  Comissao)
SELECT
  'PLANO DE REMUNERAÇÃO POR COMISSÃO' AS Imp_PlanoRemuID,
  imp_produto.id AS Imp_ProdutoID,
  prod_estoque.comissao::NUMERIC(15,2) AS Comissao
FROM produtos
JOIN prod_estoque ON prod_estoque.cod_produto = produtos.cod_produto
JOIN imp_produto ON imp_produto.id = produtos.cod_produto::VARCHAR
WHERE prod_estoque.comissao::NUMERIC(15,2) > 0;"""

prescritores = """select"""

crediarioReceber = """-- CREDIARIOS RECEBER NORMAIS (CREDIARIOS/CONVENIOS SEM SER O PARTICULAR)
INSERT INTO Imp_CrediarioReceber (
  ID,
  Imp_ClienteID,
  NumeroDocumento,
  DataEmissao,
  DataVencimento,
  Valor,
  Imp_UnidadeNegocioID,
  NumeroParcela,
  TotalParcela
)
SELECT 
	cod_contas_receber AS id,
	imp_cliente.id AS imp_clienteid,
	valor::NUMERIC(15,2) AS numerodocumento,
	dt_lancamento::TIMESTAMP AS dataemissao,
	vencimento::TIMESTAMP AS datavencimento,
	valor::NUMERIC(15,2) AS valor,
	imp_unidadenegocio.id AS imp_unidadenegocioid,
	'1',
	'1'
FROM contas_receber
JOIN imp_crediario ON imp_crediario.id = contas_receber.cod_convenio
JOIN imp_cliente ON imp_cliente.id = contas_receber.cod_cli_fun
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = contas_receber.cod_filial

-- CREDIARIOS RECEBER PARTICULAR
INSERT INTO Imp_CrediarioReceber (
  ID,
  Imp_ClienteID,
  NumeroDocumento,
  DataEmissao,
  DataVencimento,
  Valor,
  Imp_UnidadeNegocioID,
  NumeroParcela,
  TotalParcela
)
SELECT 
	cod_contas_receber AS id,
	imp_cliente.id AS imp_clienteid,
	valor::NUMERIC(15,2) AS numerodocumento,
	dt_lancamento::TIMESTAMP AS dataemissao,
	vencimento::TIMESTAMP AS vencimento,
	valor::NUMERIC(15,2) AS valor,
	imp_unidadenegocio.id AS imp_unidadenegocioid,
	'1' AS numeroparcela,
	'1' AS totalparcela
FROM contas_receber
JOIN imp_cliente ON imp_cliente.id = contas_receber.cod_contas_receber
JOIN imp_crediario ON imp_crediario.id = imp_cliente.imp_crediarioid
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = contas_receber.cod_filial
WHERE cod_convenio IS NULL"""

custo = """INSERT INTO Imp_Custo (
  imp_produtoid,
  imp_unidadenegocioid,
  custo,
  customedio
)
SELECT
	imp_produto.id AS imp_produtoid,
	imp_unidadenegocio.id AS imp_unidadenegocioid,
	prod_estoque.custo::NUMERIC(15,2) AS custo,
	prod_estoque.custo_medio::NUMERIC(15,2) AS customedio
FROM prod_estoque 
JOIN imp_produto ON imp_produto.id = prod_estoque.cod_produto
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = prod_estoque.cod_filial"""

estoque = """INSERT INTO Imp_Estoque (
  imp_produtoid,
  imp_unidadenegocioid,
  estoque
)
WITH produtos AS (
	SELECT 
		split_part(estoque, '.000', 1)::NUMERIC(15,2) AS qtd,
		prod_estoque.cod_produto,
		prod_estoque.cod_filial
	FROM prod_estoque
)
	SELECT
		imp_produto.id AS imp_produtoid,
		imp_unidadenegocio.id AS imp_unidadenegocioid,
		produtos.qtd AS estoque
	FROM produtos 
	JOIN imp_produto ON imp_produto.id = produtos.cod_produto
	JOIN imp_unidadenegocio ON imp_unidadenegocio.id = produtos.cod_filial
	WHERE produtos.qtd > 0"""

contasAPagar = """-- POR ALGUM MOTIVO A FK 'cod_fornecedor' NÃO BATE COM NENHUMA PK DA TABELA 'fornecedores', POR ISSO FOI FEITO POR NOME
INSERT INTO Imp_ContaPagar (
  ID,
  Imp_UnidadeNegocioID,
  Imp_FornecedorID,
  NumeroDocumento,
  DataEmissao,
  DataVencimento,
  ValorDocumento,
  Desconto,
  Multa,
  Observacao,
  NumeroParcela,
  TotalParcela
)
SELECT 
	cod_contas_pagar AS id,
	imp_unidadenegocio.id AS imp_unidadenegocioid,
	imp_fornecedor.id AS imp_fornecedorid,
	documento AS numerodocumento,
	dt_lancamento::TIMESTAMP AS dataemissao,
	dt_vencimento::TIMESTAMP AS dt_vencimento,
	CASE
		WHEN LENGTH(valor_documento) = 9 THEN ((SUBSTRING(REPLACE(valor_documento, '.', ''), 1, 4)||'.00'))::NUMERIC(15,2)
		WHEN LENGTH(valor_documento) = 10 THEN ((SUBSTRING(REPLACE(valor_documento, '.', ''), 1, 5)||'.00'))::NUMERIC(15,2)
		WHEN LENGTH(valor_documento) = 11 THEN ((SUBSTRING(REPLACE(valor_documento, '.', ''), 1, 6)||'.00'))::NUMERIC(15,2)
 		ELSE valor_documento::NUMERIC(15,2)
	END AS valordocumento,
	valor_desconto::NUMERIC(15,2) AS desconto,
	(COALESCE(valor_multa, '0'))::NUMERIC(15,2) AS multa,
	infor_extra AS observacao,
	(SPLIT_PART(num_parcela, '/', 1))::INT AS numeroparcela,
	(SPLIT_PART(num_parcela, '/', 2))::INT AS totalparcela	
FROM contas_pagar
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = contas_pagar.cod_filial
JOIN imp_fornecedor ON imp_fornecedor.nome = contas_pagar.razao_fornecedor
WHERE dt_pagamento IS NULL"""

demanda = """INSERT INTO Imp_HistoricoVenda (
  Imp_ProdutoID,
  Imp_UnidadeNegocioID,
  DATA,
  Quantidade)
SELECT 
	imp_produto.id AS imp_produtoid,
	imp_unidadenegocio.id AS imp_unidadenegocioid,
	prod_analise.data::TIMESTAMP AS DATA,
	SUM(CASE
		WHEN LENGTH(qtd) = 9 THEN ((SUBSTRING(REPLACE(qtd, '.', ''), 1, 4)||'.00'))::NUMERIC(15,2)
		WHEN LENGTH(qtd) = 10 THEN ((SUBSTRING(REPLACE(qtd, '.', ''), 1, 5)||'.00'))::NUMERIC(15,2)
		WHEN LENGTH(qtd) = 11 THEN ((SUBSTRING(REPLACE(qtd, '.', ''), 1, 6)||'.00'))::NUMERIC(15,2)
		ELSE qtd::NUMERIC(15,2)
	END) AS quantidade
FROM prod_analise
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = prod_analise.cod_filial
JOIN imp_produto ON imp_produto.id = prod_analise.cod_produto
WHERE prod_analise.data::TIMESTAMP >= now() - INTERVAL '180' DAY
  AND cod_venda IS NOT NULL
  AND tipo_movimento = 0
  AND motivo = 0
GROUP BY 1, 2, 3"""
