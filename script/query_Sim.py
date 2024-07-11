# -*- coding: utf-8 -*-
tmp_produto = """DROP TABLE IF EXISTS tmp_produto;
CREATE TABLE tmp_produto (ProdutoID VARCHAR(100) PRIMARY KEY);
INSERT INTO tmp_produto
WITH ESTOQUE AS  
(SELECT PROCODIGO,
      SUM(QTDE) AS QTDE
    FROM PROESTOQUE
    GROUP BY 1
    HAVING SUM(QTDE) > 0
),tmp_prod AS (
SELECT DISTINCT
  PRO.CODIGO
FROM PRO
JOIN PROLOJA ON PROLOJA.PROCODIGO = PRO.CODIGO
JOIN SAII ON SAII.PROCODIGO = PRO.CODIGO
JOIN SAI ON SAI.CODIGO = SAII.SAICODIGO
WHERE SAI.DATACADASTRO::TIMESTAMP >= NOW() - INTERVAL '24' MONTH
  AND PROLOJA.ATIVO = TRUE
),total AS (
SELECT ESTOQUE.PROCODIGO FROM ESTOQUE
UNION ALL
SELECT tmp_prod.CODIGO FROM tmp_prod
UNION ALL
SELECT DISTINCT
  PRO.CODIGO
FROM PRO
JOIN PROLOJA ON PROLOJA.PROCODIGO = PRO.CODIGO
LEFT JOIN tmp_prod ON tmp_prod.CODIGO = PRO.CODIGO
JOIN ENTI ON ENTI.PROCODIGO = PRO.CODIGO
JOIN ENT ON ENT.CODIGO = ENTI.ENTCODIGO
WHERE ENT.DATAENTRADA::TIMESTAMP >= NOW() - INTERVAL '24' MONTH
  AND tmp_prod.CODIGO IS NULL
  AND PROLOJA.ATIVO = TRUE
) SELECT DISTINCT * FROM TOTAL
ORDER BY 1"""
  
usuario = """/* Cadastro do Usuario */
INSERT INTO Imp_Usuario (
  ID,
  Login,
  Senha,
  Apelido)
SELECT 
  funcodigo||'.'||login AS ID,
  login AS Login,
  '000' AS Senha,
  login AS Apelido
FROM FUNUSU;"""
  
unidadeNegocio = """/* Cadastro da Unidade de Negocio */
INSERT INTO imp_unidadenegocio (
  ID,
  Codigo,
  Nome,
  NomeFantasia,
  RazaoSocial,
  CNPJ,
  InscricaoEstadual,
  EstadoInscricaoEstadual,
  Endereco,
  Numero,
  Cep,
  Bairro,
  Cidade,
  Estado,
  Telefone)
SELECT 
  loja.codigo AS id,
  loja.codigo AS Codigo,
  razaosocial AS nome,
  nomefantasia AS NomeFantasia,
  razaosocial AS RazaoSocial,
  regexp_replace(cnpj, '[^0-9]', '', 'g') AS CNPJ,
  regexp_replace(ie, '[^0-9]', '', 'g') AS InscricaoEstadual,
  TRIM(crfuf) AS EstadoInscricaoEstadual,
  UPPER(TRIM(cep.nomelogradouro)) AS Endereco,
  loja.numero AS Numero,
  regexp_replace(cep.cep, '[^0-9]', '', 'g') AS Cep,
  SUBSTRING(UPPER(TRIM(bairro.nome)),1,30) AS Bairro,
  SUBSTRING(UPPER(TRIM(cidade.nome)),1,30) AS Cidade,
  TRIM(crfuf) AS Estado,
  regexp_replace(loja.cttelefone, '[^0-9]', '', 'g') AS Telefone  
FROM loja
JOIN cep ON cep.codigo = loja.cepcodigo
JOIN bairro ON bairro.codigo = cep.bairrocodigo
JOIN cidade ON cidade.codigo = cep.cidadecodigo;"""
  
grupoRemarcacao = """/* Cadastro do Grupo de Remarcação [Executar dia 1 e 2] */
INSERT INTO Imp_GrupoRemarcacao (
  ID,
  Nome)
SELECT 
  codigo AS id,
  TRIM(UPPER(DESCRICAO)) AS Nome
FROM fam
LEFT JOIN Imp_GrupoRemarcacao ON Imp_GrupoRemarcacao.ID = fam.codigo::VARCHAR
WHERE Imp_GrupoRemarcacao.ID IS NULL
  AND TRIM(UPPER(DESCRICAO)) IS NOT NULL;"""
  
principioAtivo = """/* Cadastro do Principio Ativo [Executar dia 1 e 2] */ 
INSERT INTO Imp_PrincipioAtivo (
  ID,
  Nome)
SELECT 
  CODIGO AS ID, 
  UPPER(SUBSTRING(TRIM(DESCRICAO),1,130)) AS Nome  
FROM PRINCIPIOATIVO 
LEFT JOIN Imp_PrincipioAtivo ON Imp_PrincipioAtivo.id  = PRINCIPIOATIVO.CODIGO::VARCHAR
WHERE DESCRICAO IS NOT NULL
  AND Imp_PrincipioAtivo.id  IS NULL;"""
  
fabricanteNaoInformado = """/* Cadastro do Fabricante Não Informado*/ 
INSERT INTO Imp_Fabricante(ID,Nome,Tipo) VALUES('-1', 'FABRICANTE NÃO INFORMADO', 'J');
 """
  
fabricante = """/* Cadastro do Fabricante [Executar dia 1 e 2] */ 
INSERT INTO Imp_Fabricante(
  ID,
  Nome,
  Tipo,
  CNPJ)
SELECT 
  codigo AS ID, 
  COALESCE(NULLIF(UPPER(TRIM(lab.NOME)),''),'NOME NAO INFORMADO .'||CODIGO) AS Nome, -- AO MERGIAR FABRICANTE, ANALISAR SE NÃO TERÁ OCASIÕES NO COALESCE
  'J' AS tipo,
  regexp_replace(NULLIF(TRIM(LAB.CNPJ),''),'[^0-9]', '', 'g') AS CNPJ
FROM lab
LEFT JOIN Imp_Fabricante ON Imp_Fabricante.ID = lab.CODIGO::VARCHAR
WHERE imp_fabricante.id IS NULL"""
  
classficacao = """
-- Classificacao
-- ATENÇÃO REFERENTE A PROFUNDIDADE ATUALMENTE ESTA SOMENTE ATÉ A 4

-- CLASSIFICAÇÃO RAIZ
INSERT INTO Imp_Classificacao (id, nome, profundidade, principal) VALUES ('RAIZ', 'PRINCIPAL', 0, TRUE);

-- PARA PRODUTOS SEM CLASSIFICAÇÃO
INSERT INTO Imp_Classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) VALUES ('RAIZ.NÃOINFORMADA', 'NÃO INFORMADA', 1, TRUE, 'RAIZ');

-- NÍVEL 1
INSERT INTO imp_classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) 
SELECT 
  codigo AS id,
  descricao AS nome,
  1 AS profundidade,
  TRUE AS principal,
  'RAIZ'AS imp_classificacaopaiid
FROM grp 
WHERE CODIGO = '1';

-- NÍVEL 2
INSERT INTO imp_classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) 
SELECT
  codigo AS id,
  descricao AS nome,
  2 AS profundidade,
  TRUE,
  '1' AS imp_classificacaopaiid
FROM grp 
WHERE grpcodigo = '1';

--NÍVEL 3
INSERT INTO imp_classificacao (id, nome, profundidade, principal, imp_classificacaopaiid)
SELECT
  codigo AS id,
  descricao AS nome,
  3 AS profundidade,
  TRUE,
  imp_classificacao.id AS imp_classificacaopaiid
FROM grp 
JOIN imp_classificacao ON imp_classificacao.id = grpcodigo::VARCHAR
LEFT JOIN imp_classificacao imp_clas ON imp_clas.id = grp.codigo::VARCHAR
WHERE imp_clas.id IS NULL;

-- NÍVEL 4
INSERT INTO imp_classificacao (id, nome, profundidade, principal, imp_classificacaopaiid)
SELECT
  codigo AS id,
  descricao AS nome,
  4 AS profundidade,
  TRUE,
  imp_classificacao.id AS imp_classificacaopaiid
FROM grp
JOIN imp_classificacao ON imp_classificacao.id = grpcodigo::VARCHAR
LEFT JOIN imp_classificacao imp_clas ON imp_clas.id = grp.codigo::VARCHAR
WHERE imp_clas.id IS NULL;"""
  
