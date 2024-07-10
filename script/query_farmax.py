
tmp_produto = """DROP TABLE IF EXISTS tmp_produto;
CREATE TABLE tmp_produto (ProdutoID VARCHAR PRIMARY KEY);
INSERT INTO tmp_produto
SELECT
  produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '') AS ID
FROM produtos
WHERE STATUS = 'A'
  AND estoque_1::NUMERIC > 0
  OR dt_ult_venda_1::TIMESTAMP >= now() - INTERVAL '24' MONTH;"""

usuario = """INSERT INTO Imp_Usuario (
  ID,
  Login,
  Senha,
  Apelido)
SELECT
  cd_usuario AS ID,
  login AS Login,
  senha AS Senha,
  TRIM(nome) AS Apelido
FROM usuarios;

INSERT INTO Imp_Usuario (
  ID,
  Login,
  Senha,
  Apelido)
SELECT
  cd_vendedor||'-'||cd_filial AS ID,
  cd_vendedor||'-'||cd_filial AS Login,
  COALESCE(vendedores.senha, '123') AS senha,
  TRIM(nome) AS Apelido
FROM vendedores
LEFT JOIN  Imp_Usuario ON Imp_Usuario.login = vendedores.nome
WHERE STATUS = 'A'
  AND Imp_Usuario.login IS NULL;
"""

unidadeNegocio = """INSERT INTO imp_unidadenegocio (
  ID,
  Codigo,
  Nome,
  NomeFantasia,
  RazaoSocial,
  CNPJ,
  InscricaoEstadual,
  EstadoInscricaoEstadual,
  Endereco,
  Cep,
  Bairro,
  Cidade,
  Estado,
  Telefone,
  Fax)
SELECT
  filiais.cd_filial AS ID,
  LPAD(filiais.cd_filial, 2, '0') AS Codigo,
  UPPER(TRIM(filiais.nome)) AS Nome,
  UPPER(TRIM(filiais.nome)) AS NomeFantasia,
  COALESCE(UPPER(TRIM(filiais.razao)), UPPER(TRIM(filiais.nome))) AS RazaoSocial,
  filiais.cnpj AS CNPJ,
  filiais.inscricao AS InscricaoEstadual,
  filiais.uf AS EstadoInscricaoEstadual,
  TRIM(filiais.rua) AS Endereco,
  filiais.cep AS Cep,
  filiais.bairro AS Bairro,
  COALESCE(filiais.Cidade, 'CIDADE NÃO INFORMADA') AS Cidade,
  TRIM(filiais.uf) AS Estado,
  CASE
    WHEN filiais.fone IS NULL THEN filiais.fone_1
    ELSE filiais.fone END
   AS Telefone, 
  filiais.fax AS Fax
FROM filiais
LEFT JOIN imp_unidadenegocio ON imp_unidadenegocio.id = filiais.cd_filial::VARCHAR
WHERE filiais.status = 'A'
  AND imp_unidadenegocio.id IS NULL;"""

grupoRemarcacao = """INSERT INTO Imp_GrupoRemarcacao (
  ID,
  Nome)
SELECT
  id_familia AS ID,
  TRIM(descricao) AS Nome
FROM familias
LEFT JOIN Imp_GrupoRemarcacao ON Imp_GrupoRemarcacao.ID = familias.id_familia
WHERE Imp_GrupoRemarcacao.ID IS NULL;
"""

principioAtivo = """INSERT INTO Imp_PrincipioAtivo (
  ID,
  Nome)
SELECT
  cd_principio AS ID,
  SUBSTRING(TRIM(descricao), 1 , 130) AS Nome
FROM principio_ativo
LEFT JOIN Imp_PrincipioAtivo ON Imp_PrincipioAtivo.ID = principio_ativo.cd_principio
WHERE Imp_PrincipioAtivo.ID IS NULL
  AND principio_ativo.descricao IS NOT NULL;
  """

fabricanteNaoInformado = """INSERT INTO Imp_Fabricante(ID,Nome,Tipo) VALUES('0', 'FABRICANTE NÃO INFORMADO', 'J');
"""

fabricante = """INSERT INTO Imp_Fabricante(
  ID,
  Nome,
  Tipo,
  Telefone,
  Razaosocial,
  CNPJ)
SELECT
  cd_laboratorio AS ID,
  TRIM(laboratorios.nome) AS Nome,
  'J' AS Tipo,
  SUBSTRING(regexp_replace(NULLIF(TRIM(fone),''),'[^0-9]', '', 'g'), 1, 16) AS Telefone,
  TRIM(razao) AS RazaoSocial,
  regexp_replace(NULLIF(TRIM(laboratorios.cnpj),''),'[^0-9]', '', 'g') AS CNPJ
FROM laboratorios
LEFT JOIN Imp_Fabricante ON Imp_Fabricante.ID = laboratorios.cd_laboratorio
WHERE Imp_Fabricante.ID IS NULL;"""

