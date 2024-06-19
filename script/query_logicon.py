# -*- coding: utf-8 -*-
tmp_produto = """DROP TABLE IF EXISTS tmp_produto;
CREATE TABLE tmp_produto (produtoid VARCHAR(100), PRIMARY KEY (produtoid));
INSERT INTO tmp_produto                                           
WITH estoque AS (
	SELECT
	procodigo AS produtoid,
	SUM(estatual::NUMERIC) AS est
FROM estoque
GROUP BY 1   
)
SELECT DISTINCT 
	vendacheckout.procodigo
FROM vendacheckout 
JOIN estoque ON estoque.produtoid = vendacheckout.procodigo
WHERE vendacheckout.vdcdata::TIMESTAMP > now() - INTERVAL '24' MONTH OR estoque.est > 0;"""

usuario = """
INSERT INTO Imp_Usuario (
  ID,
  Login,
  Senha,
  Apelido)
SELECT 
    usucodigo AS ID,
    usucodigo||'.'||usunome AS Login,
    '123' AS Senha,
    usunome AS Apelido
FROM usuarios;"""

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
    empcodigo AS id,
    empcodigo AS Codigo,
    empnome AS Nome,
    empfantasia AS NomeFantasia,
    empnome AS RazaoSocial,
    regexp_replace(empcnpj, '[^0-9]', '', 'g') AS CNPJ,
    regexp_replace(empie, '[^0-9]', '', 'g') AS InscricaoEstadual,
    ufcodigo AS EstadoInscricaoEstadual,
    empendereco AS Endereco,
    'S/N' AS Numero,
    regexp_replace(empcep, '[^0-9]', '', 'g') AS Cep,
    SUBSTRING(UPPER(TRIM(empbairro)),1,30) AS Bairro,
    SUBSTRING(UPPER(TRIM(empcidade)),1,30) AS Cidade,
    ufcodigo AS Estado,
    regexp_replace(empfone, '[^0-9]', '', 'g') AS Telefone
FROM empresa;"""

grupoRemarcacao = """select"""

principioAtivo = """
INSERT INTO Imp_PrincipioAtivo (
  	ID,
  	Nome)
SELECT 
    pavcodigo AS ID,
    UPPER(SUBSTRING(TRIM(pavdescricao),1,130)) AS Nome
FROM principioativo
LEFT JOIN Imp_PrincipioAtivo ON Imp_PrincipioAtivo.id  = principioativo.pavcodigo::VARCHAR
WHERE Imp_PrincipioAtivo.ID IS NULL;
"""

fabricanteNaoInformado = """INSERT INTO Imp_Fabricante(ID,Nome,Tipo) VALUES('-1', 'FABRICANTE NÃO INFORMADO', 'J');"""

fabricante = """INSERT INTO Imp_Fabricante(
	ID,
	Nome,
	Tipo,
	CNPJ)
SELECT 
    pessoa.pescodigo AS ID,
	pessoa.pesnome AS Nome,
    pessoa.pestipo AS Tipo,
    REGEXP_REPLACE(pesjuridica.pjucnpj, '[^0-9]', '', 'g') AS CNPJ
FROM pessoa
JOIN pesjuridica ON pesjuridica.pescodigo = pessoa.pescodigo
LEFT JOIN Imp_Fabricante ON Imp_Fabricante.ID = pessoa.pescodigo::VARCHAR
WHERE pesfornecedor = 'S' AND imp_fabricante.id IS NULL;
"""

classficacao = """--CLASSIFICAÇÃO RAIZ
INSERT INTO Imp_Classificacao (id, nome, profundidade, principal) VALUES ('RAIZ', 'PRINCIPAL', 0, TRUE);

--PARA PRODUTOS SEM CLASSIFICAÇÃO
INSERT INTO Imp_Classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) VALUES ('RAIZ.NÃOINFORMADA', 'NÃO INFORMADA', 1, TRUE, 'RAIZ');

