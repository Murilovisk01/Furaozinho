# -*- coding: utf-8 -*-
tmp_produto = """DROP TABLE IF EXISTS tmp_produto;
CREATE TABLE tmp_produto (produtoid VARCHAR(100), PRIMARY KEY (produtoid));

INSERT INTO tmp_produto 
SELECT DISTINCT
  produto.pro_cod
FROM produto 
LEFT JOIN itens_venda ON produto.pro_cod = itens_venda.pro_cod
LEFT JOIN venda ON (venda.ter_cod = itens_venda.ter_cod AND venda.ven_cod = itens_venda.ven_cod)
WHERE produto.pro_status = 'A'
  AND (produto.pro_saldo > 0 OR venda.ven_dat > NOW() - INTERVAL '24' MONTH);"""

usuario = """INSERT INTO imp_usuario (
  id,
  login,
  senha,
  apelido)
SELECT
  fun_cod AS id,
  SUBSTRING(UPPER(COALESCE(NULLIF(TRIM(fun_login),''),fun_nome)),0,100) AS login,
  '123' AS senha,
  SUBSTRING(UPPER(COALESCE(NULLIF(TRIM(fun_nome),''),fun_login)),0,30) AS apelido
FROM funcionario
LEFT JOIN imp_usuario ON funcionario.fun_cod::VARCHAR = imp_usuario.id
WHERE imp_usuario.id IS NULL
  AND fun_status = 'S';"""

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
  Numero,
  Cep,
  Bairro,
  Cidade,
  Estado,
  Telefone)
SELECT
  emp_cod AS ID,
  LPAD(emp_cod::VARCHAR, 2, '0') AS Codigo,
  UPPER(TRIM(emp_nomefant)) AS Nome,
  UPPER(TRIM(emp_nomefant)) AS NomeFantasia,
  UPPER(TRIM(emp_razsocial)) AS RazaoSocial,
  regexp_replace(emp_cnpj, '[^0-9]', '', 'g') AS CNPJ,
  regexp_replace(emp_ie, '[^0-9]', '', 'g') AS InscricaoEstadual,
  UPPER(TRIM(emp_uf)) AS EstadoInscricaoEstadual,
  UPPER(TRIM(emp_end)) AS Endereco,
  emp_num AS Numero,
  emp_cep AS Cep,
  UPPER(TRIM(emp_bai)) AS Bairro,
  UPPER(TRIM(emp_cid)) AS Cidade,
  UPPER(TRIM(emp_uf)) AS Estado,
  COALESCE(emp_tel1, emp_tel2) AS Telefone
FROM empresa
LEFT JOIN imp_unidadenegocio ON imp_unidadenegocio.id = empresa.emp_cod::VARCHAR
WHERE imp_unidadenegocio.id IS NULL;"""

grupoRemarcacao = """select"""

principioAtivo = """INSERT INTO imp_principioativo (
  ID,
  Nome)
SELECT DISTINCT
  UPPER(SUBSTRING(TRIM(pro_principio_ativo),1,100)) AS id,
  SUBSTRING(UPPER(TRIM(pro_principio_ativo)),0,130) AS nome
FROM produto
LEFT JOIN imp_principioativo ON SUBSTRING(TRIM(pro_principio_ativo),1,100) = imp_principioativo.id
WHERE COALESCE(TRIM(pro_principio_ativo),'') <> '' 
  AND imp_principioativo.id IS NULL;"""

fabricanteNaoInformado = """--FABRICANTE NÃO INFORMADO
INSERT INTO imp_fabricante (id, nome) VALUES('NAO INFORMADO', 'NÃO INFORMADO');
 """

fabricante = """--FABRICANTES 
INSERT INTO imp_fabricante(
  id,
  nome,
  tipo,
  observacao,
  telefone,
  telefone2,
  email,
  cnpj,
  inscricaoestadual,
  estadoinscricaoestadual)
SELECT DISTINCT
  laboratorio.lab_cod AS id,
  TRIM(UPPER(lab_nome)) AS nome,
  'J' AS tipo,
  NULLIF(TRIM(lab_obs),'') AS observacao,
  NULLIF(TRIM(lab_tel1),'') AS telefone,
  NULLIF(TRIM(lab_tel2),'') AS telefone2,
  NULLIF(TRIM(lab_email),'') AS email,
  NULLIF(TRIM(lab_cnpj),'') AS cnpj,
  NULLIF(TRIM(lab_ie),'') AS inscricaoestadual,
  NULLIF(TRIM(lab_uf),'') AS estadoinscricaoestadual