classficacao = """-- CLASSIFICAÇÃO RAIZ
INSERT INTO Imp_Classificacao (id, nome, profundidade, principal) VALUES ('RAIZ', 'PRINCIPAL', 0, TRUE);

-- PARA PRODUTOS SEM CLASSIFICAÇÃO
INSERT INTO Imp_Classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) VALUES ('RAIZ.NÃOINFORMADA', 'NÃO INFORMADA', 1, TRUE, 'RAIZ');

-- PROFUNDIDADE 1
INSERT INTO Imp_Classificacao (
  id,
  nome,
  profundidade,
  principal,
  imp_classificacaopaiid)
SELECT
  'RAIZ.' || cd_classe AS ID,
  TRIM(descricao) AS Nome,
  1 AS profundiade,
  TRUE AS principal,
  'RAIZ' AS Imp_ClassificacaoPaiID
FROM classes;

-- PROFUNDIDADE 2
INSERT INTO Imp_Classificacao (
  id,
  nome,
  profundidade,
  principal,
  imp_classificacaopaiid)
SELECT DISTINCT
  Imp_Classificacao.ID || '.' || grupos.cd_grupo AS ID,
  TRIM(grupos.descricao) AS Nome,
  2 AS profundiade,
  TRUE AS principal,
  Imp_Classificacao.ID AS Imp_ClassificacaoPaiID
FROM produtos
JOIN grupos ON grupos.cd_grupo = produtos.cd_grupo
JOIN classes ON classes.cd_classe = produtos.cd_classe
JOIN Imp_Classificacao ON Imp_Classificacao.ID = 'RAIZ.'||classes.cd_classe;

-- PROFUNDIDADE 3
INSERT INTO Imp_Classificacao (
  id,
  nome,
  profundidade,
  principal,
  imp_classificacaopaiid)
SELECT DISTINCT
  Imp_Classificacao.ID || '.' || subgrupos.cd_subgrupo AS ID,
  TRIM(subgrupos.descricao) AS Nome,
  3 AS profundiade,
  TRUE AS principal,
  Imp_Classificacao.ID AS Imp_ClassificacaoPaiID
FROM subgrupos
JOIN produtos ON produtos.cd_subgrupo = subgrupos.cd_subgrupo
JOIN Imp_Classificacao ON Imp_Classificacao.ID = 'RAIZ.' || produtos.cd_grupo;"""

produto = """INSERT INTO Imp_Produto(
  ID,
  Descricao,
  Imp_FabricanteID,
  CodigoBarras,
  TipoAliquota,
  ValorAliquota,
  CestID,
  PerfilPISSnID,
  PerfilCofinsSnID,
  PerfilPISID,
  PerfilCofinsID,
  DescontoMaximo,
  PrecoReferencial,
  PrecoVenda,
  ListaPIS,
  TipoPreco,
  RegistroMS,
  CodigoNCM,
  Imp_GrupoRemarcacaoID,
  Imp_PrincipioAtivoID,
  Imp_ClassificacaoID,
  Tipo,
  DataHoraInclusao)
SELECT DISTINCT ON (TRIM(LEADING '0' FROM codigo_barras_1))
  produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '') AS ID,
  TRIM(produtos.descricao) AS Descricao,
  COALESCE(Imp_Fabricante.ID, '0') AS Imp_FabricanteID,
  TRIM(LEADING '0' FROM codigo_barras_1) AS codigobarras,
  (CASE
    WHEN icms = '0' THEN 'A'
    WHEN icms = 'II' THEN 'B'
    WHEN icms = '18' THEN 'D'
    WHEN icms = '20' THEN 'D'
    ELSE 'A'
  END) AS TipoAliquota,
  (CASE
    WHEN icms NOT IN ('0', 'II', 'FF','NN') THEN icms::NUMERIC
  END) AS ValorAliquota,
  imp_cest.id AS cestid,
  perfilpissn.id AS PerfilPISSnID,
  perfilcofinssn.id AS PerfilCofinsSnID,
  perfilpis.id AS PerfilPISID,
  perfilcofins.id AS PerfilCofinsID,
  tx_desconto::NUMERIC(15,2) AS DescontoMaximo,
  custo_unitario::NUMERIC(15,2) AS PrecoReferencial,
  preco_venda::NUMERIC(15,2) AS PrecoVenda,
  (CASE
    WHEN lista_marcacao.descricao ILIKE '%POSITIVA%' THEN 'P'
    WHEN lista_marcacao.descricao ILIKE '%NEGATIVA%' THEN 'N'
    WHEN lista_marcacao.descricao ILIKE '%NEUTRO%' THEN 'U'
    ELSE 'A'
  END) AS ListaPIS,
  (CASE
    WHEN identificador = 'M' THEN 'M'
    WHEN identificador = 'L' THEN 'L'
    ELSE 'L'
  END) AS TipoPreco,
  TRIM(produtos.registroms) AS RegistroMS,
  SUBSTRING(TRIM(produtos.ncm), 1, 8) AS CodigoNCM,
  Imp_GrupoRemarcacao.ID AS Imp_GrupoRemarcacaoID,
  Imp_PrincipioAtivo.ID AS Imp_PrincipioAtivoID,
  COALESCE(Imp_Classificacao.ID, 'RAIZ.NÃOINFORMADA') AS Imp_ClassificacaoID,
  'M' AS Tipo,
  produtos.dt_cadastro::TIMESTAMP AS DataHoraInclusao
FROM produtos
JOIN tmp_produto ON tmp_produto.produtoid = produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '')
LEFT JOIN Imp_Fabricante ON Imp_Fabricante.ID = produtos.cd_laboratorio
LEFT JOIN lista_marcacao ON lista_marcacao.cd_lista = produtos.cd_lista
LEFT JOIN produtos_fisco ON produtos_fisco.id_produto = produtos.cd_produto 
LEFT JOIN Imp_GrupoRemarcacao ON Imp_GrupoRemarcacao.ID = produtos.id_familia
LEFT JOIN Imp_PrincipioAtivo ON Imp_PrincipioAtivo.ID = produtos.cd_principio
LEFT JOIN Imp_Classificacao ON Imp_Classificacao.ID = 'RAIZ.' || produtos.cd_grupo || '.' || produtos.cd_subgrupo
LEFT JOIN imp_cest ON TRIM(imp_cest.codigo) = TRIM(produtos.cest)
LEFT JOIN perfilpis perfilpissn ON perfilpissn.piscst = produtos_fisco.cst_pis_cofins_saida AND perfilpissn.tipocontribuinte = 'B'
LEFT JOIN perfilcofins perfilcofinssn ON perfilcofinssn.cofinscst = produtos_fisco.cst_pis_cofins_saida AND perfilcofinssn.tipocontribuinte = 'B'
LEFT JOIN perfilpis ON perfilpis.piscst = produtos_fisco.cst_pis_cofins_saida AND perfilpis.tipocontribuinte = 'A'
LEFT JOIN perfilcofins ON perfilcofins.cofinscst = produtos_fisco.cst_pis_cofins_saida AND perfilcofins.tipocontribuinte = 'A'
LEFT JOIN Imp_Produto ON Imp_Produto.ID = produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '')
WHERE Imp_Produto.ID IS NULL;
"""