produto = """/*PRODUTOS*/
INSERT INTO Imp_Produto(
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
  PrecoReferencial,
  PrecoVenda,
  ListaPIS,
  listadcb,
  TipoPreco,
  RegistroMS,
  CodigoNCM,
  imp_gruporemarcacaoid,
  Imp_PrincipioAtivoID,
  Imp_ClassificacaoID,
  Tipo
 )
SELECT 
  pro.codigo AS ID,
  UPPER(SUBSTRING(TRIM(pro.descricao),1,60)) AS descricao, 
  COALESCE(Imp_Fabricante.ID, '-1') AS Imp_FabricanteID,
  SUBSTRING(TRIM(pro.codigobar),1,14) AS CodigoBarras,
   (CASE
    WHEN BTRI.ICMSCST = '60' THEN 'A' -- substituido
    WHEN BTRI.ICMSCST = '40' THEN 'B' -- isento
    WHEN BTRI.ICMSCST = '41' THEN 'C' -- não tributado
    WHEN BTRI.ICMSCST = '00' THEN 'D' -- tributado
  WHEN BTRI.ICMSCST = '0' THEN 'D' -- tributado
    ELSE 'A' -- senão substituido porque é a maioria
  END) AS TipoAliquota,
  BTRI.icmsaliq AS ValorAliquota,
  imp_cest.id AS CestID,  
  PerfilPISSn.id AS PerfilPISSnID,
  perfilcofinssn.ID AS PerfilCofinsSID,
  PerfilPIS.ID AS PerfilPISID,
  PerfilCofins.ID AS PerfilCofinsID,
  (CASE WHEN
  PROLOJA.PRECOFAB IS NULL THEN COALESCE(PROLOJA.PRECOVENDA, 0.01) ELSE COALESCE(PROLOJA.PRECOFAB, 0.01)
  END) AS PrecoReferencial,
  (CASE WHEN
  PROLOJA.PRECOVENDA IS NULL THEN COALESCE(PROLOJA.PRECOFAB, 0.01) ELSE COALESCE(PROLOJA.PRECOVENDA, 0.01)
  END) AS PrecoVenda,
  (CASE
  WHEN pro.TIPOPISCOFINS = '1' THEN 'P'
  WHEN pro.TIPOPISCOFINS = '2' THEN 'N'
  WHEN pro.TIPOPISCOFINS = '3' THEN 'U'
  ELSE 'A'
  END) AS ListaPIS,
  (CASE
  WHEN TRIM(DCB.CLASSE) = 'A1' THEN 'A'
  WHEN TRIM(DCB.CLASSE) = 'A2' THEN 'B'
  WHEN TRIM(DCB.CLASSE) = 'A3' THEN 'C'
  WHEN TRIM(DCB.CLASSE) = 'B1' THEN 'D'
  WHEN TRIM(DCB.CLASSE) = 'B2' THEN 'E'
  WHEN TRIM(DCB.CLASSE) = 'C1' THEN 'F'
  WHEN TRIM(DCB.CLASSE) = 'C2' THEN 'G'
  WHEN TRIM(DCB.CLASSE) = 'C3' THEN 'H'
  WHEN TRIM(DCB.CLASSE) = 'C4' THEN 'I'
  WHEN TRIM(DCB.CLASSE) = 'C5' THEN 'J'
  WHEN TRIM(DCB.CLASSE) = 'D1' THEN 'K'
  WHEN TRIM(DCB.CLASSE) = 'D2' THEN 'L'
  WHEN TRIM(DCB.CLASSE) = 'AM' THEN 'M'
  ELSE NULL
  END) AS listadcb,
  (CASE  
  WHEN pro.TipoPreco = '1' THEN 'L'
  WHEN pro.TipoPreco = '2' THEN 'M'
  ELSE 'L'
  END) AS TipoPreco,
  SUBSTRING(TRIM(pro.REGMS), 1 , 13) AS RegistroMS,
  TRIM(pro.NBMCODIGO) AS CodigoNCM,
  imp_gruporemarcacao.id AS imp_gruporemarcacaoid,
  Imp_PrincipioAtivo.id AS Imp_PrincipioAtivoID,
  COALESCE(Imp_Classificacao.id, 'RAIZ.NÃOINFORMADA') AS Imp_Classificacaoid,
  'M' AS Tipo
FROM
  pro
  JOIN tmp_produto ON tmp_produto.produtoid = pro.codigo::VARCHAR
  LEFT JOIN CLT  ON CLT.CODIGO = PRO.CLTCODIGO
  LEFT JOIN dcb ON dcb.CODIGO = CLT.DCBCODIGO
  LEFT JOIN Imp_Fabricante ON Imp_Fabricante.ID = pro.labcodigo::VARCHAR  
  LEFT JOIN proloja ON proloja.procodigo = pro.codigo
  LEFT JOIN Imp_Classificacao ON Imp_Classificacao.id = proloja.grpcodigo::VARCHAR    
  LEFT JOIN PROPRA ON PROPRA.PROCODIGO = pro.codigo
  LEFT JOIN imp_gruporemarcacao ON imp_gruporemarcacao.id = proloja.famcodigo::VARCHAR
  LEFT JOIN Imp_PrincipioAtivo ON Imp_PrincipioAtivo.ID = PROPRA.PRACODIGO::VARCHAR
  LEFT JOIN BTRI ON BTRI.NBMCODIGO = PRO.NBMCODIGO AND BTRI.BTRCODIGO = 1
  LEFT JOIN BTR  ON BTR.CODIGO = BTRI.BTRCODIGO AND BTR.LOJACODIGO = BTRI.LOJACODIGOBTR AND btr.loja = (SELECT codigo FROM loja WHERE LOJAFISICALOCAL = TRUE) AND BTR.tipo = 11 
  LEFT JOIN perfilpis perfilpissn ON perfilpissn.piscst = BTRI.piscst AND perfilpissn.tipocontribuinte = 'B'
  LEFT JOIN perfilcofins perfilcofinssn ON perfilcofinssn.cofinscst = BTRI.cofinscst AND perfilcofinssn.tipocontribuinte = 'B'
  LEFT JOIN Imp_Produto ON Imp_Produto.ID = pro.codigo::VARCHAR
  LEFT JOIN perfilpis ON perfilpis.piscst =  BTRI.piscst AND perfilpis.tipocontribuinte = 'A'
  LEFT JOIN perfilcofins ON perfilcofins.cofinscst = BTRI.cofinscst AND perfilcofins.tipocontribuinte = 'A'
  LEFT JOIN imp_cest ON imp_cest.codigo = TRIM(PRO.CEST)
WHERE proloja.lojacodigo = (SELECT codigo FROM loja WHERE LOJAFISICALOCAL = TRUE) /* Necessario esse filtro para a classificacao, pois a classificacao é por unidade de negocio 
										   portanto essa query aponta a loja principal, SEMPRE CONFERIR */
  AND pro.codigo <> 0 AND PRO.CODIGO <> 99999 --99999 Trata-se do código de serviço de entrega   
  AND imp_produto.id IS NULL;
 """
  
produtoMae = """-- Inserindo as embalagens MAES
INSERT INTO Imp_Produto(
  ID,
  Descricao,
  Apresentacao,
  Imp_FabricanteID,
  TipoAliquota,
  ValorAliquota,
  CestID,
  PerfilPISSnID,
  PerfilCofinsSnID,
  PerfilPISID,
  PerfilCofinsID,
  PrecoReferencial,
  PrecoVenda,
  ListaPIS,
  listadcb,
  TipoPreco,
  RegistroMS,
  CodigoNCM,
  Imp_PrincipioAtivoID,
  Imp_ClassificacaoID,
  Tipo,
  IDProdutoContido,
  QuantidadeEmbalagem
  )
SELECT  
  '-' || imp_produto.ID AS ID,
  imp_produto.Descricao,
  'CX C/' || pro.qtdefracio AS Apresentacao,
  imp_produto.Imp_FabricanteID,
  imp_produto.TipoAliquota,
  imp_produto.ValorAliquota,
  imp_produto.CestID,
  imp_produto.PerfilPISSnID,
  imp_produto.PerfilCofinsSnID,
  imp_produto.PerfilPISID,
  imp_produto.PerfilCofinsID,
  imp_produto.PrecoReferencial * pro.qtdefracio AS PrecoReferencial,
  imp_produto.PrecoVenda * pro.qtdefracio AS PrecoVenda,
  imp_produto.ListaPIS,
  imp_produto.listadcb,
  imp_produto.TipoPreco,
  imp_produto.RegistroMS,
  imp_produto.CodigoNCM,
  imp_produto.Imp_PrincipioAtivoID,
  imp_produto.Imp_ClassificacaoID,
  imp_produto.Tipo,
  imp_produto.id AS IDProdutoContido,
  pro.qtdefracio AS QuantidadeEmbalagem
FROM imp_produto
JOIN pro ON pro.codigo::VARCHAR = Imp_Produto.ID
LEFT JOIN imp_produto imp_pro ON imp_pro.id = '-' || imp_produto.ID
WHERE pro.qtdefracio > 1
  AND imp_pro.id IS NULL;
 """
  
