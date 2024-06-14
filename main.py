from selecionarDia import EscolhaSistema


def main ():

        # Pede ao usuário para inserir o nome do banco de dados
    db_name = input("Qual é o nome da base de dados que deseja manipular?\n: ")

    # Configuração dos bancos de dados
    source_db_config = {
        "host": "localhost",
        "database": db_name,
        "user": "postgres",
        "password": "supertux"
    }

    # Migra dados
    sistema = input("""Qual sistema deseja manipular?\n1 - Sistema SIM\n2 - Sistema LOGICON\n3 - Sistema EFETIVO\n4 - Sistema INFOMASTER\n:   """)
    EscolhaSistema(source_db_config, sistema)