produtoMae = """INSERT INTO Imp_Produto(
  ID,
  Descricao,
  Apresentacao,
  Imp_FabricanteID,
  TipoAliquota,
  ValorAliquota,
  DescontoMaximo,
  PrecoReferencial,
  PrecoVenda,
  ListaPIS,
  TipoPreco,
  RegistroMS,
  CodigoNCM,
  Imp_GrupoRemarcacaoID,
  Imp_PrincipioAtivoID,
  Imp_ClassificacaoID,
  Tipo,
  IDProdutoContido,
  QuantidadeEmbalagem,
  DataHoraInclusao)
SELECT
  '-' || Imp_Produto.ID AS ID,
  Imp_Produto.Descricao AS Descricao,
  'CX C/ ' || produtos.qt_embalagem AS apresentacao,
  Imp_Produto.Imp_FabricanteID AS Imp_FabricanteID,
  Imp_Produto.TipoAliquota AS TipoAliquota,
  Imp_Produto.ValorAliquota AS ValorAliquota,
  Imp_Produto.DescontoMaximo * produtos.qt_embalagem::NUMERIC(15,2) AS DescontoMaximo,
  Imp_Produto.PrecoReferencial * produtos.qt_embalagem::NUMERIC(15,2) AS PrecoReferencial,
  Imp_Produto.PrecoVenda * produtos.qt_embalagem::NUMERIC(15,2) AS PrecoVenda,
  Imp_Produto.ListaPIS AS ListaPIS,
  Imp_Produto.TipoPreco AS TipoPreco,
  Imp_Produto.RegistroMS AS RegistroMS,
  Imp_Produto.CodigoNCM AS CodigoNCM,
  Imp_Produto.Imp_GrupoRemarcacaoID AS Imp_GrupoRemarcacaoID,
  Imp_Produto.Imp_PrincipioAtivoID AS Imp_PrincipioAtivoID,
  Imp_Produto.Imp_ClassificacaoID AS Imp_ClassificacaoID,
  Imp_Produto.Tipo AS Tipo,
  Imp_Produto.ID AS IDProdutoContido,
  produtos.qt_embalagem::NUMERIC(15,2) AS QuantidadeEmbalagem,
  Imp_Produto.DataHoraInclusao AS DataHoraInclusao
FROM produtos
JOIN Imp_Produto ON Imp_Produto.ID = produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '')
LEFT JOIN Imp_Produto imp_prod ON imp_prod.id = '-' || Imp_Produto.ID
WHERE produtos.qt_embalagem::NUMERIC(15,2) > 1
  AND imp_prod.id IS NULL;
  """

codigoDeBarrasAdicional = """INSERT INTO imp_codigobarras(
  codigobarras,
  imp_produtoid)
SELECT DISTINCT ON (regexp_replace(ltrim(codigo_barras_2, '0'), '[^0-9]','','g'))
  regexp_replace(ltrim(codigo_barras_2, '0'), '[^0-9]','','g') AS codigobarras,
  imp_produto.id AS imp_produtoid
FROM produtos
JOIN imp_produto ON imp_produto.id = produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '')
LEFT JOIN imp_codigobarras ON imp_codigobarras.codigobarras = regexp_replace(ltrim(codigo_barras_2, '0'), '[^0-9]','','g')
WHERE regexp_replace(ltrim(codigo_barras_2, '0'), '[^0-9]','','g') <> ltrim(imp_produto.codigobarras, '0')
  AND imp_codigobarras.codigobarras IS NULL;
  """