codigoDeBarrasAdicional = """-- CODIGO DE BARRAS ADICIONAL
 
/* Cadastro do Codigo de barras Adicional[Executar dia 1 e 2] */
INSERT INTO imp_codigobarras(
  codigobarras,
  imp_produtoid)
SELECT DISTINCT ON (SUBSTRING(regexp_replace(ltrim(probar.PROCODIGOBAR, '0'), '[^0-9]','','g'), 1,14))
  SUBSTRING(regexp_replace(ltrim(probar.PROCODIGOBAR, '0'), '[^0-9]','','g'), 1,14) AS codigobarras,
  imp_produto.id
FROM probar
JOIN imp_produto ON imp_produto.id = probar.procodigo::VARCHAR 
LEFT JOIN imp_codigobarras ON imp_codigobarras.codigobarras = SUBSTRING(regexp_replace(ltrim(probar.PROCODIGOBAR, '0'), '[^0-9]','','g'), 1,14)
WHERE SUBSTRING(regexp_replace(ltrim(probar.PROCODIGOBAR, '0'), '[^0-9]','','g'), 1,14) IS NOT NULL
  AND SUBSTRING(regexp_replace(ltrim(probar.PROCODIGOBAR, '0'), '[^0-9]','','g'), 1,14) <> ''
  AND imp_codigobarras.codigobarras IS NULL
  AND imp_produto.codigobarras <> SUBSTRING(regexp_replace(ltrim(probar.PROCODIGOBAR, '0'), '[^0-9]','','g'), 1,14);"""
  
duploPerfilImcs = """-- Produtos cadastrados com CSOSN
-- ICMS
INSERT INTO imp_icmsproduto(
  imp_produtoid,
  perfilicmssnid,
  perfilicmsid,
  estado)
WITH icmsproduto AS (
SELECT DISTINCT
  imp_produto.id AS imp_produtoid,
  perfilsimples.id AS perfilicmssnid,
  perfillucro.ID AS perfilicmsid,
  imp_unidadenegocio.estado AS estado
FROM pro
JOIN imp_produto ON imp_produto.id = PRO.codigo::VARCHAR
JOIN BTRI ON BTRI.NBMCODIGO = PRO.NBMCODIGO AND BTRI.BTRCODIGO = (SELECT codigo FROM btr WHERE loja = (SELECT codigo FROM loja WHERE LOJAFISICALOCAL = '1') AND tipo = 11)
LEFT JOIN perfilicms perfilsimples ON (perfilsimples.icmssncso = CASE 
                    WHEN BTRI.ICMSCST = '00' THEN '102'
                    WHEN BTRI.ICMSCST = '10' THEN '202'
                    WHEN BTRI.ICMSCST = '20' THEN '102'
                    WHEN BTRI.ICMSCST = '30' THEN '203'
                    WHEN BTRI.ICMSCST = '40' THEN '300'
                    WHEN BTRI.ICMSCST = '41' THEN '400'
                    WHEN BTRI.ICMSCST = '50' THEN '400'
                    WHEN BTRI.ICMSCST = '51' THEN '400'
                    WHEN BTRI.ICMSCST = '60' THEN '500'
                    WHEN BTRI.ICMSCST = '70' THEN '500'
                      END)
LEFT JOIN perfilicms perfillucro ON perfillucro.icmscst = BTRI.ICMSCST,
imp_unidadenegocio            
WHERE BTRI.csosn IS NULL
)
SELECT DISTINCT ON (icmsproduto.imp_produtoid, icmsproduto.estado)
  icmsproduto.*
FROM icmsproduto
LEFT JOIN imp_icmsproduto ON imp_icmsproduto.imp_produtoid = icmsproduto.imp_produtoid AND imp_icmsproduto.estado = icmsproduto.estado
WHERE imp_icmsproduto.imp_produtoid IS NULL
  AND (icmsproduto.perfilicmssnid IS NOT NULL
  OR icmsproduto.perfilicmsid IS NOT NULL);"""

impostoSimples = """-- ICMS
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
JOIN BTRI ON (perfilicms.icmssncso = CASE 
          WHEN BTRI.ICMSCST = '00' THEN '102'
          WHEN BTRI.ICMSCST = '10' THEN '202'
          WHEN BTRI.ICMSCST = '20' THEN '102'
          WHEN BTRI.ICMSCST = '30' THEN '203'
          WHEN BTRI.ICMSCST = '40' THEN '300'
          WHEN BTRI.ICMSCST = '41' THEN '400'
          WHEN BTRI.ICMSCST = '50' THEN '400'
          WHEN BTRI.ICMSCST = '51' THEN '400'
          WHEN BTRI.ICMSCST = '60' THEN '500'
          WHEN BTRI.ICMSCST = '70' THEN '500'
              END)
JOIN PRO ON BTRI.NBMCODIGO = PRO.NBMCODIGO AND BTRI.BTRCODIGO = (SELECT codigo FROM btr WHERE loja = (SELECT codigo FROM loja WHERE LOJAFISICALOCAL = '1') AND tipo = 11)
JOIN imp_produto ON imp_produto.id = PRO.codigo::VARCHAR, imp_unidadenegocio
)
SELECT DISTINCT ON (icmsproduto.imp_produtoid, icmsproduto.estado)
  icmsproduto.*
FROM icmsproduto
LEFT JOIN imp_icmsproduto ON imp_icmsproduto.imp_produtoid = icmsproduto.imp_produtoid AND imp_icmsproduto.estado = icmsproduto.estado
WHERE imp_icmsproduto.imp_produtoid IS NULL;"""

impostoLucroPresumido = """-- Lucro Real/Presumido
-- ICMS
INSERT INTO imp_icmsproduto(
  imp_produtoid,
  perfilicmsid,
  estado)
WITH icmsproduto AS (
SELECT DISTINCT
  imp_produto.id AS imp_produtoid,
  perfilicms.id AS perfilicmsid,
  imp_unidadenegocio.estado AS estado
FROM perfilicms
JOIN BTRI ON perfilicms.icmscst = BTRI.ICMSCST
JOIN PRO ON BTRI.NBMCODIGO = PRO.NBMCODIGO AND BTRI.BTRCODIGO =  (SELECT codigo FROM btr WHERE loja = (SELECT codigo FROM loja WHERE LOJAFISICALOCAL = '1') AND tipo = 11)
JOIN imp_produto ON imp_produto.id = PRO.codigo::VARCHAR, imp_unidadenegocio
)
SELECT DISTINCT ON (icmsproduto.imp_produtoid, icmsproduto.estado)
  icmsproduto.*
FROM icmsproduto
LEFT JOIN imp_icmsproduto ON imp_icmsproduto.imp_produtoid = icmsproduto.imp_produtoid AND imp_icmsproduto.estado = icmsproduto.estado
WHERE imp_icmsproduto.imp_produtoid IS NULL;"""
  