FROM laboratorio
JOIN produto ON laboratorio.lab_cod = produto.lab_cod
LEFT JOIN imp_fabricante ON laboratorio.lab_cod::VARCHAR = imp_fabricante.id
WHERE imp_fabricante.id IS NULL;"""

classficacao = """-- CLASSIFICAÇÃO RAIZ
INSERT INTO Imp_Classificacao (id, nome, profundidade, principal) VALUES ('RAIZ', 'PRINCIPAL', 0, TRUE);
 
-- PARA PRODUTOS SEM CLASSIFICAÇÃO
INSERT INTO Imp_Classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) VALUES ('RAIZ.NÃOINFORMADA', 'NÃO INFORMADA', 1, TRUE, 'RAIZ');
 
-- PROFUNDIDADE 1
INSERT INTO imp_classificacao (
  id,
  nome,
  profundidade,
  principal,
  imp_classificacaopaiid)
SELECT 
  sec_descr AS ID,
  sec_descr AS Nome,
  1 AS Profundidade,
  TRUE AS Principal,
  'RAIZ' AS imp_classificacaopaiid
FROM secao
LEFT JOIN imp_classificacao ON secao.sec_descr = imp_classificacao.id
WHERE imp_classificacao.id IS NULL;"""

produto = """-- Produtos
INSERT INTO imp_produto (
  id,
  descricao,
  imp_fabricanteid,
  codigobarras,
  tipoaliquota,
  valoraliquota,
  CestID,
  PerfilPISSnID,
  PerfilCofinsSnID,
  PerfilPISID,
  PerfilCofinsID,
  precoreferencial,
  precovenda,
  listapis,
  listadcb,
  tipopreco,
  registroms,
  codigoncm,
  imp_principioativoid,
  imp_classificacaoid,
  tipo)
SELECT DISTINCT ON (produto.pro_cod)
  produto.pro_cod AS id,
  TRIM(pro_descr) AS descricao,
  COALESCE(imp_fabricante.id,'NAO INFORMADO') AS imp_fabricanteid,
  TRIM(pro_codbar) AS codigobarras, 
  (CASE
    WHEN tributos.tri_cod = 'FF' THEN 'A'
    WHEN tributos.tri_cod = 'II' THEN 'B'
    WHEN tributos.tri_cod = 'NN' THEN 'C'
    WHEN tributos.tri_cod LIKE '%T' THEN 'D'
  END) AS tipoaliquota,
  (CASE 
    WHEN tributos.tri_cod LIKE '%T' AND tributos.tri_percentual > 0 THEN tributos.tri_percentual 
    ELSE NULL
  END) AS valoraliquota,
  imp_cest.id AS cestid,
  PerfilPISSn.id AS PerfilPISSnID,
  perfilcofinssn.ID AS PerfilCofinsSID,
  PerfilPIS.ID AS PerfilPISID,
  PerfilCofins.ID AS PerfilCofinsID,
  COALESCE(produto.pro_custo, 1.0) AS precoreferencial,  --OBS: O que o InfoMaster chama de "Custo" é na verdade o "PrecoReferencial" 
  COALESCE(produto.pro_preco, 1.0) AS precovenda,
  (CASE pro_lista
    WHEN '+' THEN 'P' 
    WHEN '-' THEN 'N'
    WHEN 'N' THEN 'U'
    ELSE 'A'
  END) AS listapis, --OBS: o tipo "L=Liberado" não faz sentido
    (CASE
  WHEN TRIM(dcb.DCB_PORTARIA) = 'A-1' THEN 'A'
  WHEN TRIM(dcb.DCB_PORTARIA) = 'A-2' THEN 'B'
  WHEN TRIM(dcb.DCB_PORTARIA) = 'A-3' THEN 'C'
  WHEN TRIM(dcb.DCB_PORTARIA) = 'B-1' THEN 'D'
  WHEN TRIM(dcb.DCB_PORTARIA) = 'B-2' THEN 'E'
  WHEN TRIM(dcb.DCB_PORTARIA) = 'C-1' THEN 'F'
  WHEN TRIM(dcb.DCB_PORTARIA) = 'C-2' THEN 'G'
  WHEN TRIM(dcb.DCB_PORTARIA) = 'C-3' THEN 'H'
  WHEN TRIM(dcb.DCB_PORTARIA) = 'C-4' THEN 'I'
  WHEN TRIM(dcb.DCB_PORTARIA) = 'C-5' THEN 'J'
  WHEN TRIM(dcb.DCB_PORTARIA) = 'D-1' THEN 'K'
  WHEN TRIM(dcb.DCB_PORTARIA) = 'D-2' THEN 'L'
  WHEN TRIM(dcb.DCB_PORTARIA) = 'A-M' THEN 'M'
  ELSE NULL
  END) AS listadcb,
  'L' AS tipopreco, 
  (CASE 
    WHEN pro_codreg ~ '^[0-9]{13}$' THEN pro_codreg 
    ELSE NULL
  END) AS registroms,
  NULLIF(TRIM(pro_cod_ncm), '') AS codigoncm,
  imp_principioativo.ID AS imp_principioativoid,
  COALESCE(imp_classificacao.id, 'RAIZ.NÃOINFORMADA') AS imp_classificacaoid,
  (CASE 
    WHEN pro_cod_serv IS NOT NULL THEN 'S' 
    ELSE 'M'
  END) AS tipo