duploPerfilImcs = """-- Produtos cadastrados com CSOSN
INSERT INTO imp_icmsproduto(
  imp_produtoid,
  perfilicmssnid,
  perfilicmsid,
  estado)
WITH icmsproduto AS (
SELECT DISTINCT
  imp_produto.id AS imp_produtoid,
  perfilsimples.id AS perfilicmssnid,
  perfillucro.id AS perfilicmsid,
  imp_unidadenegocio.estado AS estado
FROM imp_produto
JOIN produtos ON produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '') = imp_produto.id
LEFT JOIN produtos_fisco ON produtos_fisco.id_produto = produtos.cd_produto
LEFT JOIN perfilicms perfilsimples ON perfilsimples.icmssncso = produtos.csosn
LEFT JOIN perfilicms perfillucro ON perfillucro.icmscst = produtos_fisco.cst_icms,
imp_unidadenegocio
)
SELECT DISTINCT ON (icmsproduto.imp_produtoid, icmsproduto.estado)
  icmsproduto.*
FROM icmsproduto
LEFT JOIN imp_icmsproduto ON imp_icmsproduto.imp_produtoid = icmsproduto.imp_produtoid AND imp_icmsproduto.estado = icmsproduto.estado
WHERE imp_icmsproduto.imp_produtoid IS NULL
  AND (icmsproduto.perfilicmssnid IS NOT NULL
  OR icmsproduto.perfilicmsid IS NOT NULL);
  """

impostoLucroPresumido = """INSERT INTO imp_icmsproduto(
  imp_produtoid,
  perfilicmsid,
  estado)
WITH icmsproduto AS (
SELECT DISTINCT
  imp_produto.id AS imp_produtoid,
  perfilicms.id AS perfilicmsid,
  imp_unidadenegocio.estado AS estado
FROM perfilicms
JOIN produtos_fisco ON produtos_fisco.cst_icms = perfilicms.icmscst
JOIN produtos ON produtos.cd_produto = produtos_fisco.id_produto
JOIN imp_produto ON imp_produto.id = produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), ''), imp_unidadenegocio
)
SELECT DISTINCT ON (icmsproduto.imp_produtoid, icmsproduto.estado)
  icmsproduto.*
FROM icmsproduto
LEFT JOIN imp_icmsproduto ON imp_icmsproduto.imp_produtoid = icmsproduto.imp_produtoid AND imp_icmsproduto.estado = icmsproduto.estado
WHERE imp_icmsproduto.imp_produtoid IS NULL;"""

impostoSimples = """-- Produtos cadastrados com CSOSN
INSERT INTO imp_icmsproduto(
  imp_produtoid,
  perfilicmssnid,
  estado)
WITH icmsproduto AS (
SELECT DISTINCT
  imp_produto.id AS imp_produtoid,
  perfilicms.id AS perfilicmssnid,
  imp_unidadenegocio.estado AS estado
FROM perfilicms
JOIN produtos ON produtos.csosn = perfilicms.icmssncso
JOIN imp_produto ON imp_produto.id = produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), ''), imp_unidadenegocio
)
SELECT DISTINCT ON (icmsproduto.imp_produtoid, icmsproduto.estado)
  icmsproduto.*
FROM icmsproduto
LEFT JOIN imp_icmsproduto ON imp_icmsproduto.imp_produtoid = icmsproduto.imp_produtoid AND imp_icmsproduto.estado = icmsproduto.estado
WHERE imp_icmsproduto.imp_produtoid IS NULL;"""

fornencedor = """
INSERT INTO Imp_Fornecedor(
  ID,
  Nome,
  Tipo,
  Telefone,
  Telefone2,
  Fax,
  Site,
  Email,
  CNPJ,
  RazaoSocial,
  InscricaoEstadual,
  Observacao)
SELECT
  cd_distribuidor AS ID,
  TRIM(distribuidores.nome) AS Nome,
  'J' AS Tipo,
  TRIM(fone) AS Telefone,
  TRIM(fone_comercial) AS Telefone2,
  TRIM(distribuidores.fax) AS Fax,
  TRIM(distribuidores.homepage) AS Site,
  TRIM(distribuidores.email) AS Email,
  regexp_replace(NULLIF(TRIM(distribuidores.cnpj),''),'[^0-9]', '', 'g') AS CNPJ,
  TRIM(distribuidores.razao) AS RazaoSocial,
  regexp_replace(NULLIF(TRIM(distribuidores.ie),''),'[^0-9]', '', 'g') AS InscricaoEstadual,
  TRIM(obs_geral) AS Observacao
FROM distribuidores
LEFT JOIN Imp_Fornecedor ON Imp_Fornecedor.ID = distribuidores.cd_distribuidor
WHERE Imp_Fornecedor.ID IS NULL;

INSERT INTO imp_fornecedor_endereco(
  ID,
  Imp_Fornecedorid,
  Endereco,
  Numero,
  Cep,
  Bairro,
  Cidade,
  Estado,
  Complemento)
SELECT
  cd_distribuidor AS ID,
  Imp_Fornecedor.ID AS Imp_Fornecedorid,
  TRIM(distribuidores.endereco) AS Endereco,
  SUBSTRING(COALESCE(TRIM(distribuidores.numero), 'N/I'), 1, 6) AS Numero,
  TRIM(regexp_replace(distribuidores.cep,'[^0-9]','','g')) AS Cep,
  COALESCE(TRIM(distribuidores.bairro), 'BAIRRO NÃO INFORMADO') AS Bairro,
  COALESCE(TRIM(distribuidores.cidade), 'CIDADE NÃO INFORMADA') AS Cidade,
  TRIM(distribuidores.uf) AS Estado,
  SUBSTRING(TRIM(distribuidores.complemento), 1, 30) AS Complemento
FROM distribuidores
JOIN Imp_Fornecedor ON Imp_Fornecedor.ID = distribuidores.cd_distribuidor
LEFT JOIN imp_fornecedor_endereco ON imp_fornecedor_endereco.ID = distribuidores.cd_distribuidor
WHERE TRIM(distribuidores.endereco) IS NOT NULL
AND imp_fornecedor_endereco.ID IS NULL;
"""

