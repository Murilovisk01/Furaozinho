import psycopg2
import logging

# Função para conectar ao banco de dados e executar a consulta
def obter_registros():
    try:
        # Conectar ao banco de dadosde dados
        conn = psycopg2.connect(
            dbname=base_secundaria["nome"],
            user=base_secundaria["usuario"],
            password=base_secundaria["senha"],
            host=base_secundaria["host"]
        )
        # Criar um cursor para a conexão
        cur = conn.cursor()

        # Consulta SQL para obter todos os registros da tabela
        cur.execute(f"SELECT 'MERGE.'||ID, login, senha, apelido FROM imp_usuario")
        usuarios = cur.fetchall()

        cur.execute(f"""SELECT 'MERGE.'||ID,Codigo,Nome,NomeFantasia,RazaoSocial,CNPJ,InscricaoEstadual,
        EstadoInscricaoEstadual,Endereco,Numero,Cep,Bairro,Cidade,Estado,Telefone FROM imp_unidadenegocio""")
        unidade_Negocios = cur.fetchall()

        cur.execute(f"SELECT 'MERGE.'||ID, nome FROM imp_principioativo")
        principios_ativos = cur.fetchall()

        cur.execute(f"SELECT 'MERGE.'||ID, nome, tipo, cnpj from imp_Fabricante")
        fabricantes = cur.fetchall()

        #Classificação Nivel 1
        cur.execute(f"Select 'MERGE.'||id, nome, principal, 'MERGE' from imp_classificacao where profundidade = 1 ")
        class_nivel1 = cur.fetchall()
        #Classificação Nivel 2
        cur.execute(f"Select 'MERGE.'||id, nome, principal, 'MERGE.'||imp_classificacaopaiid from imp_classificacao where profundidade = 2 ")
        class_nivel2 = cur.fetchall()
        #Classificação Nivel 3
        cur.execute(f"Select 'MERGE.'||id, nome, principal, 'MERGE.'||imp_classificacaopaiid from imp_classificacao where profundidade = 3 ")
        class_nivel3 = cur.fetchall()
        #Classificação Nivel 4
        cur.execute(f"Select 'MERGE.'||id, nome, principal, 'MERGE.'||imp_classificacaopaiid from imp_classificacao where profundidade = 4 ")
        class_nivel4 = cur.fetchall()

        cur.execute(f"INSERT INTO Imp_Classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) VALUES ('MERGE', 'MERGE', 1, TRUE, 'RAIZ');")


        # Fechar o cursor e a conexão
        cur.close()
        conn.close()
        return usuarios,unidade_Negocios,principios_ativos,fabricantes,class_nivel1,class_nivel2,class_nivel3,class_nivel4
    
    except psycopg2.Error as e:
        # Em caso de erro, fecha o cursor e a conexão e relança a exceção
        cur.close()
        conn.close()
        raise e

#Conexão nas bases principal
def inserir_dados_na_base_principal():
    conn_principal = psycopg2.connect(
        dbname=base_principal["nome"],
        user=base_principal["usuario"],
        password=base_principal["senha"],
        host=base_principal["host"]
    )
    cur_principal = conn_principal.cursor()

    try:
        # Obtendo os registros da base secundária
        usuarios, unidade_Negocios, principios_ativos,fabricantes,class_nivel1,class_nivel2,class_nivel3,class_nivel4  = obter_registros()

        for registro in usuarios:
            cur_principal.execute("select count(*) from imp_usuario where id = %s", (registro[0],))
            count = cur_principal.fetchone()[0]
            if count > 0:
                novo_id = registro[0] + ".MERGE"
            else:
                novo_id = registro[0]

            cur_principal.execute("select count(*) from imp_usuario where login = %s", (registro[1],))
            count = cur_principal.fetchone()[0]
            if count > 0:
                novo_login = registro[1] + "-MERGE"
            else:
                novo_login = registro[1]            
            cur_principal.execute("insert into imp_usuario (id,login,senha,apelido) values (%s, %s, %s, %s)",(novo_id, novo_login, registro[2], registro[3]))
            print("Insert de Usuarios com sucesso!")

        for unidade in unidade_Negocios: 
            cur_principal.execute("""
                INSERT INTO imp_unidadenegocio (ID,Codigo,Nome,NomeFantasia,RazaoSocial,CNPJ,InscricaoEstadual,
                EstadoInscricaoEstadual,Endereco,Numero,Cep,Bairro,Cidade,Estado,Telefone)
                values (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s)""",(unidade[0], unidade[1], unidade[2], unidade[3],
                unidade[4], unidade[5], unidade[6], unidade[7],unidade[8], unidade[9], unidade[10], unidade[11], unidade[12], unidade[13],unidade[14]))
            print("Insert de Unidade de Negocio com sucesso!")
            
        for principio in principios_ativos:
            # Verifica se o nome do princípio ativo já existe na base principal
            cur_principal.execute("SELECT COUNT(*) FROM imp_principioativo WHERE nome = %s", (principio[1],))
            count = cur_principal.fetchone()[0]

            # Se não existir, insere o registro na base principal
            if count == 0:
                cur_principal.execute("INSERT INTO imp_principioativo (ID, nome) VALUES (%s, %s)", principio)
            print("Insert de Principio Ativo com sucesso!")

        for fabricante in fabricantes:
            cur_principal.execute("INSERT INTO imp_Fabricante (ID, nome, tipo, cnpj) VALUES (%s, %s,%s,%s)",fabricante)
            print("Insert de Fabricante com sucesso!")

        cur_principal.execute("INSERT INTO Imp_Classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) VALUES ('MERGE', 'MERGE', 1, TRUE, 'RAIZ');")

        #Nivel 1 
        for nivel1 in class_nivel1:
            cur_principal.execute("INSERT INTO Imp_Classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) VALUES (%s, %s,2, %s,  %s)",nivel1)
            print("Insert de Classificacao com sucesso!")
        for nivel2 in class_nivel2:
            cur_principal.execute("INSERT INTO Imp_Classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) VALUES (%s, %s,3, %s,  %s)",nivel2)
            print("Insert de Classificacao com sucesso!")
        for nivel3 in class_nivel3:
            cur_principal.execute("INSERT INTO Imp_Classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) VALUES (%s, %s,4, %s,  %s)",nivel3)  
            print("Insert de Classificacao com sucesso!")
        for nivel4 in class_nivel4:
            cur_principal.execute("INSERT INTO Imp_Classificacao (id, nome, profundidade, principal, imp_classificacaopaiid) VALUES (%s, %s,5,%s,  %s)",nivel4)      
            print("Insert de Classificacao com sucesso!")


        # Commit para salvar as alterações no banco de dados
        conn_principal.commit()
        print("Registros inseridos com sucesso!")
    except psycopg2.Error as e:
        # Em caso de erro, faz rollback das alterações
        conn_principal.rollback()
        print("Erro ao inserir registros:", e)
    finally:
        # Fechar o cursor e a conexão
        cur_principal.close()
        conn_principal.close()


#conexao com o banco 
base_secundaria = {
    "nome": "teste1",
    "usuario": "postgres",
    "senha": "supertux",
    "host": "localhost"
}

base_principal = {
    "nome": "teste",
    "usuario": "postgres",
    "senha": "supertux",
    "host": "localhost"
}

# Chamada da função para inserir os registros na base principal
inserir_dados_na_base_principal()