fornencedor = """-- Fornecedores
INSERT INTO Imp_Fornecedor(
  ID,
  Nome,
  Tipo,
  Telefone,
  Email,
  CNPJ,
  CPF,
  INSCRICAOESTADUAL,
  IDENTIDADE,
  Observacao)
SELECT DISTINCT
  frn.CODIGO AS id,
   COALESCE(UPPER(REPLACE(TRIM(frn.NOME),'''','')), 'NOME NÃO INFORMADO') AS nome,
   (CASE
     WHEN tipopessoa = TRUE THEN 'J'
     ELSE 'F'
   END) AS tipo,
  ltrim(regexp_replace(NULLIF(TRIM((SELECT numero FROM frntel WHERE frn.codigo = frntel.frncodigo AND frntel.tipo = 1 LIMIT 1)),''),'[^0-9]', '', 'g'),'0') AS Telefone,
  SUBSTRING(TRIM(frn.email),1,50) AS Email,
  (CASE
     WHEN tipopessoa = TRUE THEN NULLIF(NULLIF(regexp_replace(NULLIF(TRIM(CPFCNPJ),''),'[^0-9]', '', 'g'), '0'), '')
   END) AS CNPJ,
   (CASE
     WHEN tipopessoa = FALSE THEN SUBSTRING(NULLIF(NULLIF(regexp_replace(NULLIF(TRIM(CPFCNPJ),''),'[^0-9]', '', 'g'), '0'), ''), 1, 11)
   END) AS CPF,
   (CASE
     WHEN tipopessoa = TRUE THEN NULLIF(NULLIF(regexp_replace(NULLIF(TRIM(ierg),''),'[^0-9]', '', 'g'), '0'), '')
   END) AS inscricaoestadual,
   (CASE
     WHEN tipopessoa = FALSE THEN SUBSTRING(NULLIF(NULLIF(regexp_replace(NULLIF(TRIM(ierg),''),'[^0-9A-z]', '', 'g'), '0'), ''),1 , 15)
   END) AS identidade,
  NULLIF(UPPER(TRIM(frn.obs)),'') AS Observacao
FROM frn
LEFT JOIN Imp_Fornecedor ON Imp_Fornecedor.ID = frn.codigo::VARCHAR
WHERE  Imp_Fornecedor.ID IS NULL
  AND frn.nome IS NOT NULL
  AND frn.nome <> '';
  /* Endereco do Fornecedor [Executar dia 1 e 2] */
INSERT INTO imp_fornecedor_endereco(
  ID,
  Imp_Fornecedorid,
  Endereco,
  Numero,
  Cep,
  Bairro,
  Cidade,
  Estado)
SELECT
  frn.CODIGO AS id,
  Imp_Fornecedor.ID AS Imp_FornecedorID,
  COALESCE(NULLIF(UPPER(TRIM(cep.nomelogradouro)),''), 'ENDEREÇO NÃO INFORMADO') AS Endereco,
  COALESCE(SUBSTRING(NULLIF(TRIM(frn.numero),''), 1, 6), 'N/I') AS Numero,
  TRIM(regexp_replace(cep.cep,'[^0-9]','','g')) AS Cep,
  COALESCE(NULLIF(UPPER(TRIM(bairro.nome)),''), 'BAIRRO NÃO INFORMADO') AS Bairro,
  COALESCE(NULLIF(UPPER(TRIM(cidade.nome)),''), 'CIDADE NÃO INFORMADA') AS Cidade,
  COALESCE(NULLIF(UPPER(TRIM(cidade.estado)),''),'SP') AS Estado
FROM frn
JOIN cep ON cep.codigo = frn.cepcodigo
JOIN bairro ON bairro.codigo = cep.bairrocodigo
JOIN cidade ON cidade.codigo = cep.cidadecodigo
JOIN imp_fornecedor ON imp_fornecedor.ID = frn.codigo::VARCHAR
LEFT JOIN imp_fornecedor_endereco ON imp_fornecedor_endereco.ID = frn.codigo::VARCHAR
WHERE imp_fornecedor_endereco.ID IS NULL;"""
  
planoPagamento = """-- PLANO DE PAGAMENTO
/*PARTICULAR*/
INSERT INTO Imp_PlanoPagamento (ID, Nome, MinParcela, MaxParcela, TipoIntervaloEntrada, IntervaloEntrada, TipoIntervaloParcela, IntervaloParcela) VALUES ('0', '0.PARTICULAR', 1, 1, 'M', 1, 'M', 1);

/*CREDIARIO PRÓPRIO(ESPECIAL*/
INSERT INTO Imp_PlanoPagamento (ID, Nome, MinParcela, MaxParcela, TipoIntervaloEntrada, IntervaloEntrada, TipoIntervaloParcela, IntervaloParcela) VALUES ('-2', 'PARTICULAR (ESPECIAL)', 1, 1, 'M', 1, 'M', 1);

/*PLANO PAGAMENTO*/
-- Na tabela cnv o tipopag = 2 é convenio com forma de pagamento avista, e o tipopag = 1 é a prazo
INSERT INTO Imp_PlanoPagamento(
  ID,
  Nome,
  MinParcela,
  MaxParcela,
  IntervaloEntrada,
  IntervaloParcela)
SELECT DISTINCT
  CODIGO AS id, 
  CODIGO ||'.'||UPPER(TRIM(NOME)) AS nome,
  1 AS MinParcela,
  COALESCE(qtdmaxparcparcelamento,1) AS MaxParcela,
  0 AS IntervaloEntrada,
  1 AS IntervaloParcela
FROM cnv;

/*FECHAMENTO DO PLANO PAGAMENTO*/
INSERT INTO Imp_FechamentoPlanoPagamento (
  ID,
  Imp_PlanoPagamentoID,
  DiaFechamento,
  DiaVencimento)
SELECT DISTINCT
  codigo AS ID,
  imp_planopagamento.id AS imp_planopagamentoid,
  (CASE WHEN
    diafech IS NULL THEN '30' ELSE diafech
  END) AS DiaFechamento,
  (CASE WHEN
    diavenc IS NULL THEN '30' ELSE diavenc
  END) AS DiaVencimento
FROM cnv
JOIN imp_planopagamento ON imp_planopagamento.id = cnv.codigo::VARCHAR;"""
  
cadernoDeOferta = """/* Cadastro do Caderno de Ofertas */
/* Inserindo caderno de ofertas de Ofertas por desconto */
INSERT INTO Imp_CadernoOferta(
  ID, 
  Nome, 
  DataHoraInicial, 
  DataHoraFinal)
SELECT DISTINCT
  DESCONTO.codigo AS ID,
  UPPER(TRIM(DESCONTO.DESCRICAO)) AS Nome,
  datainicial::TIMESTAMP AS DataHoraInicial,
  datafinal::TIMESTAMP AS DataHoraFinal
FROM DESCPROD
JOIN imp_produto ON imp_produto.id =  DESCPROD.PROCODIGO::VARCHAR
JOIN DESCONTO ON DESCONTO.codigo = DESCPROD.DESCONTOCODIGO
WHERE datafinal > now()
  AND ativo = TRUE
ORDER BY 1;

/*ITENS DOS CADERNOS DE OFERTA DO TIPO DESCONTO E PRECO*/
INSERT INTO Imp_ItemCadernoOferta(
  Imp_CadernoOfertaID,
  Imp_ProdutoID,
  TipoOferta,
  DescontoOferta,
  precoOferta)
SELECT DISTINCT
  Imp_CadernoOferta.ID AS Imp_CadernoOfertaID,
  imp_produto.ID AS Imp_ProdutoID,
  (CASE 
      WHEN DESCPROD.PERDESC IS NULL AND DESCPROD.VALOR IS NOT NULL THEN 'P'
  ELSE 'D'	  
  END) AS TipoOferta,
  (CASE WHEN
     DESCPROD.PERDESC > 0 AND DESCPROD.VALOR IS NULL THEN DESCPROD.PERDESC
  END)::NUMERIC(15,2) AS DescontoOferta,
  (CASE WHEN
    DESCPROD.VALOR > 0 AND DESCPROD.PERDESC IS NULL THEN DESCPROD.VALOR
  END)::NUMERIC(15,2)  AS PrecoOferta
FROM DESCPROD
JOIN imp_produto ON imp_produto.ID = DESCPROD.PROCODIGO::VARCHAR
JOIN DESCONTO ON DESCONTO.CODIGO = DESCPROD.DESCONTOCODIGO
JOIN Imp_CadernoOferta ON Imp_CadernoOferta.ID = DESCONTO.CODIGO::VARCHAR
WHERE datafinal > now()
  AND (DESCPROD.VALOR > 0 OR DESCPROD.PERDESC > 0)
ORDER BY 2;"""
  
