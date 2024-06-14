import logging
import time
from psycopg2 import sql, DatabaseError
import psycopg2
from database_connector import DatabaseConnector
from script.query_infoMaster import ( tmp_produto, usuario, unidadeNegocio, grupoRemarcacao, principioAtivo, fabricanteNaoInformado, fabricante, classficacao, 
    produto, produtoMae, codigoDeBarrasAdicional,duploPerfilImcs,impostoLucroPresumido, impostoSimples, fornencedor, 
    planoPagamento, cadernoDeOferta, cadernoDeOfertaQuantidade,cadernoDeOfertaLevePague, cadernoDeOfertaClassificacao,cadernoDeOfertaUnidade, 
    crediario, cliente,  dependenteCliente, planoRemuneracao, prescritores, crediarioReceber, custo, estoque, contasAPagar, demanda )

# Dicionário mapeando as consultas para nomes legíveis
query_names = {
    tmp_produto: "TMP Produto",
    usuario: "Usuário",
    unidadeNegocio: "Unidade de Negócio",
    grupoRemarcacao: "Grupo de Remarcação",
    principioAtivo: "Princípio Ativo",
    fabricanteNaoInformado: "Fabricante Não Informado",
    fabricante: "Fabricante",
    classficacao: "Classificação",
    produto: "Produto",
    produtoMae: "Produto Mãe",
    codigoDeBarrasAdicional: "Código de Barras Adicional",
    duploPerfilImcs: "Imposto Duplo",
    impostoSimples: "Imposto Simples",
    impostoLucroPresumido: "Imposto Lucro/Presumido",
    fornencedor: "Fornecedor",
    planoPagamento: "Plano de Pagamento",
    cadernoDeOferta: "Caderno de Oferta",
    cadernoDeOfertaQuantidade: "Caderno de Oferta Por Quantidade",
    cadernoDeOfertaClassificacao: "Caderno de Oferta Por Classificacao",
    cadernoDeOfertaUnidade: "Caderno de Oferta Por unidade",
    cadernoDeOfertaLevePague: "Caderno de Oferta Por Leve e Pague",
    crediario: "Crediário",
    cliente: "Cliente",
    dependenteCliente: "Dependente do Cliente",
    planoRemuneracao: "Plano de Remuneração",
    prescritores: "Prescritores",
    crediarioReceber: "Crediário a Receber",
    custo: "Custo",
    estoque: "Estoque",
    contasAPagar: "Contas a Pagar",
    demanda: "Demanda"
}

class SistemaInfoMaster:
    def __init__(self, source_db_config):
        self.source_db_config = source_db_config

def popular_dia1(source_db_config):
    # Configura o logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Criando instâncias do DatabaseConnector
        source_connector = DatabaseConnector(source_db_config)

        # Conecta-se ao banco de dados de origem
        with source_connector.connect() as source_conn:
            logger.info("Conectado ao banco de dados! Começando o DIA 1!")

            # Inicia a transação
            source_conn.autocommit = False

            # Inicia o cronômetro
            start_time = time.time()

            with source_conn.cursor() as source_cursor:
                # Lista de consultas a serem executadas
                queries = [
                tmp_produto, usuario, unidadeNegocio, grupoRemarcacao, principioAtivo, fabricanteNaoInformado, fabricante, classficacao, 
                produto, produtoMae, codigoDeBarrasAdicional, fornencedor, 
                planoPagamento, cadernoDeOferta, cadernoDeOfertaQuantidade,cadernoDeOfertaLevePague, cadernoDeOfertaClassificacao,cadernoDeOfertaUnidade, 
                crediario, cliente,  dependenteCliente, planoRemuneracao, prescritores,
                ]

                for query in queries:
                    query_name = query_names.get(query, "Consulta Desconhecida")
                    try:
                        source_cursor.execute(query)
                        inserted_records = source_cursor.rowcount
                        logger.info(f"{inserted_records} registros inseridos com sucesso para consulta: {query_name}")
                        source_conn.commit()
                    except psycopg2.Error as e:
                        logger.error(f"Erro ao executar a consulta {query_name}: {e}")
                        source_conn.rollback()
                        input("Corrija o problema e pressione Enter para continuar...")

                # Seleção de impostos
                while True:
                    opcao = input("""Insert da tabela imp_icmsproduto\n1 - Imposto Duplo\n2 - Imposto Simples\n3 - Imposto Lucro Presumido\nDigite o modelo desejado :""")
                    try:
                        if opcao == '1':
                            source_cursor.execute(duploPerfilImcs)
                        elif opcao == '2':
                            source_cursor.execute(impostoSimples)
                        elif opcao == '3':
                            source_cursor.execute(impostoLucroPresumido)
                        else:
                            print("Opção inválida. Por favor, escolha novamente.")
                            continue

                        inserted_records = source_cursor.rowcount
                        logger.info(f"{inserted_records} registros inseridos com sucesso para consulta: Imposto {opcao}")
                        source_conn.commit()
                        break
                    except psycopg2.Error as e:
                        logger.error(f"Erro ao executar a consulta para Imposto {opcao}: {e}")
                        source_conn.rollback()
                        input("Corrija o problema e pressione Enter para continuar...")

            # Calcula o tempo decorrido
            elapsed_time = int(time.time() - start_time)
            logger.info(f"Tempo decorrido: {elapsed_time} segundos")
            logger.info("Dados do DIA 1 inseridos com sucesso!")

    except psycopg2.Error as e:
        logger.error(f"Ocorreu um erro: {e}")


def popular_dia2(source_db_config):
    # Configura o logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Criando instâncias do DatabaseConnector
        source_connector = DatabaseConnector(source_db_config)

        # Conecta-se ao banco de dados de origem
        with source_connector.connect() as source_conn:
            logger.info("Conectado ao banco de dados! Começando o DIA 2!")

            # Inicia a transação
            source_conn.autocommit = False

            # Inicia o cronômetro
            start_time = time.time()

            with source_conn.cursor() as source_cursor:
                # Lista de consultas a serem executadas
                queries = [
                    tmp_produto,principioAtivo,fabricante, produto, produtoMae,
                    codigoDeBarrasAdicional, cliente, dependenteCliente, custo, estoque, contasAPagar, demanda, crediarioReceber
                ]

                for query in queries:
                    try:
                        source_cursor.execute(query)
                        inserted_records = source_cursor.rowcount
                        query_name = query_names.get(query, "Consulta Desconhecida")
                        logger.info(f"{inserted_records} registros inseridos com sucesso para consulta: {query_name}")
                        source_conn.commit()
                    except psycopg2.Error as e:
                        logger.error(f"Erro ao executar a consulta {query_name}: {e}")
                        source_conn.rollback()
                        input("Corrija o problema e pressione Enter para continuar...")

            # Calcula o tempo decorrido
            elapsed_time = int(time.time() - start_time)
            logger.info(f"Tempo decorrido: {elapsed_time} segundos")
            logger.info("Dados do DIA 2 inseridos com sucesso!")

    except psycopg2.Error as e:
        logger.error(f"Ocorreu um erro: {e}")