-- NIVEL 1
INSERT INTO imp_classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) 
SELECT 
	clmcodigo AS id, 
	clmdescricao AS nome, 
	1 AS profundidade, 
	'true' AS principal, 
	'RAIZ' AS imp_classificacaopaiid
FROM classmerc
WHERE clmnivel = '1';

-- NIVEL 2
INSERT INTO imp_classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) 
SELECT 
clmcodigo AS id, 
clmdescricao AS nome, 
2 AS profundidade, 
'true' AS principal, 
clmpai AS imp_classificacaopaiid
FROM classmerc
WHERE clmnivel = '2';"""

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
  PrecoReferencial,
  PrecoVenda,
  ListaPIS,
  listadcb,
  TipoPreco,
  RegistroMS,
  CodigoNCM,
  Imp_PrincipioAtivoID,
  Imp_ClassificacaoID,
  Tipo
 )
SELECT DISTINCT ON (produto.procodigo)
	produto.procodigo AS ID,
	UPPER (SUBSTRING(TRIM(produto.prodescricao),1,60)) AS Descricao,
	COALESCE(imp_fabricante.id, '-1') AS Imp_FabricanteID,
	SUBSTRING(TRIM(procodbarra.codbarra),1,14) AS CodigoBarras,
	(CASE
		WHEN produto.cifcodigo = '3' THEN 'A' -- substituido
		WHEN produto.cifcodigo = '4' THEN 'B' -- isento
		WHEN produto.cifcodigo = '5' THEN 'C' -- não tributado
		WHEN produto.cifcodigo = '1' THEN 'D' -- tributado
	ELSE 'A' -- senão substituido porque é a maioria
	END) AS TipoAliquota,
	produto.proicms::NUMERIC AS ValorAliquota,
	imp_cest.id AS CestID,
	perfilpissn.id AS PerfilPISSnID,
	perfilcofinssn.id AS PerfilCofinsSnID,
	perfilpis.id AS PerfilPISID,
	perfilcofins.id AS PerfilCofinsID,
	produto.propreco_nfiscal::NUMERIC(15,2) AS PrecoReferencial,
	produto.propreco_venda::NUMERIC(15,2) AS PrecoVenda,
	'A' AS ListaPIS,
	NULL AS listadcb,
	'L' AS TipoPreco,
	SUBSTRING(TRIM(produto.proregistro_anvisa),1,13) AS RegistroMS,
	SUBSTRING(TRIM(produto.proncm),1,8) AS CodigoNCM,
	imp_principioativo.id AS Imp_PrincipioAtivoID,
	COALESCE(Imp_Classificacao.id, 'RAIZ.NÃOINFORMADA') AS Imp_ClassificacaoID,
	'M' AS Tipo
FROM produto
JOIN tmp_produto ON tmp_produto.produtoid = produto.procodigo::VARCHAR
LEFT JOIN proembala ON proembala.procodigo = produto.procodigo AND preembalagemvenda = 'S'
LEFT JOIN procodbarra ON procodbarra.precodigo = proembala.precodigo
LEFT JOIN imp_fabricante ON imp_fabricante.id = produto.forcodigo
LEFT JOIN imp_classificacao ON imp_classificacao.id = produto.clmcodigo
LEFT JOIN produtoxprincipioativo ON produtoxprincipioativo.procodigo::VARCHAR = produto.procodigo
LEFT JOIN imp_principioativo ON imp_principioativo.id = produtoxprincipioativo.pavcodigo::VARCHAR
LEFT JOIN cest ON cest.cestcodigo = produto.cestcodigo
LEFT JOIN imp_cest ON imp_cest.codigo = cest.cestchave
LEFT JOIN imp_produto ON imp_produto.id = produto.procodigo
LEFT JOIN perfilpis perfilpissn ON perfilpissn.piscst = produto.stpcodigo AND perfilpissn.tipocontribuinte = 'B'
LEFT JOIN perfilcofins perfilcofinssn ON perfilcofinssn.cofinscst = produto.stccodigo AND perfilcofinssn.tipocontribuinte = 'B'
LEFT JOIN perfilpis ON perfilpis.piscst =  produto.stpcodigo AND perfilpis.tipocontribuinte = 'A'
LEFT JOIN perfilcofins ON perfilcofins.cofinscst = produto.stccodigo AND perfilcofins.tipocontribuinte = 'A'
WHERE imp_produto.id IS NULL;
"""