cadernoDeOfertaQuantidade = """-- INSERINDO CADERNOS DE OFERTA POR QUANTIDADE
INSERT INTO Imp_CadernoOferta(
  ID, 
  Nome, 
  DataHoraInicial, 
  DataHoraFinal)
SELECT DISTINCT 
  DESCONTO.CODIGO||'.DESC_QTDE' AS ID,
  UPPER(TRIM(DESCONTO.DESCRICAO))||'.DESC_QTDE' AS NOME,
  datainicial::TIMESTAMP AS DataHoraInicial,
  datafinal::TIMESTAMP AS DataHoraFinal
FROM DESCONTO
JOIN descqtde ON descqtde.DESCONTOCODIGO = DESCONTO.CODIGO
WHERE ATIVO = TRUE
  AND DATAFINAL > NOW();


INSERT INTO imp_itemcadernoofertaquantidade (
   Imp_CadernoOfertaID, 
   Imp_ProdutoID,
   Quantidade, 
   Desconto, 
   DescontoPorQtdVendaAcimaQtd, 
   DescontoPorQtdTipo)
WITH a AS (
SELECT 
	lojacodigo,
	procodigo,
	descontocodigo,
	qtde,
	perdesc
FROM descqtde
), qtde_1 AS(
SELECT	
	a.qtde,
	a.perdesc,
	descqtde.qtde AS qtd_certa,
	descqtde.perdesc,
    a.lojacodigo,
	a.procodigo,
	a.descontocodigo,
	descqtde.perdesc AS porcentagem,
	descqtde.perdesc::NUMERIC(15,2) AS calculo
FROM descqtde
  JOIN a ON a.lojacodigo = descqtde.lojacodigo AND a.procodigo = descqtde.procodigo AND a.descontocodigo = descqtde.descontocodigo
WHERE a.qtde::NUMERIC(15,2) = 1
  AND descqtde.qtde::NUMERIC(15,2) = 1
), qtde_2 AS (
SELECT	
	a.qtde,
	a.perdesc,
	descqtde.qtde AS qtd_certa,
	descqtde.perdesc,
        a.lojacodigo,
	a.procodigo,
	a.descontocodigo,
	descqtde.perdesc + a.perdesc AS porcentagem,
	((COALESCE(a.perdesc::NUMERIC(15,2),descqtde.perdesc::NUMERIC(15,2))+descqtde.perdesc::NUMERIC(15,2))/descqtde.qtde::NUMERIC(15,2))::NUMERIC(15,2) AS calculo
FROM descqtde
  JOIN a ON a.lojacodigo = descqtde.lojacodigo AND a.procodigo = descqtde.procodigo AND a.descontocodigo = descqtde.descontocodigo
WHERE a.qtde::NUMERIC(15,2) = 1
  AND descqtde.qtde::NUMERIC(15,2) = 2
), qtde_3 AS (
SELECT
	a.qtde,
	a.perdesc,
	descqtde.qtde AS qtd_certa,
	descqtde.perdesc,
	a.lojacodigo,
	a.procodigo,
	a.descontocodigo,
	qtde_2.porcentagem + descqtde.perdesc AS porcentagem,
	((COALESCE(a.perdesc,descqtde.perdesc) + descqtde.perdesc)/descqtde.qtde)::NUMERIC(15,2) AS calculo
FROM descqtde
  JOIN a ON a.lojacodigo = descqtde.lojacodigo AND a.procodigo = descqtde.procodigo AND a.descontocodigo = descqtde.descontocodigo
  LEFT JOIN qtde_2 ON qtde_2.lojacodigo = descqtde.lojacodigo AND qtde_2.procodigo = descqtde.procodigo AND qtde_2.descontocodigo = descqtde.descontocodigo
WHERE a.qtde::NUMERIC(15,2) = 2
  AND descqtde.qtde::NUMERIC(15,2) = 3
), qtde_4 AS (
SELECT
	a.qtde,
	a.perdesc,
	descqtde.qtde AS qtd_certa,
	descqtde.perdesc,
	a.lojacodigo,
	a.procodigo,
	a.descontocodigo,
	qtde_3.porcentagem + descqtde.perdesc AS porcentagem,
	((a.perdesc::NUMERIC(15,2)+descqtde.perdesc::NUMERIC(15,2))/descqtde.qtde::NUMERIC(15,2))::NUMERIC(15,2) AS calculo
FROM descqtde
  JOIN a ON a.lojacodigo = descqtde.lojacodigo AND a.procodigo = descqtde.procodigo AND a.descontocodigo = descqtde.descontocodigo
  LEFT JOIN qtde_3 ON qtde_3.lojacodigo = descqtde.lojacodigo AND qtde_3.procodigo = descqtde.procodigo AND qtde_3.descontocodigo = descqtde.descontocodigo
WHERE a.qtde::NUMERIC(15,2) = 3
  AND descqtde.qtde::NUMERIC(15,2) = 4
), qtde_5 AS (
SELECT
	a.qtde,
	a.perdesc,
	descqtde.qtde AS qtd_certa,
	descqtde.perdesc,
	a.lojacodigo,
	a.procodigo,
	a.descontocodigo,
	qtde_4.porcentagem + descqtde.perdesc AS porcentagem,
	((a.perdesc::NUMERIC(15,2)+descqtde.perdesc::NUMERIC(15,2))/descqtde.qtde::NUMERIC(15,2))::NUMERIC(15,2) AS calculo
FROM descqtde
  JOIN a ON a.lojacodigo = descqtde.lojacodigo AND a.procodigo = descqtde.procodigo AND a.descontocodigo = descqtde.descontocodigo
  LEFT JOIN qtde_4 ON qtde_4.lojacodigo = descqtde.lojacodigo AND qtde_4.procodigo = descqtde.procodigo AND qtde_4.descontocodigo = descqtde.descontocodigo
WHERE a.qtde::NUMERIC(15,2) = 4
  AND descqtde.qtde::NUMERIC(15,2) = 5
),TOTAL AS (
SELECT DISTINCT * 
FROM qtde_1
UNION ALL SELECT * FROM qtde_2
UNION ALL SELECT * FROM qtde_3
UNION ALL SELECT * FROM qtde_4
UNION ALL SELECT * FROM qtde_5
ORDER BY 6,7
) 
SELECT 
  imp_cadernooferta.id AS Imp_CadernoOfertaID,
  imp_produto.id AS imp_produtoid,
  total.qtd_certa AS Quantidade,
  ROUND((porcentagem / total.qtd_certa),2)::NUMERIC(15,4) AS desconto,
  'B'::VARCHAR AS DescontoPorQtdVendaAcimaQtd,
  'A'::VARCHAR AS DescontoPorQtdTipo
FROM TOTAL
  JOIN imp_produto ON imp_produto.id = total.procodigo::VARCHAR
  JOIN imp_cadernooferta ON imp_cadernooferta.id = total.descontocodigo||'.DESC_QTDE'::VARCHAR
ORDER BY 2,1,3;  """
  
cadernoDeOfertaClassificacao = """-- CADERNO DE OFERTAS POR CLASSIFICACAO
INSERT INTO Imp_CadernoOferta(
  ID, 
  Nome, 
  DataHoraInicial, 
  DataHoraFinal)
SELECT DISTINCT
  DESCONTO.codigo||'.CLASSI' AS ID,
  UPPER(TRIM(DESCONTO.DESCRICAO))||'.CLASSI' AS Nome,
  datainicial::TIMESTAMP AS DataHoraInicial,
  datafinal::TIMESTAMP AS DataHoraFinal
FROM DESCONTO
JOIN descgrpr ON descgrpr.descontocodigo = DESCONTO.codigo
JOIN Imp_Classificacao ON Imp_Classificacao.id = descgrpr.grpcodigo::VARCHAR
WHERE datafinal > now()
  AND ativo = TRUE
  AND (desconto.sugeredesconto = TRUE OR desconto.OBRIGADESCONTO = TRUE) 
ORDER BY 1;

-- Itens por Classificação (Grupos)
INSERT INTO imp_itemcadernooferta (
  imp_cadernoofertaid,
  IMP_ClassificacaoID,
  tipooferta,
  descontooferta)
SELECT DISTINCT ON (Imp_Classificacao.ID)
  imp_cadernooferta.ID AS imp_cadernoofertaid,
  Imp_Classificacao.ID AS ClassificacaoID,
  'D' AS tipooferta,
  descgrpr.perdesc AS descontooferta
FROM descgrpr
JOIN imp_cadernooferta ON imp_cadernooferta.ID = descgrpr.DESCONTOCODIGO||'.CLASSI'::VARCHAR
JOIN Imp_Classificacao ON Imp_Classificacao.id = descgrpr.grpcodigo::VARCHAR
 """