FROM produto
JOIN tmp_produto ON tmp_produto.produtoid = produto.pro_cod::VARCHAR
JOIN tributos ON produto.tri_cod = tributos.tri_cod
LEFT JOIN imp_fabricante ON imp_fabricante.id = produto.lab_cod::VARCHAR
LEFT JOIN imp_principioativo ON imp_principioativo.id = SUBSTRING(TRIM(pro_principio_ativo),1,100)
LEFT JOIN imp_classificacao ON imp_classificacao.id = produto.sec_descr::VARCHAR
LEFT JOIN cest ON cest.cest_ncm = NULLIF(TRIM(pro_cod_ncm), '')
LEFT JOIN imp_cest ON TRIM(imp_cest.codigo) = TRIM(cest.cest_cod)
LEFT JOIN perfilpis perfilpissn ON perfilpissn.piscst = produto.pro_cst_pis AND perfilpissn.tipocontribuinte = 'B'
LEFT JOIN perfilcofins perfilcofinssn ON perfilcofinssn.cofinscst = produto.pro_cst_cofins AND perfilcofinssn.tipocontribuinte = 'B'
LEFT JOIN perfilpis ON perfilpis.piscst = produto.pro_cst_pis AND perfilpis.tipocontribuinte = 'A'
LEFT JOIN perfilcofins ON perfilcofins.cofinscst = produto.pro_cst_cofins AND perfilcofins.tipocontribuinte = 'A'
LEFT JOIN dcb ON dcb.dcb_cod = produto.dcb_cod
LEFT JOIN imp_produto ON produto.pro_cod::VARCHAR = imp_produto.id
WHERE imp_produto.id IS NULL 
  AND produto.pro_status = 'A';
 """

produtoMae = """ 
--EMBALAGENS MÃE
INSERT INTO imp_produto (
  id,
  descricao,
  imp_fabricanteid,
  codigobarras,
  tipoaliquota,
  valoraliquota,
  precoreferencial,
  precovenda,
  listapis,
  tipopreco,
  registroms,
  codigoncm,
  imp_principioativoid,
  imp_classificacaoid,
  tipo,
  IDProdutoContido,
  QuantidadeEmbalagem,
  DataHoraInclusao)
SELECT DISTINCT
  '-' || produto.pro_cod AS id,
  TRIM(pro_descr) AS descricao,
  COALESCE(imp_fabricante.id,'NAO INFORMADO') AS imp_fabricanteid,
  TRIM(pro_codbar) AS codigobarras, 
  (CASE
    WHEN tributos.tri_cod = 'FF' THEN 'A'
    WHEN tributos.tri_cod = 'II' THEN 'B'
    WHEN tributos.tri_cod = 'NN' THEN 'C'
    WHEN tributos.tri_cod LIKE '%T' THEN 'D'
  END) AS tipoaliquota,
  (CASE 
    WHEN tributos.tri_cod LIKE '%T' AND tributos.tri_percentual > 0 THEN tributos.tri_percentual 
    ELSE NULL
  END) AS valoraliquota,
  COALESCE(produto.pro_custo, 1.0) AS precoreferencial,  --OBS: O que o InfoMaster chama de "Custo" é na verdade o "PrecoReferencial" 
  COALESCE(produto.pro_preco, 1.0) AS precovenda,
  (CASE pro_lista
    WHEN '+' THEN 'P' 
    WHEN '-' THEN 'N'
    WHEN 'N' THEN 'U'
    ELSE 'A'
  END) AS listapis, --OBS: o tipo "L=Liberado" não faz sentido
  'L' AS tipopreco, 
  (CASE 
    WHEN pro_codreg ~ '^[0-9]{13}$' THEN pro_codreg 
    ELSE NULL
  END) AS registroms,
  NULLIF(TRIM(pro_cod_ncm), '') AS codigoncm,
  imp_principioativo.ID AS imp_principioativoid,
  COALESCE(imp_classificacao.id, 'RAIZ.NÃOINFORMADA') AS imp_classificacaoid,
  (CASE 
    WHEN pro_cod_serv IS NOT NULL THEN 'S' 
    ELSE 'M'
  END) AS tipo,
  produto.pro_cod AS IDProdutoContido,
  pro_fracao AS QuantidadeEmbalagem,
  pro_dtcad AS DataHoraInclusao
