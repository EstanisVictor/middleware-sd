import time
import rpyc

class Client:
    def __init__(self, name):
        self.proxy = None
        self.name = name
        self.id_client = None

    def conectar_controller(self):
        return self.proxy.root.conectar_controller()

    def join_system(self, host, port):
        self.proxy = rpyc.connect(host, port, config={'allow_public_attrs': True})
        self.id_client = self.proxy.root.join_system(self.name)

    def monitorar(self):
        return self.proxy.root.monitorar()

    def send_message(self, room_name, message):
        try:
            return self.proxy.root.send_message(self.id_client, room_name, message)
        except Exception as e:
            print(e)
            exit(0)

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
        while client.conectar_controller():
            print("Conectado ao Controller")
            while True:
                op = menu(client)
                try:
                    if op == '1':
                        print("Precione CTRL+C para sair do monitoramento")
                        try:
                            while True:
                                print(client.monitorar())
                                time.sleep(1)
                        except KeyboardInterrupt:
                            with open("log.txt", "w") as file:
                                file.write("")
                            pass
                    elif op == '2':
                        print("Saindo do chat")
                        break
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
    client.join_system('localhost', 18860)

    main(client)