cadernoDeOfertaLevePague = """-- CADERNO OFERTA POR QUANTIDADE 
-- ATENÇÃO ESSE SCRIPT FOI BASEADO NO CLIENTE 1879 ONDE O DESCONTO POR QUANTIDADE É APLICADO APENAS EM UM ITEM NA COMPRA

-- INSERINDO CADERNOS DE OFERTA POR QUANTIDADE
INSERT INTO Imp_CadernoOferta(
  ID, 
  Nome, 
  DataHoraInicial, 
  DataHoraFinal)
SELECT DISTINCT 
  DESCONTO.CODIGO||'.DESC_QTDE' AS ID,
  UPPER(TRIM(DESCONTO.DESCRICAO))||'.DESC_QTDE' AS NOME,
  datainicial::TIMESTAMP AS DataHoraInicial,
  datafinal::TIMESTAMP AS DataHoraFinal
FROM DESCONTO
JOIN descqtde ON descqtde.DESCONTOCODIGO = DESCONTO.CODIGO
WHERE ATIVO = TRUE
  AND DATAFINAL > NOW();

-- Inserindo caderno de oferta por quantidade
INSERT INTO imp_itemcadernoofertaquantidade (
  Imp_CadernoOfertaID, 
  Imp_ProdutoID,
  Quantidade, 
  PRECOTOTAL, 
  DescontoPorQtdVendaAcimaQtd, 
  DescontoPorQtdTipo)  
SELECT
  imp_cadernooferta.id AS Imp_CadernoOfertaID, 
  imp_produto.id AS Imp_ProdutoID,
  descqtde.qtde AS Quantidade,
  ROUND((imp_produto.precovenda * descqtde.qtde) - (imp_produto.precovenda * (descqtde.perdesc/100))::NUMERIC(15,4),2) AS PRECOTOTAL,  
  'B'::VARCHAR AS DescontoPorQtdVendaAcimaQtd,
  'C'::VARCHAR AS DescontoPorQtdTipo  
FROM descqtde
JOIN imp_produto ON imp_produto.id = descqtde.procodigo::VARCHAR
JOIN imp_cadernooferta ON imp_cadernooferta.id = descqtde.DESCONTOCODIGO||'.DESC_QTDE'::VARCHAR
WHERE descqtde.perdesc > 0;""" 

cadernoDeOfertaUnidade = """-- Unidade de negócio do caderno de oferta
INSERT INTO imp_uncadernooferta (
  Imp_CadernoOfertaID,
  Imp_UnidadeNegocioID
)
SELECT DISTINCT
  Imp_CadernoOferta.ID AS CadernoOfertaID,
  Imp_UnidadeNegocio.ID AS UnidadeNegocioID
FROM DESCLOJA
JOIN Imp_CadernoOferta ON ((Imp_CadernoOferta.ID = DESCLOJA.DESCONTOCODIGO::VARCHAR) OR (imp_cadernooferta.ID = DESCLOJA.DESCONTOCODIGO||'.CLASSI'::VARCHAR))
JOIN Imp_UnidadeNegocio ON Imp_UnidadeNegocio.ID = Imp_UnidadeNegocio.CODIGO::VARCHAR
ORDER BY 1;"""
 
crediario = """--CREDIÁRIO PARTICULAR
INSERT INTO Imp_Crediario (ID, NomeCrediario, LimitePadraoCliente, Imp_PlanoPagamentoID) VALUES ('0', 'PARTICULAR', 0, '0');

--CREDIÁRIO AVISTA
INSERT INTO Imp_Crediario (ID, NomeCrediario, LimitePadraoCliente, Imp_PlanoPagamentoID) VALUES ('AVISTA', 'AVISTA', 0, '0');

-- INSERINDO CREDIARIOS

INSERT INTO Imp_Crediario (
  ID,
  NomeCrediario,
  LimitePadraoCliente,
  Imp_PlanoPagamentoID,
  Toleranciaatraso,	
  TipoCrediario,
  Nome,
  Tipo,
  Telefone,
  Telefone2,
  Email,
  CNPJ,
  InscricaoEstadual,
  EstadoInscricaoEstadual
)
WITH CONVENIO AS (
  SELECT DISTINCT
    cnvcodigo 
  FROM cli 
  WHERE cnvcodigo IS NOT NULL 
)
SELECT DISTINCT
  CNV.codigo AS id,
  CNV.nome AS NomeCrediario,
  COALESCE(CNV.limitecliente,'0')::NUMERIC(15,4) AS LimitePadraoCliente,
  imp_planopagamento.id  AS Imp_PlanoPagamentoID,
  COALESCE(cnv.diascarencia, 0) AS Toleranciaatraso,  (CASE 
    WHEN CONVENIO.CNVCODIGO IS NOT NULL THEN 'C'
    ELSE 'P'
   END) AS TipoCrediario,
  UPPER(TRIM(CNV.nome)) AS nome,
  (CASE
  WHEN NULLIF(regexp_replace(TRIM(cnv.cpfcnpj),'[^0-9]', '', 'g'),'') IS NOT NULL THEN 'J'
  ELSE 'F'
  END) AS tipo,
  NULLIF(regexp_replace(TRIM(split_part(cnv.telefone, ' OU ', 1)),'[^0-9]', '', 'g'),'') AS Telefone,
  regexp_replace(NULLIF(TRIM(split_part(cnv.telefone, ' OU ', 2)),''),'[^0-9]', '', 'g') AS Telefone_2,
  SUBSTRING(NULLIF(TRIM(cnv.email),''),1,50) AS Email,
  NULLIF(regexp_replace(TRIM(cnv.cpfcnpj),'[^0-9]', '', 'g'),'') AS CNPJ,
  NULLIF(regexp_replace(TRIM(cnv.ie),'[^0-9]', '', 'g'),'') AS InscricaoEstadual,
  'SP' AS EstadoInscricaoEstadual
FROM CNV
LEFT JOIN convenio ON convenio.cnvcodigo = cnv.codigo
LEFT JOIN imp_planopagamento ON imp_planopagamento.id = cnv.codigo::VARCHAR;"""
  
