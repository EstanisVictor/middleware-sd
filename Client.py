import os
import time
import rpyc
class Client:
    def __init__(self, name):
        self.proxy = None
        self.name = name
        self.id_client = None

    def verifica_conexao_controller(self):
        return self.proxy.root.verifica_conexao_controller()

    def join_controller(self):
        return self.proxy.root.join_controller()

    def join_system(self, host, port):
        self.proxy = rpyc.connect(host, port, config={'allow_public_attrs': True})
        self.id_client = self.proxy.root.join_system(self.name)

    def ligar_desligar_lampada(self, comando):
        return self.proxy.root.ligar_desligar_lampada(comando)

    def monitorar(self):
        return self.proxy.root.monitorar()

def menu(client: Client):
    # limpar_console()
    try:
        print(
            '1 - Monitorar o sistema'
            '\n2 - Sair do chat'
            '\n3 - Enviar mensagem'
        )
        print("=================================================")
        op = input('Digite uma dessas opções: ')
        return op
    except KeyboardInterrupt:
        exit(0)


def main(client: Client):
    try:
        while client.verifica_conexao_controller():
            print("Controller está disponível")
            if client.join_controller():
                print("Conectado ao controller")
                while True:
                    op = menu(client)
                    try:
                        if op == '1':
                            print("Precione CTRL+C para sair do monitoramento")
                            try:
                                while True:
                                    for dado in client.monitorar():
                                        print(dado)
                                    time.sleep(1)
                            except KeyboardInterrupt:
                                pass
                        elif op == '2':
                            print("Saindo do chat")
                            break
                        elif op == '3':
                            comando = input('Digite o comando: ')
                            client.ligar_desligar_lampada(comando)
                    except Exception as ex:
                        print(ex)
                        break
        print("Controller não está disponível")
    except Exception as ex:
        print("Controller não está disponível")
        print(ex)
        exit(0)



if __name__ == '__main__':
    name = input('Digite seu nome: ')
    client = Client(name)
    client.join_system('localhost', 18850)

    main(client)