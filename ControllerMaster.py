import os
import socket
import uuid
import rpyc
from pymongo import MongoClient
from cryptography.fernet import Fernet
from module import key

MONGO_HOST = os.environ.get("MONGO_URI")
MONGO_NAME = "IOT"
DADOS = "DADOS"


class ControllerMaster(rpyc.Service):
    def __init__(self):
        self.controllerPort = 18861
        self.proxy = None
        self.host = 'localhost'
        self.key = key

    def exposed_join_system(self, name):
        user_id = uuid.uuid4()
        return str(user_id)

    def exposed_join_controller(self):  # Função para conectar ao controller
        self.proxy = rpyc.connect(self.host, self.controllerPort)
        self.conectar_mqtt()
        return True

    def exposed_verifica_conexao_controller(self):
        self.controllerPort = 18861
        # Checando primeiro controller
        if self.verifica_conexao_server(self.host, self.controllerPort):
            print("Conectado ao controller 1")
            return True
        else:
            self.controllerPort = 18862
            # Checando segundo controller
            if self.verifica_conexao_server(self.host, self.controllerPort):
                print("Conectado ao controller 2")
                return True
            else:
                return False

    def ligar_desligar_lampada(self, comando):  # Para acessar os controllers
        return self.proxy.root.ligar_desligar_lampada(comando)

    def exposed_ligar_desligar_lampada(self, comando):
        return self.ligar_desligar_lampada(comando)

    def monitorar(self):  # Para acessar os controllers
        return self.proxy.root.monitorar()

    def exposed_monitorar(self):  # Para responder ao cliente
        message = self.monitorar()
        return message

    def verifica_conexao_server(self, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((host, port))
            return True
        except (ConnectionRefusedError, socket.timeout):
            return False

    def conectar_mqtt(self):  # Decide qual controller vai publicar e assinar os tópicos
        return self.proxy.root.conectar_mqtt()


if __name__ == '__main__':
    print("Iniciando Controller Master")
    # Resetandio o banco de dados sempre que iniciar o master, para não houver superlotação
    mongo_cliente = MongoClient(MONGO_HOST)
    mongo_db = mongo_cliente[MONGO_NAME]
    mongo_collection = mongo_db[DADOS]
    mongo_collection.delete_many({})
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(ControllerMaster, port=18850)
    t.start()