cliente = """-- CLIENTES
/*Cadastro do cliente [Executar dia 1 e 2] */
INSERT INTO Imp_Cliente (
  ID,
  Imp_CrediarioID,
  STATUS,	
  NumeroCartao,
  DataAberturaCrediario,
  TipoLimite,
  Limite,
  Nome,
  Tipo,
  Mensagemvenda,
  Telefone,
  Email,
  DataNascimento,
  Sexo,
  Cnpj,
  CPF,
  inscricaoestadual,
  identidade,
  SiglaOrgaoIdentidade,
  EstadoIdentidade,
  numerocartaoexportacao
)
SELECT DISTINCT
  cli.codigo AS id,
  		(CASE
       	WHEN cli.TIPO = 1 THEN 'AVISTA'
       	WHEN cli.TIPO = 3 THEN COALESCE(imp_crediario.id,'0')
       	ELSE '0'
  END) AS Imp_CrediarioID,
	 	(CASE
       	WHEN cli.ativo = '0' THEN 'I'
       	ELSE 'A'
  END) AS STATUS,	
  TRIM(cli.cartaofidelidade) AS NumeroCartao,
  cli.datacadastro::TIMESTAMP AS DataAberturaCrediario,
  		(CASE
       	WHEN cli.TIPO = 3 THEN 'C'
       	WHEN (CASE WHEN limitecompra > 0 THEN limitecompra ELSE 0 END) = 0 THEN 'S'
      	ELSE 'P'
  END) AS TipoLimite, 
  		(CASE WHEN limitecompra > 0 THEN limitecompra ELSE 0 
  END) AS Limite,
  NULLIF(UPPER(TRIM(cli.nome)),'') AS Nome,
  		(CASE
     	WHEN tipopessoa = TRUE THEN 'J'
     	ELSE 'F'
  END) AS Tipo,
  SUBSTRING(cli.obs, 1 ,255) AS MensagemVenda,
  regexp_replace(NULLIF(TRIM((SELECT CLITEL.NUMERO FROM CLITEL WHERE CLITEL.CLICODIGO = CLI.CODIGO LIMIT 1)),''),'[^0-9]', '', 'g') AS TELEFONE,
  SUBSTRING(TRIM(cli.email),1,50) AS Email,
  cli.datanascimento::TIMESTAMP AS DataNascimento,
    	(CASE
    	WHEN cli.sexo = 1 THEN 'M'
    	WHEN cli.sexo = 2 THEN 'F'
  END) AS Sexo,
     	(CASE
     	WHEN tipopessoa = TRUE THEN SUBSTRING(NULLIF(NULLIF(regexp_replace(NULLIF(TRIM(CPFCNPJ),''),'[^0-9]', '', 'g'), '0'), ''), 1, 14)
  END) AS CNPJ,
     	(CASE
     	WHEN tipopessoa = FALSE THEN SUBSTRING(NULLIF(NULLIF(regexp_replace(NULLIF(TRIM(CPFCNPJ),''),'[^0-9]', '', 'g'), '0'), ''), 1, 11)
  END) AS CPF,
     	(CASE
     	WHEN tipopessoa = TRUE THEN SUBSTRING(NULLIF(NULLIF(regexp_replace(NULLIF(TRIM(rg),''),'[^0-9]', '', 'g'), '0'), ''),1,20)
  END) AS inscricaoestadual,
     	(CASE
     	WHEN tipopessoa = FALSE THEN SUBSTRING(NULLIF(NULLIF(regexp_replace(NULLIF(TRIM(rg),''),'[^0-9A-z]', '', 'g'), '0'), ''),1,15)
  END) AS identidade,
  TRIM(orgaoemissor) AS SiglaOrgaoIdentidade,
  SUBSTRING(TRIM(ufemissor), 1 , 2) AS EstadoIdentidade,
  TRIM(cli.matricula) AS numerocartaoexportacao
FROM cli
 JOIN imp_unidadenegocio ON imp_unidadenegocio.id = cli.lojacodigo::VARCHAR
 LEFT JOIN imp_crediario ON imp_crediario.id = cli.cnvcodigo::VARCHAR
 LEFT JOIN Imp_Cliente ON Imp_Cliente.ID = cli.codigo::VARCHAR
WHERE Imp_Cliente.ID IS NULL
  AND NULLIF(TRIM(cli.nome),'') IS NOT NULL;


-- Endereco de cliente
INSERT INTO imp_cliente_endereco(
  id,
  imp_clienteid,
  endereco,
  numero,
  complemento,
  cep,
  bairro,
  cidade,
  estado)
SELECT
  cliend.codigo AS id,
  imp_cliente.id AS imp_clienteid,
  COALESCE(NULLIF(UPPER(TRIM(TIPOLOGRADOURO.ABREVIATURA)),''),'R') ||'.'||COALESCE(SUBSTRING(UPPER(TRIM(cep.nomelogradouro)),1,70),'N/I') AS endereco,
  SUBSTRING(COALESCE(CLIEND.numero,'N/I'),1,6) AS numero,
  SUBSTRING(cliend.complemento,1,30) AS complemento,
  NULLIF(regexp_replace(TRIM(cep.cep),'[^0-9]', '', 'g'),'') AS cep,
  UPPER(TRIM(BAIRRO.NOME)) AS bairro,
  UPPER(TRIM(CIDADE.NOME)) AS cidade,
  COALESCE(UPPER(TRIM(CIDADE.ESTADO)),'SP') AS estado
FROM CLIEND 
 JOIN Imp_Cliente ON Imp_Cliente.ID = CLIEND.clicodigo::VARCHAR
 JOIN cep ON cep.codigo = cliend.cepcodigo
 LEFT JOIN bairro ON bairro.codigo = cep.bairrocodigo
 LEFT JOIN cidade ON cidade.codigo = cep.CIDADECODIGO
 LEFT JOIN TIPOLOGRADOURO ON TIPOLOGRADOURO.codigo = cep.TIPOLOGRADOUROCODIGO
 LEFT JOIN Imp_Cliente_endereco ON Imp_Cliente_endereco.ID = cliend.codigo::VARCHAR
WHERE imp_cliente_endereco.id IS NULL
  AND IMP_CLIENTE.ID IS NOT NULL; """
  
dependenteCliente = """-- DEPENDENTE DE CLIENTE
/*Cadastro do Dependentecliente [Executar dia 1 e 2] */
INSERT INTO Imp_DependenteCliente(
  ID,
  Imp_ClienteID,
  Nome,
  DataNascimento)
SELECT
  codigo AS ID,
  imp_cliente.id AS imp_clienteid,
  TRIM(clid.nome) AS Nome,
  clid.datanasc AS DataNascimento
FROM clid
JOIN imp_cliente ON Imp_cliente.id = clid.clicodigo::VARCHAR
LEFT JOIN imp_dependentecliente ON imp_dependentecliente.id = clid.codigo::VARCHAR
WHERE imp_dependentecliente.id IS NULL;"""
  
planoRemuneracao = """/* Cadastro do Plano de Remuneração por comissao*/
INSERT INTO imp_planoremu (
  id,
  nome,
  datainicial,
  datafinal,
  ConsiderarDevolucao,
  tipo)
SELECT DISTINCT
  COMISSAO.CODIGO,
  SUBSTRING(UPPER(TRIM(COMISSAO.DESCRICAO)),1,30) AS NOME,
  DATACADASTRO AS DataInicial,
  datafinal::TIMESTAMP AS datafinal,
  FALSE AS ConsiderarDevolucao,
  'A' AS Tipo
FROM 
  COMISSAO
JOIN comissaopro ON comissaopro.COMISSAOCODIGO = COMISSAO.CODIGO 
JOIN Imp_produto ON Imp_produto.id = COMISSAOPRO.PROCODIGO::VARCHAR
WHERE meta = '0' -- comissao campo meta = 0
  AND COMISSAOPRO.percom IS NOT NULL ;

-- Inserindo os itens remuneração por comissao
INSERT INTO imp_planoremucomissao (
  Imp_PlanoRemuID,
  Imp_ProdutoID,
  Comissao)
SELECT DISTINCT ON (imp_produtoid)
  imp_planoremu.id AS imp_planoremuid,
  imp_produto.id AS imp_produtoid,
  COMISSAOPRO.percom AS comissao
FROM COMISSAOPRO
JOIN Imp_produto ON Imp_produto.id = COMISSAOPRO.PROCODIGO::VARCHAR
JOIN imp_planoremu ON imp_planoremu.id = COMISSAOPRO.COMISSAOCODIGO::VARCHAR
WHERE
 COMISSAOPRO.percom IS NOT NULL; 


/* Cadastro do Plano de Remuneração por bonificação*/
INSERT INTO imp_planoremu (
  id,
  nome,
  datainicial,
  datafinal,
  ConsiderarDevolucao,
  tipo)
SELECT DISTINCT
  COMISSAO.CODIGO,
  SUBSTRING(UPPER(TRIM(COMISSAO.DESCRICAO)),1,30) AS NOME,
  DATACADASTRO AS DataInicial,
  datafinal::TIMESTAMP AS datafinal,
  FALSE AS ConsiderarDevolucao,
  'C' AS Tipo
FROM 
  COMISSAO
JOIN comissaopro ON comissaopro.COMISSAOCODIGO = COMISSAO.CODIGO 
JOIN Imp_produto ON Imp_produto.id = COMISSAOPRO.PROCODIGO::VARCHAR
WHERE meta = '0' -- comissao campo meta = 0
  AND COMISSAOPRO.VALOR IS NOT NULL ;

--Inserindo os itens Remuneração por bonificação
INSERT INTO imp_planoremubonificacao (
  Imp_PlanoRemuID,
  Imp_ProdutoID,
  bonificacao)
SELECT DISTINCT
  imp_planoremu.id AS imp_planoremuid,
  imp_produto.id AS imp_produtoid,
  COMISSAOPRO.VALOR AS bonificacao
FROM COMISSAOPRO
JOIN Imp_produto ON Imp_produto.id = COMISSAOPRO.PROCODIGO::VARCHAR
JOIN imp_planoremu ON imp_planoremu.id = COMISSAOPRO.COMISSAOCODIGO::VARCHAR
WHERE
 COMISSAOPRO.VALOR IS NOT NULL;"""
  
prescritores = """/* Cadastro dos Prescritores*/ 
INSERT INTO Imp_Prescritor (
  ID,
  nome,
  numero,
  tipoconselho,
  cidade,
  estado,
  datainscricao)
SELECT DISTINCT ON (crm,conselho,ufconselho)
  med.codigo AS id,
  UPPER(TRIM(med.nome)) AS nome,
  REGEXP_REPLACE(TRIM(med.crm),'[^0-9]', '', 'g')::NUMERIC AS numero,
 (CASE
    WHEN conselho = '1' THEN 'M'
    WHEN conselho = '3' THEN 'V'
    WHEN conselho = '2' THEN 'O'
    WHEN conselho = '4' THEN 'R'
    ELSE 'M'
  END) AS tipoconselho,
  UPPER(TRIM(CIDADE.NOME)) AS CIDADE,
  COALESCE(med.ufconselho) AS estado,
  med.datacadastro AS datainscricao
FROM med
LEFT JOIN CEP ON CEP.CODIGO = MED.CEPCODIGO
LEFT JOIN CIDADE ON CIDADE.CODIGO = CEP.CIDADECODIGO
WHERE ufconselho IS NOT NULL
  AND med.crm IS NOT NULL
  AND ativo = TRUE
  AND med.nome IS NOT NULL;"""
  
