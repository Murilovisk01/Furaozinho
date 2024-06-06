# selecionarDia.py
from popular.popular_Sim import SistemaSim, popular_dia1 as sim_dia1, popular_dia2 as sim_dia2
from popular.popular_logicon import SistemaLogicon, popular_dia1 as logicon_dia1, popular_dia2 as logicon_dia2
from popular.popular_efetivo import SistemaEfetivo, popular_dia1 as efetivo_dia1, popular_dia2 as efetivo_dia2
from popular.popular_infoMaster import SistemaInfoMaster, popular_dia1 as info_dia1, popular_dia2 as info_dia2



def EscolhaSistema(source_db_config, sistema):
    if sistema.lower() == "1":
        sistema_sim = SistemaSim(source_db_config)
        opcao = input("Qual DIA deseja realizar\n1 - DIA 01\n2 - DIA 02\n:  ")
        if opcao == '1':
            sim_dia1(source_db_config)
        elif opcao == '2':
            sim_dia2(source_db_config)
        else:
            print("Opção inválida. Por favor, escolha novamente.")
    elif sistema.lower() == "2":
        sistema_logicon = SistemaLogicon(source_db_config)
        opcao = input("Qual DIA deseja realizar\n1 - DIA 01\n2 - DIA 02\n:  ")
        if opcao == '1':
            logicon_dia1(source_db_config)
        elif opcao == '2':
            logicon_dia2(source_db_config)
        else:
            print("Opção inválida. Por favor, escolha novamente.")
    elif sistema.lower() == "3":
        sistema_efetivo = SistemaEfetivo(source_db_config)
        opcao = input("Qual DIA deseja realizar\n1 - DIA 01\n2 - DIA 02\n:  ")
        if opcao == '1':
            efetivo_dia1(source_db_config)
        elif opcao == '2':
            efetivo_dia2(source_db_config)
        else:
            print("Opção inválida. Por favor, escolha novamente.")    
    elif sistema.lower() == "4":
        sistema_infoMaster = SistemaInfoMaster(source_db_config)
        opcao = input("Qual DIA deseja realizar\n1 - DIA 01\n2 - DIA 02\n:  ")
        if opcao == '1':
            info_dia1(source_db_config)
        elif opcao == '2':
            info_dia2(source_db_config)
        else:
            print("Opção inválida. Por favor, escolha novamente.")   
    else:
        print("Sistema inválido.")