produtoMae = """INSERT INTO Imp_Produto(
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
SELECT DISTINCT ON (ID)
	'-'||imp_produto.id AS ID,
	imp_produto.Descricao AS Descricao,
	'CX C/' || proembala.prequantidade AS Apresentacao,
	imp_produto.Imp_FabricanteID,
	imp_produto.TipoAliquota,
	imp_produto.ValorAliquota,
	imp_produto.CestID,
	imp_produto.PerfilPISSnID,
	imp_produto.PerfilCofinsSnID,
	imp_produto.PerfilPISID,
	imp_produto.PerfilCofinsID,
	imp_produto.PrecoReferencial * proembala.prequantidade::NUMERIC(15,2) AS PrecoReferencial,
	imp_produto.PrecoVenda * proembala.prequantidade::NUMERIC(15,2) AS PrecoVenda,
	imp_produto.ListaPIS,
	imp_produto.listadcb,
	imp_produto.TipoPreco,
	imp_produto.RegistroMS,
	imp_produto.CodigoNCM,
	imp_produto.Imp_PrincipioAtivoID,
	imp_produto.Imp_ClassificacaoID,
	imp_produto.Tipo,
	imp_produto.id AS IDProdutoContido,
	proembala.prequantidade::INT AS QuantidadeEmbalagem
FROM imp_produto
JOIN produto ON produto.procodigo = imp_produto.id
LEFT JOIN proembala ON proembala.procodigo = produto.procodigo AND preembalagemvenda = 'N'
LEFT JOIN procodbarra ON procodbarra.precodigo = proembala.precodigo
LEFT JOIN imp_produto imp_pro ON imp_pro.id = '-' || imp_produto.ID
WHERE proembala.prequantidade > '1'
AND imp_produto.id IS NULL;
"""

codigoDeBarrasAdicional = """INSERT INTO imp_codigobarras(
  codigobarras,
  imp_produtoid)
SELECT DISTINCT
  SUBSTRING(regexp_replace(ltrim(procodbarra.codbarra, '0'), '[^0-9]','','g'), 1,14)AS CodigoBarras,
  imp_produto.id AS imp_produtoid
FROM produto
LEFT JOIN proembala ON proembala.procodigo = produto.procodigo
LEFT JOIN procodbarra ON procodbarra.precodigo = proembala.precodigo
JOIN imp_produto ON imp_produto.id = produto.procodigo
LEFT JOIN imp_codigobarras ON imp_codigobarras.codigobarras = SUBSTRING(regexp_replace(ltrim(procodbarra.codbarra, '0'), '[^0-9]','','g'), 1,14)
WHERE imp_produto.codigobarras <> SUBSTRING(regexp_replace(ltrim(procodbarra.codbarra, '0'), '[^0-9]','','g'), 1,14)
AND imp_codigobarras.codigobarras IS NULL;
"""

duploPerfilImcs = """select"""

impostoLucroPresumido = """-- Inserir na imp_icmsproduto
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
JOIN SITUACAO_TRIBUTARIA_NFISCAL ON '0'||perfilicms.icmscst = SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf
JOIN produto ON produto.pro_sit_trib_nf = SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf
JOIN imp_produto ON imp_produto.id = produto.procodigo, imp_unidadenegocio
)
SELECT DISTINCT ON (icmsproduto.imp_produtoid, icmsproduto.estado)
  icmsproduto.*
FROM icmsproduto
LEFT JOIN imp_icmsproduto ON imp_icmsproduto.imp_produtoid = icmsproduto.imp_produtoid AND imp_icmsproduto.estado = icmsproduto.estado
WHERE imp_icmsproduto.imp_produtoid IS NULL;"""