FROM produto
JOIN tmp_produto ON tmp_produto.produtoid = produto.pro_cod::VARCHAR
JOIN tributos ON produto.tri_cod = tributos.tri_cod
LEFT JOIN imp_fabricante ON imp_fabricante.id = produto.lab_cod::VARCHAR
LEFT JOIN imp_principioativo ON imp_principioativo.id = SUBSTRING(TRIM(pro_principio_ativo),1,100)
LEFT JOIN imp_classificacao ON imp_classificacao.id = produto.sec_descr::VARCHAR
JOIN imp_produto ON produto.pro_cod::VARCHAR = imp_produto.id
LEFT JOIN imp_produto ip ON '-' || produto.pro_cod::VARCHAR = ip.id
WHERE ip.id IS NULL
  AND produto.pro_status = 'A'
  AND produto.pro_fracao > 1;"""

codigoDeBarrasAdicional = """select"""

duploPerfilImcs = """select"""

impostoLucroPresumido = """-- LUCRO REAL - ||ATENÇÃO REALIZAR A VALIDAÇÃO|| 
INSERT INTO imp_icmsproduto(
  imp_produtoid,
  perfilicmsid,
  estado)
WITH icmsproduto AS (
SELECT DISTINCT
  imp_produto.id AS imp_produtoid,
  perfilicms.id AS perfilicmssnid,
  imp_unidadenegocio.estado AS estado
FROM perfilicms 
JOIN produto ON SUBSTRING(produto.pro_st_icms,1,2) = perfilicms.icmscst
JOIN imp_produto ON imp_produto.id = produto.pro_cod::VARCHAR, imp_unidadenegocio
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
JOIN produto ON produto.pro_st_icms = perfilicms.icmssncso
JOIN imp_produto ON imp_produto.id = produto.pro_cod::VARCHAR, imp_unidadenegocio
)
SELECT DISTINCT ON (icmsproduto.imp_produtoid, icmsproduto.estado)
  icmsproduto.*
FROM icmsproduto
LEFT JOIN imp_icmsproduto ON imp_icmsproduto.imp_produtoid = icmsproduto.imp_produtoid AND imp_icmsproduto.estado = icmsproduto.estado
WHERE imp_icmsproduto.imp_produtoid IS NULL;"""

fornencedor = """--FORNECEDORES
INSERT INTO imp_fornecedor (
  id,
  nome,
  tipo,
  observacao,
  telefone,
  telefone2,
  email,
  razaosocial,
  cnpj,
  inscricaoestadual,
  estadoinscricaoestadual)
SELECT
  COALESCE(for_cod,'-1') AS id,
  COALESCE(UPPER(TRIM(for_nome)),'NAO INFORMADO') AS nome,
  'J'AS tipo,
  NULLIF(TRIM(for_obs),'') AS observacao,
  NULLIF(TRIM(for_tel1),'') AS telefone,
  NULLIF(TRIM(for_tel2),'') AS telefone2,
  NULLIF(TRIM(for_email),'') AS email,
  COALESCE(UPPER(TRIM(for_nome)),'NAO INFORMADO') AS razaosocial,
  NULLIF(TRIM(for_cnpj),'') AS cnpj,
  NULLIF(TRIM(for_ie),'') AS inscricaoestadual,
  COALESCE(NULLIF(TRIM(for_uf),''),'SP') AS estadoinscricaoestadual
FROM fornecedor
LEFT JOIN imp_fornecedor ON fornecedor.for_cod::VARCHAR = imp_fornecedor.id
WHERE imp_fornecedor.id IS NULL;

--ENDEREÇOS DO FORNECEDOR
INSERT INTO imp_fornecedor_endereco(
  id,
  imp_fornecedorid,
  endereco,
  numero,
  complemento,
  cep,
  bairro,
  cidade,
  estado)