planoPagamento = """-- PARTICULAR
INSERT INTO Imp_PlanoPagamento (ID, Nome, MinParcela, MaxParcela, TipoIntervaloEntrada, IntervaloEntrada, TipoIntervaloParcela, IntervaloParcela) VALUES ('0', '0.PARTICULAR', 1, 1, 'M', 1, 'M', 1);
 
--PLANO PAGAMENTO
INSERT INTO Imp_PlanoPagamento(
  ID,
  Nome,
  MinParcela,
  MaxParcela,
  IntervaloEntrada,
  IntervaloParcela)
SELECT
  cd_convenio AS ID,
  TRIM(nome) AS Nome,
  1 AS MinParcela,
  1 AS MaxParcela,
  0 AS IntervaloEntrada,
  1 AS IntervaloParcela
FROM convenios;
 
--FECHAMENTO DO PLANO PAGAMENTO
INSERT INTO Imp_FechamentoPlanoPagamento (
  ID,
  Imp_PlanoPagamentoID,
  DiaFechamento,
  DiaVencimento)
SELECT
  cd_convenio AS ID,
  Imp_PlanoPagamento.ID AS Imp_PlanoPagamentoID,
  dt_fechamento::INT AS DiaFechamento,
  COALESCE(dt_vencimento, dt_fechamento)::INT AS DiaVencimento
FROM convenios
JOIN Imp_PlanoPagamento ON Imp_PlanoPagamento.ID = convenios.cd_convenio
WHERE dt_fechamento IS NOT NULL;
"""

cadernoDeOferta = """INSERT INTO Imp_CadernoOferta(ID, Nome, DataHoraInicial, DataHoraFinal) VALUES ('OFERTAS LOJA 01', 'OFERTAS LOJA 01', NOW(), NOW() + interval '1 year');

--ITENS DOS CADERNOS DE OFERTA DO TIPO PREÇO
INSERT INTO Imp_ItemCadernoOferta(
  Imp_CadernoOfertaID,
  Imp_ProdutoID,
  TipoOferta,
  precooferta)
SELECT DISTINCT
  Imp_CadernoOferta.ID AS Imp_CadernoOfertaID,
  Imp_Produto.ID AS Imp_ProdutoID,
  'P' AS TipoOferta,
  preco_promocao::NUMERIC(15,2) AS PrecoOferta
FROM produtos 
JOIN Imp_Produto ON Imp_Produto.id = produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '')
JOIN Imp_UnidadeNegocio ON Imp_UnidadeNegocio.id = '1'
JOIN Imp_CadernoOferta ON Imp_CadernoOferta.ID = 'OFERTAS LOJA '||Imp_UnidadeNegocio.codigo||''
WHERE preco_promocao::NUMERIC > 0
  AND dt_vencimento_promocao::TIMESTAMP > CURRENT_DATE;
"""

cadernoDeOfertaQuantidade = """
INSERT INTO imp_cadernooferta (id, nome) VALUES ('QTD PRECO TOTAL', 'QTD PRECO TOTAL');

-- ITENS DE CADERNO DE OFERTAS
INSERT INTO imp_itemcadernoofertaquantidade (
  Imp_CadernoOfertaID, 
  Imp_ProdutoID,
  Quantidade, 
  precototal, 
  DescontoPorQtdVendaAcimaQtd, 
  DescontoPorQtdTipo)
SELECT
  imp_cadernooferta.id AS Imp_CadernoOfertaID,
  imp_produto.id AS Imp_ProdutoID,
  produtos_preco_quantidade.quantidadeinicial::INTEGER AS quantidade,
  (produtos_preco_quantidade.quantidadeinicial::NUMERIC * produtos_preco_quantidade.preco_venda::NUMERIC) AS precototal,
  'B'::VARCHAR AS DescontoPorQtdVendaAcimaQtd,
  'C'::VARCHAR AS DescontoPorQtdTipo
FROM produtos_preco_quantidade
JOIN produtos ON TRIM(LEADING '0' FROM produtos.cd_produto) = produtos_preco_quantidade.id_produto
JOIN Imp_Produto ON Imp_Produto.id = produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '')
JOIN imp_cadernooferta ON imp_cadernooferta.id = 'QTD PRECO TOTAL'
WHERE produtos_preco_quantidade.preco_venda > '0'
"""