impostoSimples = """-- Inserir na imp_icmsproduto
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
JOIN SITUACAO_TRIBUTARIA_NFISCAL ON (perfilicms.icmssncso = CASE 
          WHEN SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf = '000' THEN '102'
          WHEN SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf = '010' THEN '202'
          WHEN SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf = '020' THEN '102'
          WHEN SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf = '030' THEN '203'
          WHEN SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf = '040' THEN '300'
          WHEN SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf = '041' THEN '400'
          WHEN SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf = '050' THEN '400'
          WHEN SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf = '051' THEN '400'
          WHEN SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf = '060' THEN '500'
          WHEN SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf = '070' THEN '500'
		  WHEN SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf = '090' THEN '900'
              END)
JOIN produto ON produto.pro_sit_trib_nf = SITUACAO_TRIBUTARIA_NFISCAL.pro_sit_trib_nf
JOIN imp_produto ON imp_produto.id = produto.procodigo, imp_unidadenegocio
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
    Email,
    CNPJ,
    CPF,
    INSCRICAOESTADUAL,
    IDENTIDADE)
SELECT
    pessoa.pescodigo AS ID,
    UPPER((TRIM(pessoa.pesnome))) AS Nome,
    COALESCE(NULLIF(UPPER(TRIM(pessoa.pestipo)),''), 'J') AS Tipo,
    SUBSTRING(NULLIF(REGEXP_REPLACE(pessoa.pesfone,'[^0-9]', '', 'g'), ''),1,16) AS Telefone,
    TRIM(pessoa.pesemail) AS Email,
    CASE
        WHEN pessoa.pestipo = 'J' THEN pesjuridica.pjucnpj
    END AS CNPJ,
    CASE 
        WHEN pessoa.pestipo = 'F' THEN pesfisica.pficpf
    END AS CPF,
    CASE
        WHEN pessoa.pestipo = 'J' THEN pesjuridica.pjuinsestadual
    END AS INSCRICAOESTADUAL,
    CASE 
        WHEN pessoa.pestipo = 'F' THEN pesfisica.pfirg
    END AS IDENTIDADE
FROM pessoa
LEFT JOIN pesjuridica ON pesjuridica.pescodigo = pessoa.pescodigo
LEFT JOIN pesfisica ON pessoa.pescodigo = pesfisica.pescodigo
WHERE pessoa.pesfornecedor = 'S'
AND Imp_Fornecedor.ID IS NULL;
"""


planoPagamento = """/*Plano de pagamento no sistema é colocado no cliente, como na importação nao tem como importa direto no cliente estamos fazendo a importação dos planos que é feito no cliente 
O implantador tera que repassar com o cliente e ensinar a fazer o vinculo no cliente caso ele queira continuar a fazer assim*/

INSERT INTO Imp_PlanoPagamento (ID, Nome, MinParcela, MaxParcela, TipoIntervaloEntrada, IntervaloEntrada, TipoIntervaloParcela, IntervaloParcela) VALUES ('0', '0.PARTICULAR', 1, 1, 'M', 1, 'M', 1);

INSERT INTO Imp_PlanoPagamento(
	ID, 
	Nome, 
	MinParcela, 
	MaxParcela, 
	TipoIntervaloEntrada,
	IntervaloEntrada, 
	TipoIntervaloParcela, 
	IntervaloParcela)
SELECT DISTINCT ON (IntervaloEntrada)
	pescodigo AS id, 
	'PLANO DE PAGAMENTO DIA ' ||'- '||pcldiavencimento AS nome,
	1 AS MinParcela,
	1 AS MaxParcela,
	'D' AS tipointervaloentrada,
	pcldiavencimento AS IntervaloEntrada,
	'M' AS TipoIntervaloparcela,
	1 AS IntervaloParcela
FROM pescliente;"""