SELECT
  for_cod AS id,
  COALESCE(imp_fornecedor.id,'-1') AS imp_fornecedorid,
  UPPER(TRIM(for_end)) AS endereco,
  (CASE
    WHEN for_num ~ '^[0-9]' THEN regexp_replace(for_num, '[^0-9]', '', 'g')
    ELSE 'N/I'
  END) AS numero,
  UPPER(NULLIF(TRIM(for_con),'')) AS complemento,
  UPPER(NULLIF(TRIM(for_cep),'')) AS cep,
  UPPER(COALESCE(NULLIF(TRIM(for_bai),''),'NAO INFORMADO')) AS bairro,
  UPPER(NULLIF(TRIM(for_cid),'')) AS cidade,
  NULLIF(TRIM(for_uf),'') AS estado
FROM fornecedor
LEFT JOIN imp_fornecedor_endereco ON fornecedor.for_cod::VARCHAR = imp_fornecedor_endereco.id
LEFT JOIN imp_fornecedor ON fornecedor.for_cod::VARCHAR = imp_fornecedor.id
WHERE imp_fornecedor_endereco.id IS NULL 
  AND NULLIF(TRIM(for_end),'') IS NOT NULL;"""

planoPagamento = """INSERT INTO imp_planopagamento(id,nome,minparcela,maxparcela,tipointervaloentrada,intervaloentrada,tipointervaloparcela,intervaloparcela) VALUES ('-1','PARTICULAR',1,1,'D','1','M','1');"""

cadernoDeOferta = """--INSERINDO CADERNO DE OFERTA
INSERT INTO imp_cadernooferta (id, nome, DataHoraInicial, DataHoraFinal) VALUES ('DESCONTO', 'DESCONTO', now(), now() + INTERVAL '1 year');

--INSERINDO ITENS CADERNO OFERTAS DO TIPO PREÇO
INSERT INTO imp_itemcadernooferta (
  imp_cadernoofertaid,
  imp_produtoid,
  tipooferta,
  precooferta)
SELECT
  imp_cadernooferta.id AS imp_cadernoofertaid,
  imp_produto.id AS imp_produtoid,
  'P' AS tipooferta,
  produto.pro_valor_desc_vista
FROM produto 
JOIN imp_produto ON imp_produto.id = produto.pro_cod::VARCHAR
JOIN imp_cadernooferta ON imp_cadernooferta.id = 'DESCONTO'
WHERE pro_preco <> pro_valor_desc_vista
AND pro_valor_desc_vista > 0;

--INSERINDO CADERNO DE OFERTA da tabela "pro_promo_v"
INSERT INTO imp_cadernooferta (id, nome, DataHoraInicial, DataHoraFinal) VALUES ('DESCONTO_VENDA', 'DESCONTO_VENDA', now(), now() + INTERVAL '1 year');


--INSERINDO ITENS CADERNO OFERTAS DO TIPO PREÇO
INSERT INTO imp_itemcadernooferta (
  imp_cadernoofertaid,
  imp_produtoid,
  tipooferta,
  precooferta)
SELECT
  imp_cadernooferta.id AS imp_cadernoofertaid,
  imp_produto.id AS imp_produtoid,
  'P' AS tipooferta,
  produto.pro_promo_v
FROM produto 
JOIN imp_produto ON imp_produto.id = produto.pro_cod::VARCHAR
JOIN imp_cadernooferta ON imp_cadernooferta.id = 'DESCONTO_VENDA'
WHERE pro_preco <> pro_promo_v
AND pro_promo_v > 0;

--INSERINDO CADERNO DE OFERTA da tabela "PRO_A_PRAZO"
INSERT INTO imp_cadernooferta (id, nome, DataHoraInicial, DataHoraFinal) VALUES ('DESCONTO_A_PRAZO', 'DESCONTO_A_PRAZO', now(), now() + INTERVAL '1 year');

--INSERINDO ITENS CADERNO OFERTAS DO TIPO PREÇO
INSERT INTO imp_itemcadernooferta (
  imp_cadernoofertaid,
  imp_produtoid,
  tipooferta,
  precooferta)
SELECT
  imp_cadernooferta.id AS imp_cadernoofertaid,
  imp_produto.id AS imp_produtoid,
  'P' AS tipooferta,
  produto.PRO_A_PRAZO
FROM produto 
JOIN imp_produto ON imp_produto.id = produto.pro_cod::VARCHAR
JOIN imp_cadernooferta ON imp_cadernooferta.id = 'DESCONTO_A_PRAZO'
WHERE pro_preco <> PRO_A_PRAZO
AND PRO_A_PRAZO > 0;
"""

cadernoDeOfertaQuantidade = """select"""

cadernoDeOfertaLevePague = """select"""

cadernoDeOfertaClassificacao = """select"""

cadernoDeOfertaUnidade = """select"""

crediario = """--CREDIÁRIO PARTICULAR
INSERT INTO Imp_Crediario (ID, NomeCrediario, LimitePadraoCliente, Imp_PlanoPagamentoID) VALUES ('0', 'PARTICULAR', 0, '-1');