cadernoDeOfertaLevePague = """select"""

cadernoDeOfertaClassificacao = """-- CADERNO DE OFERTAS CLASSIFICACAO
INSERT INTO imp_cadernooferta (id, nome) VALUES ('PORCENT.CLASSIF.PRECO', 'PORCENT.CLASSIF.PRECO');

-- Itens por Classificação (Grupos)
INSERT INTO imp_itemcadernooferta (
  imp_cadernoofertaid,
  IMP_ClassificacaoID,
  tipooferta,
  descontooferta)
SELECT DISTINCT ON (Imp_Classificacao.nome)
  imp_cadernooferta.ID AS imp_cadernoofertaid,
  Imp_Classificacao.ID AS ClassificacaoID,
  'D' AS tipooferta,
  grupos.tx_desconto::numeric AS descontooferta
FROM grupos
JOIN imp_cadernooferta ON imp_cadernooferta.ID = 'PORCENT.CLASSIF.PRECO'
JOIN produtos ON produtos.cd_grupo = grupos.cd_grupo
JOIN subgrupos ON subgrupos.cd_subgrupo = produtos.cd_subgrupo
JOIN Imp_Classificacao ON Imp_Classificacao.ID = 'RAIZ.'||subgrupos.cd_subgrupo||'.'||grupos.cd_grupo::VARCHAR
WHERE grupos.tx_desconto > '0';
"""

cadernoDeOfertaUnidade = """select"""

crediario = """--CREDIÁRIO PARTICULAR
INSERT INTO Imp_Crediario (ID, NomeCrediario, LimitePadraoCliente, Imp_PlanoPagamentoID) VALUES ('0', 'PARTICULAR', 0, '0');


--CREDIÁRIOS
INSERT INTO Imp_Crediario (
  ID,
  NomeCrediario,
  LimitePadraoCliente,
  MensagemVenda,
  Imp_PlanoPagamentoID,
  TipoCrediario,
  Nome,
  Tipo,
  Telefone,
  Fax,
  Email,
  CNPJ,
  InscricaoEstadual)
SELECT
  cd_convenio AS ID,
  TRIM(convenios.nome) AS NomeCrediario,
  COALESCE(SUBSTRING(limite_credito, 1, 10), '0')::NUMERIC AS LimitePadraoCliente,
  TRIM(obs_geral) AS MensagemVenda,
  Imp_PlanoPagamento.ID AS Imp_PlanoPagamentoID,
  'C' AS TipoCrediario,
  TRIM(convenios.nome) AS Nome,
  'J' AS Tipo,
  regexp_replace(NULLIF(TRIM(fone),''),'[^0-9]', '', 'g') AS Telefone,
  regexp_replace(NULLIF(TRIM(fax),''),'[^0-9]', '', 'g') AS Fax,
  TRIM(SUBSTRING(email, 1,50)) AS Email,
  regexp_replace(NULLIF(TRIM(cnpj),''),'[^0-9]', '', 'g') AS CNPJ,
  regexp_replace(NULLIF(TRIM(ie),''),'[^0-9]', '', 'g') AS InscricaoEstadual
FROM convenios
JOIN Imp_PlanoPagamento ON Imp_PlanoPagamento.ID = convenios.cd_convenio;
"""