cadernoDeOferta = """INSERT INTO Imp_CadernoOferta(
    ID, 
    Nome, 
    DataHoraInicial, 
    DataHoraFinal)
SELECT
    'ofert'||'.'||ofrcodigo AS ID, 
    ofrdescricao AS Nome, 
    ofrdatainicio AS DataHoraInicial, 
    ofrdatafim AS DataHoraFinal
FROM ofertaretaguarda
WHERE ofrstatus = 'A';
INSERT INTO Imp_CadernoOferta(
    ID, 
    Nome, 
    DataHoraInicial, 
    DataHoraFinal)
SELECT
	prmcodigo AS ID, 
	prmdescricao AS Nome, 
	prmdatainicio AS DataHoraInicial, 
	prmdatafim AS DataHoraFinal
FROM promocao
WHERE prmstatus = 'A';

INSERT INTO Imp_ItemCadernoOferta(
    Imp_CadernoOfertaID,
    Imp_ProdutoID,
    TipoOferta,
    DescontoOferta,
    precoOferta)
SELECT 
	imp_cadernooferta.id AS Imp_CadernoOfertaID,
	imp_produto.id AS Imp_ProdutoID,
	'P' AS TipoOferta,
	NULL AS DescontoOferta,
	ofertaretaguardaitem.oitvalor::NUMERIC AS precoOferta
FROM ofertaretaguardaitem
JOIN proembala ON proembala.precodigo = ofertaretaguardaitem.precodigo
JOIN produto ON proembala.procodigo = produto.procodigo 
JOIN procodbarra ON procodbarra.precodigo = proembala.precodigo	
JOIN imp_produto ON imp_produto.id = produto.procodigo
JOIN imp_cadernooferta ON imp_cadernooferta.id = 'ofert' || '.' || CAST(ofrcodigo AS VARCHAR);

INSERT INTO Imp_ItemCadernoOferta(
    Imp_CadernoOfertaID,
    Imp_ProdutoID,
    TipoOferta,
    precoOferta)
SELECT 
	imp_cadernooferta.id AS Imp_CadernoOfertaID,
	imp_produto.id AS Imp_ProdutoID,
	'P' AS TipoOferta,
	itempromocao.ipmvalor::NUMERIC AS precoOferta
FROM ITEMPROMOCAO
JOIN imp_produto ON imp_produto.id = ITEMPROMOCAO.procodigo::VARCHAR
JOIN imp_cadernooferta ON imp_cadernooferta.id = ITEMPROMOCAO.prmcodigo::VARCHAR;
"""

cadernoDeOfertaQuantidade = """select"""

cadernoDeOfertaLevePague = """select"""

cadernoDeOfertaClassificacao = """select"""

cadernoDeOfertaUnidade = """select"""

crediario = """                                                        --CREDIÁRIO AVISTA
INSERT INTO Imp_Crediario (ID, NomeCrediario, LimitePadraoCliente, Imp_PlanoPagamentoID) VALUES ('AVISTA', 'AVISTA', 0, '0');

INSERT INTO Imp_Crediario (
	ID,
	NomeCrediario,
	LimitePadraoCliente,
	Imp_PlanoPagamentoID,	
	TipoCrediario
)
SELECT 
	grccodigo AS id,
	grcdescricao AS nomeCrediario,
	'0' AS LimitePadraoCliente,
	'0' AS Imp_PlanoPagamentoID,
	'P' AS TipoCrediario
FROM grupo_cliente;"""

