from selecionarDia import EscolhaSistema


if __name__ == "__main__":
    # Configuração dos bancos de dados
    source_db_config = {
        "host": "localhost",
        "database": "simteste_imp",
        "user": "postgres",
        "password": "supertux"
    }



    # Migra dados
sistema = input("""Qual sistema deseja manipular?\n1 - Sistema SIM\n2 - Sistema LOGICON\n:  """)
EscolhaSistema(source_db_config, sistema)