cliente = """
INSERT INTO Imp_Cliente (
  ID,
  Imp_CrediarioID,
  NumeroCartao,
  DataAberturaCrediario,
  TipoLimite,
  Limite,
  Nome,
  Tipo,
  Observacao,
  Telefone,
  Telefone2,
  Email,
  CPF,
  DataNascimento,
  Identidade,
  Sexo,
  Profissao,
  Conjuge,
  FiliacaoMae,
  EstadoCivil,
  Cnpj,
  STATUS)
SELECT
  cd_cliente AS ID,
  COALESCE(imp_crediario.ID, '0') AS Imp_CrediarioID,
  cartaofidelidade AS NumeroCartao,
  data_ficha::TIMESTAMP AS DataAberturaCrediario,
  (CASE
    WHEN limite_credito::NUMERIC > 0 THEN 'P'
    ELSE 'C'
  END) AS TipoLimite,
  COALESCE(SUBSTRING(limite_credito, 1, 10), '0')::NUMERIC AS Limite,
  COALESCE(UPPER(REPLACE(TRIM(SUBSTRING(clientes.nome, 1,50)),'''','')), 'NOME NÃO INFORMADO') AS Nome,
  (CASE
    WHEN TRIM(clientes.cpf) IS NOT NULL AND TRIM(clientes.cnpj) IS NULL THEN 'F'
    WHEN TRIM(clientes.cpf) IS NULL AND TRIM(clientes.cnpj) IS NOT NULL THEN 'J'
    ELSE 'F'
  END) AS Tipo,
  TRIM(observacao_geral) AS Observacao,
  regexp_replace(NULLIF(TRIM(clientes.fone),''),'[^0-9]', '', 'g') AS Telefone,
  regexp_replace(NULLIF(TRIM(clientes.fone_comercial),''),'[^0-9]', '', 'g') AS Telefone2,
  TRIM(clientes.email) AS Email,
  SUBSTRING(regexp_replace(NULLIF(TRIM(clientes.cpf),''),'[^0-9]', '', 'g'), 1,11) AS CPF,
  dt_nascimento::TIMESTAMP AS DataNascimento,
  regexp_replace(NULLIF(TRIM(rg),''),'[^0-9]', '', 'g') AS Identidade,
  (CASE
    WHEN clientes.sexo = 'M' THEN 'M'
    WHEN clientes.sexo = 'F' THEN 'F'
  END) AS Sexo,
  TRIM(funcao) AS Profissao,
  TRIM(clientes.conjuge) AS Conjuge,
  TRIM(nome_mae) AS FiliacaoMae,
  (CASE
    WHEN clientes.estado_civil = 'C' THEN 'C'
    WHEN clientes.estado_civil = 'S' THEN 'S'
    ELSE 'N'
  END) AS EstadoCivil,
  regexp_replace(NULLIF(TRIM(clientes.cnpj),''),'[^0-9]', '', 'g') AS CNPJ,
  (CASE
    WHEN clientes.status = 'A' THEN 'A'
    WHEN clientes.status = 'I' THEN 'I'
    ELSE 'A'
  END) AS STATUS
FROM clientes
LEFT JOIN imp_crediario ON imp_crediario.ID = clientes.cd_convenio
LEFT JOIN Imp_Cliente ON Imp_Cliente.ID = clientes.cd_cliente
WHERE Imp_Cliente.ID IS NULL;

INSERT INTO Imp_Cliente_Endereco (
  ID,
  Imp_ClienteID,
  Endereco,
  Numero,
  Complemento,
  Cep,
  Bairro,
  Cidade,
  Estado)
SELECT
  clientes.cd_cliente AS ID,
  Imp_Cliente.ID AS Imp_ClienteID,
  TRIM(clientes.endereco) AS Endereco,
  SUBSTRING(COALESCE(TRIM(clientes.numero), 'N/I'),1,6) AS Numero,
  SUBSTRING(TRIM(clientes.complemento),1, 30) AS Complemento,
  TRIM(regexp_replace(clientes.cep,'[^0-9]','','g')) AS Cep,
  COALESCE(TRIM(clientes.bairro), 'BAIRRO NÃO INFORMADO') AS Bairro,
  COALESCE(TRIM(clientes.cidade), 'CIDADE NÃO INFORMADA') AS Cidade,
  TRIM(clientes.uf) AS Estado
FROM clientes
JOIN Imp_Cliente ON Imp_Cliente.ID = clientes.cd_cliente
LEFT JOIN Imp_Cliente_Endereco ON Imp_Cliente_Endereco.ID = clientes.cd_cliente
WHERE TRIM(clientes.endereco) IS NOT NULL
  AND Imp_Cliente_Endereco.ID IS NULL;
"""

dependenteCliente = """INSERT INTO Imp_DependenteCliente(
  ID,
  Imp_ClienteID,
  Nome) 
SELECT
  cd_cliente_dependente AS ID,
  Imp_cliente.ID AS Imp_clienteID,
  TRIM(clientes_dependentes.nome) AS Nome
FROM clientes_dependentes
JOIN Imp_Cliente ON Imp_Cliente.ID = clientes_dependentes.cd_cliente_titular
LEFT JOIN Imp_DependenteCliente ON Imp_DependenteCliente.ID = clientes_dependentes.cd_cliente_dependente
WHERE Imp_DependenteCliente.ID IS NULL;
"""

planoRemuneracao = """INSERT INTO imp_planoremu(id, nome, datainicial, datafinal, considerardevolucao) VALUES ('-1', 'COMISSÃO POR PRODUTOS', NOW(), NOW() + INTERVAL '10 years', FALSE);

INSERT INTO Imp_PlanoRemuComissao (
  Imp_PlanoRemuID,
  Imp_ProdutoID,
  Comissao)
SELECT
  '-1' AS Imp_PlanoRemuID,
 Imp_Produto.ID AS Imp_ProdutoID,
 produtos.comissao::NUMERIC AS Comissao
FROM produtos
JOIN Imp_Produto ON Imp_Produto.ID = produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '')
WHERE comissao IS NOT NULL
  AND comissao::NUMERIC > 0;
"""

prescritores = """INSERT INTO Imp_Prescritor (
  ID,
  nome,
  numero,
 -- tipoconselho,
  estado,
  datainscricao)
SELECT
  medicos.id_medico AS id,
  TRIM(medicos.nome) AS nome,
  medicos.crm::INTEGER AS numero,
 /* (CASE
    WHEN tipo = 'CRM' THEN 'M'
    WHEN tipo = 'CRMV' THEN 'V'
    WHEN tipo = 'CRO' THEN 'O'
    WHEN tipo = 'COREN' THEN 'C'
    WHEN tipo = 'RMS' THEN 'R'
    ELSE 'M'
  END) AS tipoconselho, */
  COALESCE(medicos.uf) AS estado,
  medicos.datacadastro AS datainscricao
FROM medicos
WHERE uf IS NOT NULL
  AND uf <> '';
  """