cliente = """INSERT INTO Imp_Cliente (
  ID,
  Imp_CrediarioID,
  STATUS,
  NumeroCartao,	
  DataAberturaCrediario,
  TipoLimite,
  Limite,
  Nome,
  Tipo,
  Telefone,
  Email,
  DataNascimento,
  Sexo,
  Cnpj,
  CPF,
  inscricaoestadual,
  identidade,
  SiglaOrgaoIdentidade,
  EstadoIdentidade)
SELECT 
    pescliente.pescodigo AS id,
    CASE 
        WHEN pescliente.grccodigo IS NULL THEN 'AVISTA'
        ELSE pescliente.grccodigo::VARCHAR 
    END AS imp_crediarioid,
    CASE
		WHEN pescliente.pclstatus = 'B' THEN 'S'
	ELSE pescliente.pclstatus END AS STATUS,
	cartaocliente.ctccartao AS NumeroCartao,
    pescliente.pclcadastro AS DataAberturaCrediario,
    'P' AS TipoLimite,
    pescliente.pcllimitecredito AS Limite,
    pessoa.pesnome AS Nome,
    pessoa.pestipo AS Tipo,
    SUBSTRING(TRIM(pessoa.pesfone),1,16) AS Telefone,
    TRIM(pessoa.pesemail) AS Email,
    CASE 
        WHEN pessoa.pestipo = 'F' THEN pesfisica.pfidatanascimento
    END AS DataNascimento,
    CASE
        WHEN pessoa.pestipo = 'F' THEN pesfisica.pfisexo
    END AS Sexo,
    CASE
        WHEN pessoa.pestipo = 'J' THEN pesjuridica.pjucnpj
    END AS Cnpj,
    CASE 
        WHEN pessoa.pestipo = 'F' THEN pesfisica.pficpf
    END AS CPF,
    CASE
        WHEN pessoa.pestipo = 'J' THEN pesjuridica.pjuinsestadual
    END AS inscricaoestadual,
    CASE 
        WHEN pessoa.pestipo = 'F' THEN pesfisica.pfirg
    END AS identidade,
    SUBSTRING(TRIM(pessoa.pesuf), 1, 2) AS SiglaOrgaoIdentidade,
    SUBSTRING(TRIM(pessoa.pesuf), 1, 2) AS EstadoIdentidade
FROM 
    pescliente
LEFT JOIN pessoa ON pescliente.pescodigo = pessoa.pescodigo
LEFT JOIN cartaocliente ON cartaocliente.pescodigo = pessoa.pescodigo
LEFT JOIN pesfisica ON pessoa.pescodigo = pesfisica.pescodigo
LEFT JOIN pesjuridica ON pessoa.pescodigo = pesjuridica.pescodigo
LEFT JOIN imp_crediario ON imp_crediario.id = pescliente.grccodigo::VARCHAR
LEFT JOIN imp_cliente ON imp_cliente.id = pescliente.pescodigo::VARCHAR
WHERE Imp_Cliente.ID IS NULL;
"""

enderecoCliente = """INSERT INTO imp_cliente_endereco(
    id,
    imp_clienteid,
    endereco,
    numero,
    cep,
    bairro,
    cidade,
    estado)
SELECT
	pessoa.pescodigo AS id,
	imp_cliente.id AS imp_clienteid,
	pessoa.pesendereco AS endereco,
	'N/I' AS numero,
	pescep AS cep,
	pesbairro AS bairro,
	pescidade AS cidade,
	pesuf AS estado
FROM pescliente
LEFT JOIN pessoa ON pescliente.pescodigo = pessoa.pescodigo
JOIN Imp_Cliente ON Imp_Cliente.ID = pescliente.pescodigo::VARCHAR
WHERE pessoa.pesendereco IS NOT NULL;
"""

dependenteCliente = """select"""

planoRemuneracao = """select"""

prescritores = """select"""

