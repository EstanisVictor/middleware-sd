import socket
import uuid
import rpyc
class ControllerMaster(rpyc.Service):
    def __init__(self):
        self.controllerPort = 18861
        self.proxy = None
        self.host = 'localhost'

    def exposed_join_system(self, name):
        user_id = uuid.uuid4()
        return str(user_id)

    def exposed_join_controller(self): #Função para conectar ao controller
        self.proxy = rpyc.connect(self.host, self.controllerPort)
        self.conectar_mqtt()
        return True
    def exposed_verifica_conexao_controller(self):
        self.controllerPort = 18861
        if self.verifica_conexao_server(self.host, self.controllerPort):  # Checando primeiro controller
            print("Conectado ao controller 1")
            return True
        else:
            self.controllerPort = 18862
            if self.verifica_conexao_server(self.host, self.controllerPort):  # Checando segundo controller
                print("Conectado ao controller 2")
                return True
            else:
                return False
    def monitorar(self): #Para acessar os controllers
        return self.proxy.root.monitorar()

    def exposed_monitorar(self): #Para responder ao cliente
        return self.monitorar()
    def verifica_conexao_server(self, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((host, port))
            return True
        except (ConnectionRefusedError, socket.timeout):
            return False
    def conectar_mqtt(self): #Decide qual controller vai publicar e assinar os tópicos
        return self.proxy.root.conectar_mqtt()

if __name__ == '__main__':
    print("Iniciando Controller Master")
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(ControllerMaster, port=18850)
    t.start()