crediarioReceber = """/*A tabela vwrec deve ser gerada no servidor SQLSERVER do cliente*/
INSERT INTO imp_crediarioreceber (
  ID,
  Imp_ClienteID,
  Imp_UnidadeNegocioID,
  NumeroDocumento,
  DataEmissao,
  DataVencimento,
  Valor,
  NumeroParcela,
  TotalParcela,
  OBSERVACAO)
WITH CREDIARIOARECEBER AS (
SELECT
  imp_cliente.id AS imp_clienteid,
  imp_unidadenegocio.id AS imp_unidadenegocioid,
  COALESCE(regexp_replace(NULLIF(TRIM(VWREC.documento),''),'[^0-9]', '', 'g'), '0')::BIGINT AS NumeroDocumento,
      (CASE 
      WHEN REC.tppcodigo = 6 AND VWREC.parcela::INTEGER > 1 THEN VWREC.dataemissao + ( (VWREC.PARCELA::INTEGER - 1) || ' months')::INTERVAL 
      ELSE VWREC.dataemissao
      END)::DATE 
  AS dataemissao,
  (CASE 
    WHEN VWREC.datavencimento::DATE <= CURRENT_DATE THEN CURRENT_DATE
  ELSE VWREC.datavencimento
   END)::DATE    AS datavencimento,
  SUM((VWREC.vlrparcela::NUMERIC+VWREC.vlrjuros::NUMERIC)::NUMERIC(15,2)) AS valor,
  COALESCE(NULLIF(TRIM(VWREC.parcela::VARCHAR),'0'),'1')::NUMERIC AS numeroparcela,
  COALESCE(NULLIF(TRIM(VWREC.parcela::VARCHAR),'0'),'1')::NUMERIC AS totalparcela,
  VWREC.dataemissao::DATE AS dataemissao_ORIGINAL,
  VWREC.datavencimento::DATE AS datavencimento_original,
  VWREC.vlrparcela::NUMERIC AS valor_original
FROM VWREC
 JOIN REC ON REC.CODIGO::VARCHAR = VWREC.CODIGO::VARCHAR
 JOIN imp_cliente ON imp_cliente.id = VWREC.clicodigo::VARCHAR
 JOIN imp_unidadenegocio ON imp_unidadenegocio.id = VWREC.loja::VARCHAR
WHERE VWREC.baixado = '0'
  AND REC.tppcodigo IN ('4','6') -- Tipo = 6 convenio // TIPO = 4 crediario
  AND VWREC.CLICODIGO IS NOT NULL 
GROUP BY 1,2,3,4,5,7,8,9,10,11
) 
SELECT 
  numerodocumento||'.'||imp_clienteid||'.'||numeroparcela||'.'||valor AS ID,
  imp_clienteid,
  imp_unidadenegocioid,
  numerodocumento,
  dataemissao,
  datavencimento,
  valor AS valor,
  numeroparcela,
  totalparcela,
  'VALOR ORIGINAL DA PARCELA É R$ '||valor_original|| ' - DATA VENCIMENTO = '|| datavencimento_original||' - DATA DE EMISSAO = '||dataemissao_original AS OBSERVACAO
FROM CREDIARIOARECEBER;"""
  
custo = """--     CUSTO
-- PRECOCUS = preço de custo
-- PRECOCUSM = preço de custo médio com imposto
-- PRECOCUSMC = preço custo médio sem imposto
INSERT INTO Imp_Custo(
  Imp_ProdutoID,
  Imp_UnidadeNegocioID,
  Custo,
  CustoMedio)
SELECT 
  imp_produto.id AS Imp_ProdutoID,
  imp_unidadenegocio.id AS Imp_UnidadeNegocioID,
  proloja.precocus::NUMERIC(15,2) AS custo,
  COALESCE(NULLIF(proloja.PRECOCUSM::NUMERIC(15,2),0),proloja.precocus::NUMERIC(15,2)) AS customedio
FROM proloja
JOIN imp_produto ON imp_produto.id = proloja.procodigo::VARCHAR
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = proloja.lojacodigo::VARCHAR
WHERE proloja.precocus IS NOT NULL
  AND proloja.precocus::NUMERIC(15,2) > 0;"""
  
estoque = """-- ESTOQUE
-- Na tabela de Estoque a coluna proestoque.lote = 0 é os produtos não controlados
INSERT INTO Imp_Estoque (
  Imp_ProdutoID,
  Imp_UnidadeNegocioID,
  Estoque)
SELECT 
  Imp_Produto.id AS imp_produtoid,
  imp_unidadenegocio.id AS Imp_UnidadeNegocioID,
  SUM(proestoque.qtde) AS Estoque
FROM proestoque 
  JOIN Imp_Produto ON Imp_Produto.id = proestoque.procodigo::VARCHAR
  JOIN imp_unidadenegocio ON imp_unidadenegocio.id = proestoque.lojacodigo::VARCHAR
WHERE proestoque.qtde > 0
GROUP BY 1,2
ORDER BY IMP_PRODUTO.ID::NUMERIC """
  
contasAPagar = """-- CONTAS A PAGAR
INSERT INTO Imp_ContaPagar (
  ID,
  Imp_UnidadeNegocioID,
  Imp_FornecedorID,
  Descricao,  
  NumeroDocumento,
  DataEmissao,
  DataVencimento,
  ValorDocumento,
  NumeroParcela,  
  Desconto,
  Acrescimo,
  Observacao,
  TotalParcela)
SELECT 
  PAG.CODIGO AS ID, 
  imp_unidadenegocio.id AS imp_unidadenegocioid,
  Imp_Fornecedor.ID AS imp_fornecedorid,
  SUBSTRING(FRN.NOME,1,50) AS Descricao, 
  SUBSTRING(PAG.DOCUMENTO,1 , 20) AS NumeroDocumento, 
  PAG.DATAEMISSAO::TIMESTAMP AS DataEmissao,
  PAG.DATAVENCIMENTO::TIMESTAMP AS DataVencimento,
  PAG.VLRPARCELA AS ValorDocumento,
  '1' AS NumeroParcela,
  COALESCE(pag.vlrdesconto,0) AS Desconto,
  COALESCE(PAG.VLRJUROS,0) + COALESCE(PAG.VLRACRESCIMO,0) AS Acrescimo,
  NULLIF(SUBSTRING(UPPER(TRIM(PAG.OBS)),250),'') AS  Observacao,
  PAG.vlrparcela - COALESCE(pag.vlrdesconto,0) + COALESCE(PAG.VLRJUROS,0) + COALESCE(PAG.VLRACRESCIMO,0) AS TotalParcela
FROM PAG
JOIN FRN ON FRN.CODIGO = PAG.frncodigo 
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = pag.loja::VARCHAR
JOIN Imp_Fornecedor ON  Imp_Fornecedor.ID = FRN.CODIGO::VARCHAR
WHERE PAG.DATABAIXA IS NULL
  AND PAG.VLRPARCELA IS NOT NULL
  AND PAG.DOCUMENTO IS NOT NULL
  AND PAG.TAXACARTAO = '0' -- A TAXA CARTAO = 0 É UTILIZADA PARA OS CARTÕES
ORDER BY DOCUMENTO;"""
  
demanda = """-- DEMANDA 
INSERT INTO imp_historicovenda(
  imp_produtoid,
  imp_unidadenegocioid,
  DATA,
  quantidade)
SELECT 
  imp_produto.id AS imp_produtoid,
  imp_unidadenegocio.id AS imp_unidadenegocioid,
  (sai.datacadastro::DATE)::TIMESTAMP AS DATA,
  SUM(qtde) AS quantidade
FROM saii  
JOIN sai ON sai.codigo = saii.saicodigo
JOIN imp_produto ON imp_produto.id = SAII.procodigo::VARCHAR
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = SAII.loja::VARCHAR
WHERE sai.datacadastro > CURRENT_DATE - INTERVAL '180' DAY  -- Inserido a datacadastro, pois em alguns casos o cliente pode vender sem valor fiscal, e com isso o campo "datahoracupom" fica nulo
  AND sai.STATUS = 2 -- 2 É VENDA CONFIRMADA - 1 É VENDA PENDENTE - 3 É VENDA CANCELADA       
GROUP BY 1,2,3;"""