crediarioReceber = """INSERT INTO imp_crediarioreceber (
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
SELECT
    titcodigo AS ID,
    imp_cliente.id AS Imp_ClienteID,
    imp_unidadenegocio.id AS Imp_UnidadeNegocioID,
    regexp_replace(titulo.titdocumento, '[^0-9]', '', 'g')::BIGINT AS NumeroDocumento,
    titemissao AS DataEmissao,
    titemissao + (pescliente.pcldiavencimento || ' days')::INTERVAL AS DataVencimento,
    (titvalor - tittotalpago)::NUMERIC(15,2) AS Valor,
    titnumparcelas AS NumeroParcela,
    titnumparcelas AS TotalParcela,
    titobservacao AS observacao 
FROM titulo
JOIN imp_cliente ON imp_cliente.id = titulo.pescodigo::VARCHAR
JOIN pescliente ON pescliente.pescodigo::VARCHAR = imp_cliente.id
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = titulo.empcodigo::VARCHAR
WHERE tittipodocumento = 'R' AND titstatus = 'A'
GROUP BY 1,2,3,4,5,6,7,8,9,10"""

custo = """INSERT INTO Imp_Custo(
	Imp_ProdutoID,
	Imp_UnidadeNegocioID,
	Custo,
	CustoMedio)
SELECT 
	imp_produto.id AS imp_produtoid,
	'1' AS imp_unididadeNegocioid,
	propreco_custo_sem_icms::NUMERIC(15,2) AS custo,
	propreco_custo_medio_cicms::NUMERIC(15,2) AS customedio
FROM produto
JOIN imp_produto ON imp_produto.id = produto.procodigo"""

estoque = """INSERT INTO Imp_Estoque (
	Imp_ProdutoID,
	Imp_UnidadeNegocioID,
	Estoque)
SELECT
	imp_produto.id AS imp_produtoid,
	'1' AS Imp_unidadeneogocioID, -- estou setando a loja porque nao tem coluna de loja
	SUM(estatual::NUMERIC) AS Estoque
FROM estoque
JOIN Imp_Produto ON Imp_Produto.id = estoque.procodigo::VARCHAR
WHERE estatual::NUMERIC > 0
GROUP BY 1  """

contasAPagar = """INSERT INTO Imp_ContaPagar (
	ID,
	Imp_UsuarioID,
	Imp_UnidadeNegocioID,
	Imp_FornecedorID,
	Descricao,  
	NumeroDocumento,
	DataEmissao,
	DataVencimento,
	ValorDocumento,
	NumeroParcela,  
	Desconto)
SELECT
	titcodigo AS ID,
	imp_usuario.id AS Imp_UsuarioID,
	imp_unidadenegocio.id AS Imp_UnidadeNegocioID,
	imp_fornecedor.id AS Imp_FornecedorID,
	SUBSTRING(imp_fornecedor.nome,1,50) AS Descricao,
	titdocumento AS NumeroDocumento,
	titemissao AS DataEmissao,
	titrecebimento AS DataVencimento,
	(titvalor - tittotalpago)::NUMERIC(15,2) AS ValorDocumento,
	titnumparcelas AS NumeroParcela,
	titdescontos AS Desconto
FROM titulo
JOIN imp_fornecedor ON imp_fornecedor.id = titulo.pescodigo::VARCHAR
JOIN imp_usuario ON imp_usuario.id = titulo.usucodigo::VARCHAR
JOIN imp_unidadenegocio ON imp_unidadenegocio.id = titulo.empcodigo::VARCHAR
WHERE tittipodocumento = 'D' AND titstatus = 'A' """

demanda = """INSERT INTO imp_historicovenda(
    imp_produtoid,
    imp_unidadenegocioid,
    DATA,
    quantidade)
SELECT 
    imp_produto.id AS imp_produtoid,
    '1' AS imp_unidadenegocioid, --Nao tem uma coluna do unidade de negocio, talvez a loja nao tenho funçao para multilojas 
    vdcdata AS DATA,
    vdcquantidade::NUMERIC AS quantidade
FROM VENDACHECKOUT
JOIN imp_produto ON imp_produto.id = VENDACHECKOUT.procodigo::VARCHAR
WHERE vdcdata > CURRENT_DATE - INTERVAL '180' DAY"""