--CREDIARIOS
INSERT INTO imp_crediario (
  ID,
  nomecrediario,
  imp_planopagamentoid,
  limitepadraocliente,
  taxajuros,
  toleranciaatraso,
  toleranciajuros,
  toleranciamulta)
SELECT DISTINCT
  convenio.con_cod AS ID,
  UPPER(TRIM(con_nome)) AS nomecrediario,
  '-1' AS imp_planopagamentoid,
  0.00 AS limitepadraocliente,
  COALESCE(con_juros,0.00) AS taxajuros,
  COALESCE(con_dias_bloqueio,0) AS toleranciaatraso,
  COALESCE(con_ndiatolera,0) AS toleranciajuros,
  COALESCE(con_ndiatolera,0) AS toleranciamulta
FROM convenio
JOIN cliente ON convenio.con_cod = cliente.con_cod
LEFT JOIN imp_crediario ON convenio.con_cod::VARCHAR = imp_crediario.id
WHERE imp_crediario.id IS NULL;"""

cliente = """
--CLIENTES

INSERT INTO imp_cliente(
  ID,
  imp_crediarioid,
  dataaberturacrediario,
  tipolimite,
  limite,
  mensagemvenda,
  nome,
  tipo,
  observacao,
  telefone,
  telefone2,
  email,
  cpf,
  datanascimento,
  identidade,
  siglaorgaoidentidade,
  estadoidentidade,
  sexo,
  cnpj)
SELECT
  cliente.cli_cod AS ID,
  COALESCE(imp_crediario.id,'0') AS imp_crediarioid,
  cli_cad AS dataaberturacrediario,
  (CASE
    WHEN cli_lim > 0 THEN 'P'
    ELSE 'C'
  END) AS tipolimite,
  COALESCE(cli_lim,0.00) AS limite,
  NULLIF(UPPER(TRIM(cli_obs)),'') AS mensagemvenda,
  UPPER(TRIM(cli_nome)) AS nome,
  COALESCE(cli_pessoa,'F') AS tipo,
  NULLIF(UPPER(TRIM(cli_obs)),'') AS observacao,
  NULLIF(regexp_replace(TRIM(cli_tel1),'[^0-9]', '', 'g'),'') AS telefone,
  NULLIF(regexp_replace(TRIM(cli_tel2),'[^0-9]', '', 'g'),'') AS telefone2,
  NULLIF(TRIM(cli_email),'') AS email,
  (CASE
    WHEN LENGTH(cli_cpf) = 11 THEN regexp_replace(NULLIF(TRIM(cli_cpf),''),'[^0-9]', '', 'g')
  END) AS cpf,
  cli_nasc AS datanascimento,
  SUBSTRING(NULLIF(cli_rg,'ISENTO'), 1, 15) AS identidade,
  SUBSTRING(NULLIF(TRIM(cli_oe_rg),''), 1, 10) AS siglaorgaoidentidade,
  NULLIF(TRIM(cli_uf_rg),'') AS estadoidentidade,
  (CASE
    WHEN substr(cli_sexo,1,1) = 'M' THEN 'M'
    WHEN substr(cli_sexo,1,1) = 'F' THEN 'F'
    ELSE 'N'
  END) AS sexo,
  (CASE
    WHEN LENGTH(TRIM(cli_cpf)) = 14 THEN TRIM(cli_cpf)
    ELSE NULL
  END) AS cnpj
FROM cliente
LEFT JOIN imp_cliente ON cliente.cli_cod::VARCHAR = imp_cliente.id
LEFT JOIN imp_crediario ON imp_crediario.id = cliente.con_cod::VARCHAR
WHERE imp_cliente.id IS NULL;