crediarioReceber = """INSERT INTO Imp_CrediarioReceber (
  ID,
  Imp_ClienteID,
  NumeroDocumento,
  DataEmissao,
  DataVencimento,
  Valor,
  Imp_UnidadeNegocioID,
  NumeroParcela,
  TotalParcela,
  Observacao)
SELECT
  contas_receber.cd_contas_receber AS ID,
  clientes.cd_cliente AS Imp_ClienteID,
  contas_receber.cd_venda::NUMERIC AS NumeroDocumento,
  contas_receber.dt_lancamento::TIMESTAMP AS DataEmissao,
  contas_receber.dt_vencimento::TIMESTAMP AS DataVencimento,
  contas_receber.valor::NUMERIC(15,2) AS Valor,
  Imp_UnidadeNegocio.ID AS Imp_UnidadeNegocioID,
  (CASE
    WHEN documento ILIKE '%Parc.%' THEN REPLACE(split_part(documento, '/', 1), 'Parc.', '')
    ELSE '1'
  END)::NUMERIC AS NumeroParcela,
  (CASE
    WHEN documento ILIKE '%Parc.%' THEN REPLACE(split_part(documento, '/', 2), 'Parc.', '')
    ELSE '1'
  END)::NUMERIC AS TotalParcela,
  SUBSTRING(contas_receber.observacao, 1, 250) AS Observacao
FROM clientes
JOIN contas_receber ON contas_receber.cd_cliente = clientes.cd_cliente
JOIN Imp_UnidadeNegocio ON Imp_UnidadeNegocio.ID = contas_receber.cd_filial
WHERE contas_receber.status = 'A';
"""

custo = """INSERT INTO Imp_Custo (
  imp_produtoid,
  imp_unidadenegocioid,
  custo,
  customedio)
SELECT
  imp_produto.ID AS Imp_ProdutoID,
  '1' AS imp_unidadenegocioid,
  COALESCE(custo_unitario::NUMERIC, 0.01) AS custo,
  COALESCE(COALESCE(custo_medio::NUMERIC, custo_unitario::NUMERIC), 0.01) AS customedio
FROM produtos
JOIN imp_produto ON imp_produto.id = produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '')
WHERE custo_unitario::NUMERIC > 0;
"""

estoque = """INSERT INTO Imp_Estoque (
  imp_produtoid,
  imp_unidadenegocioid,
  estoque)
SELECT
  imp_produto.ID AS imp_produtoID,
  '1' AS imp_unidadenegocioid,
  estoque_1::NUMERIC AS estoque
FROM produtos
JOIN imp_produto ON imp_produto.id = produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '')
WHERE estoque_1::NUMERIC > 0;
"""

contasAPagar = """INSERT INTO Imp_ContaPagar (
  ID,
  Imp_UnidadeNegocioID,
  Imp_FornecedorID,
  NumeroDocumento,
  DataEmissao,
  DataVencimento,
  ValorDocumento,
  Desconto,
  Acrescimo,
  Multa,
  Observacao,
  NumeroParcela,
  TotalParcela)
SELECT
  cd_contas_pagar || '.' || COALESCE(numero_nota, '0') AS ID,
  Imp_UnidadeNegocio.ID AS Imp_UnidadeNegocioID,
  Imp_Fornecedor.ID AS Imp_FornecedorID,
  cd_contas_pagar::NUMERIC AS NumeroDocumento,
  dt_lancamento::TIMESTAMP AS DataEmissao,
  dt_vencimento::TIMESTAMP AS DataVencimento,
  valor::NUMERIC AS ValorDocumento,
  vl_desconto::NUMERIC AS Desconto,
  despesafinanceira::NUMERIC AS Acrescimo,
  vl_juros::NUMERIC AS Multa,
  SUBSTRING(contas_pagar.observacao, 1, 250) AS Observacao,
  1 AS NumeroParcela,
  1 AS TotalParcela
FROM contas_pagar
JOIN Imp_Fornecedor ON Imp_Fornecedor.ID = contas_pagar.cd_distribuidor
JOIN Imp_UnidadeNegocio ON Imp_UnidadeNegocio.ID = contas_pagar.cd_filial
WHERE contas_pagar.status = 'A';
"""

demanda = """INSERT INTO Imp_HistoricoVenda (
  Imp_ProdutoID,
  Imp_UnidadeNegocioID,
  DATA,
  Quantidade)
SELECT
  Imp_Produto.ID AS Imp_ProdutoID,
  Imp_UnidadeNegocio.ID AS Imp_UnidadeNegocioID,
  data_lancamento::TIMESTAMP AS DATA,
  SUM(quantidade::NUMERIC) AS Quantidade
FROM lancamentos
JOIN produtos ON produtos.cd_produto = lancamentos.cd_produto
JOIN Imp_Produto ON Imp_Produto.ID = produtos.cd_produto || '.' || COALESCE(TRIM(LEADING '0' FROM produtos.codigo_barras_1), '')
JOIN Imp_UnidadeNegocio ON Imp_UnidadeNegocio.ID = lancamentos.cd_filial
WHERE cd_venda IS NOT NULL
  AND quantidade::NUMERIC > 0
  AND data_lancamento::TIMESTAMP >= now() - INTERVAL '180 DAYS'
  AND lancamentos.tipo_venda = 'V' -- lançamentos do tipo venda e não transferência
GROUP BY 1,2,3;
"""
