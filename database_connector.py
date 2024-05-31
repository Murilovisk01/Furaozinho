import psycopg2
import logging

class DatabaseConnector:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.config)
            logging.info("Conexão estabelecida com sucesso")
            return self.connection
        except psycopg2.Error as error:
            logging.error(f"Erro ao conectar ao banco de dados: {error}")
            raise

    def close(self):
        if self.connection:
            self.connection.close()
            logging.info("Conexão fechada")