--ENDEREÇOS DOS CLIENTES
INSERT INTO imp_cliente_endereco (
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
  cli_cod || '.' || enc_cod AS id,
  cli_cod AS imp_clienteid,
  SUBSTRING(UPPER(TRIM(enc_end)),1,70) AS endereco,
  COALESCE(NULLIF(SUBSTRING(TRIM(enc_num),1,6),''), 'N/A') AS numero,
  NULLIF(TRIM(enc_con),'') AS complemento,
  NULLIF(TRIM(enc_cep),'') AS cep,
  COALESCE(NULLIF(TRIM(enc_bai),''), 'BAIRRO NÃO INFORMADO') AS bairro,
  COALESCE(NULLIF(UPPER(TRIM(enc_cid)),''), 'CIDADE NÃO INFORMADA') AS cidade,
  SUBSTRING(COALESCE(NULLIF(UPPER(TRIM(enc_UF)),''), 'SP'),1,2) AS estado
FROM enderecos_cli
JOIN imp_cliente ON enderecos_cli.cli_cod::VARCHAR = imp_cliente.id
LEFT JOIN imp_cliente_endereco ON (cli_cod || '.' || enc_cod) = imp_cliente_endereco.id
WHERE imp_cliente_endereco.id IS NULL 
  AND enc_end IS NOT NULL;"""

dependenteCliente = """select"""

planoRemuneracao = """select"""

prescritores = """/* Cadastro dos Prescritores*/ 
INSERT INTO Imp_Prescritor (
  ID,
  nome,
  numero,
  tipoconselho,
  cidade,
  estado)
SELECT 
  med_cod AS id,
  COALESCE(NULLIF(TRIM(UPPER(REPLACE(med_nome,'''',''))),''),'NAO INFORMADO') AS nome,
  TRIM(REPLACE(REPLACE(REPLACE(medico.med_crm,'.',''),'-',''),' ',''),'')::bigint AS numero,
   (CASE
    WHEN med_consprof = 'CRM' THEN 'M'
    WHEN med_consprof = 'CRMV' THEN 'V'
    WHEN med_consprof = 'CRO' THEN 'O'
    WHEN med_consprof = 'COREN' THEN 'C'
    WHEN med_consprof = 'RMS' THEN 'R'
    ELSE 'M'
  END) AS tipoconselho,
  NULLIF(TRIM(UPPER(med_cid::varchar)),'') AS cidade,
  TRIM(UPPER(med_ufcrm)) as estado
FROM MEDICO
WHERE NULLIF(TRIM(REPLACE(REPLACE(REPLACE(medico.med_crm,'.',''),'-',''),' ','')),'') IS NOT NULL and 
	TRIM(REGEXP_REPLACE(medico.med_crm, '[^0-9]', '', 'g')) <> '';"""

crediarioReceber = """INSERT INTO imp_crediarioreceber (
  id,
  imp_clienteid,
  numerodocumento,
  dataemissao,
  datavencimento,
  valor,
  imp_unidadenegocioid,
  numeroparcela,
  totalparcela,
  taxajuros,
  observacao)
SELECT
  titulo.tit_cod||'.'||tit_parcela::VARCHAR AS id,
  imp_cliente.id AS imp_clienteid,
  titulo.tit_cod AS numerodocumento,
  tit_data AS dataemissao,
  tit_vencimento AS datavencimento,
  tit_valor - COALESCE(titulo_pgt.valorpago, 0) AS valor,
  imp_unidadenegocio.id AS imp_unidadenegocioid,
  tit_parcela AS numeroparcela,
  tit_parcela AS totalparcela,
  tit_juros AS taxajuros,
  NULLIF(TRIM(tit_obs),'') AS observacao
FROM titulo
JOIN imp_cliente ON titulo.cli_cod::VARCHAR = imp_cliente.id
LEFT JOIN (SELECT tit_cod, SUM(pgt_valor) AS valorpago FROM pagamento_titulo GROUP BY 1) AS titulo_pgt ON titulo.tit_cod = titulo_pgt.tit_cod
LEFT JOIN imp_crediarioreceber ON titulo.tit_cod::VARCHAR = imp_crediarioreceber.id ,
empresa
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = empresa.emp_cod::VARCHAR
WHERE imp_crediarioreceber.id IS NULL
  AND titulo.tit_status = 'R'
  AND empresa.emp_cod = 1 --OBS: Como os títulos não estão vinculados às Empresas estou travando aqui para vincular tudo com a primeira Empresa
  AND tit_valor - COALESCE(titulo_pgt.valorpago, 0) > 0;"""

custo = """INSERT INTO imp_custo (
  imp_produtoid,
  imp_unidadenegocioid,
  custo,
  customedio)
SELECT
  imp_produto.id AS imp_produtoid, 
  imp_unidadenegocio.id AS imp_unidadenegocioid,
  produto.pro_custo AS custo,
  COALESCE(NULLIF(produto.pro_custo_medio, 0), produto.pro_custo) AS customedio
FROM empresa
JOIN produto ON (TRUE)
JOIN imp_produto ON produto.pro_cod::VARCHAR = imp_produto.id
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = empresa.emp_cod::VARCHAR
LEFT JOIN imp_custo ON produto.pro_cod::VARCHAR = imp_custo.imp_produtoid AND empresa.emp_cod::VARCHAR = imp_custo.imp_unidadenegocioid
WHERE imp_custo.imp_produtoid IS NULL
  AND produto.pro_custo > 0
  AND produto.pro_custo_medio > 0
  AND empresa.emp_cod = 1; --OBS: Como o estoque está na tabela de Produto, assumo então que o InfoMaster não suporta multi-lojas, e por isso estou travando aqui para pegar o estoque da primeira Empresa"""

estoque = """INSERT INTO imp_estoque (
  imp_produtoid,
  imp_unidadenegocioid,
  estoque)
SELECT
  imp_produto.id AS imp_produtoid, 
  imp_unidadenegocio.id AS imp_unidadenegocioid,
  produto.pro_saldo AS estoque
FROM empresa
JOIN produto ON (TRUE)
JOIN imp_produto ON produto.pro_cod::VARCHAR = imp_produto.id
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = empresa.emp_cod::VARCHAR
LEFT JOIN imp_estoque ON produto.pro_cod::VARCHAR = imp_estoque.imp_produtoid AND empresa.emp_cod::VARCHAR = imp_estoque.imp_unidadenegocioid
WHERE imp_estoque.imp_produtoid IS NULL
  AND produto.pro_saldo > 0 
  AND empresa.emp_cod = 1; --OBS: Como o estoque está na tabela de Produto, assumo então que o InfoMaster não suporta multi-lojas, e por isso estou travando aqui para pegar o estoque da primeira Empresa"""

contasAPagar = """INSERT INTO imp_contapagar (
  id,
  imp_unidadenegocioid,
  imp_fornecedorid,
  descricao,
  numerodocumento,
  dataemissao,
  datavencimento,
  valordocumento,
  observacao,
  numeroparcela,
  totalparcela)
SELECT 
  cpg_cod || '-' || cpg_parcela AS id,
  imp_unidadenegocio.id AS imp_unidadenegocioid,
  imp_fornecedor.id AS imp_fornecedorid,
  NULLIF(TRIM(conta.cnt_descr),'') AS descricao,
  NULLIF(TRIM(cpg_doc),'') AS numerodocumento,
  cpg_data_emissao AS dataemissao,
  cpg_data_ven AS datavencimento,
  cpg_valor AS valordocumento,
  NULLIF(TRIM(cpg_obs),'') AS observacao,
  cpg_parcela AS numeroparcela,
  cpg_qtde_parc AS totalparcela
FROM empresa
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = empresa.emp_cod::VARCHAR,
contas_pagar
JOIN imp_fornecedor ON imp_fornecedor.id = contas_pagar.for_cod::VARCHAR
LEFT JOIN conta ON contas_pagar.cnt_cod = conta.cnt_cod
LEFT JOIN imp_contapagar ON contas_pagar.cpg_cod::VARCHAR = imp_contapagar.id
WHERE imp_contapagar.id IS NULL
  AND cpg_status = 'R'
  AND cpg_valor > 0
  AND empresa.emp_cod = 1; --OBS: Como os títulos não estão vinculados às Empresas estou travando aqui para vincular tudo com a primeira Empresa"""

demanda = """INSERT INTO imp_historicovenda(
  imp_produtoid,
  imp_unidadenegocioid,
  DATA,
  quantidade)
SELECT
  imp_produto.id AS imp_produtoid,
  imp_unidadenegocio.id AS imp_unidadenegocioid,
  venda.ven_dat::DATE AS DATA,
  SUM(itens_venda.itv_qtde) AS quantidade
FROM empresa
JOIN venda ON (TRUE)
JOIN itens_venda ON (venda.ter_cod = itens_venda.ter_cod AND venda.ven_cod = itens_venda.ven_cod)
JOIN imp_produto ON imp_produto.id = itens_venda.pro_cod::VARCHAR
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = empresa.emp_cod::VARCHAR
LEFT JOIN imp_historicovenda ON itens_venda.pro_cod::VARCHAR = imp_historicovenda.imp_produtoid AND empresa.emp_cod::VARCHAR = imp_historicovenda.imp_unidadenegocioid    
WHERE imp_historicovenda.imp_produtoid IS NULL
  AND venda.ven_dat >= NOW() - INTERVAL '3' MONTH
  AND venda.ven_status = 'A'   
GROUP BY 1, 2, 3;"""
