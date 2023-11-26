import time
import rpyc
import tkinter as tk
from threading import Thread

from cryptography.fernet import Fernet
from module import key

root = tk.Tk()


class Client:
    def __init__(self, name, master):
        self.proxy = None
        self.name = name
        self.id_client = None
        self.master = master
        self.master.title(self.name)
        self.output_text = tk.Text(master, wrap="word")
        self.output_text.pack(expand=1, fill="both")
        self.stop_thread = False
        self.changeController = False
        self.key = key

    def obter_dados_monitorados(self, dados_monitorados):
        resultado = []
        for criptografado in dados_monitorados:
            fernet = Fernet(self.key)
            valor_descriptografado = fernet.decrypt(criptografado).decode()
            if valor_descriptografado.find("Hora"):
                pattern = "Lâmpada: " + valor_descriptografado
                resultado.append(pattern)
            else:
                pattern = "Sensor: " + valor_descriptografado
                resultado.append(pattern)

        return resultado

    def start_thread(self):
        self.thread = Thread(target=self.read_input, daemon=True)
        self.thread.start()

    def read_input(self):
        self.stop_thread = False
        while not self.stop_thread:
            dado = self.obter_dados_monitorados(self.monitorar())

            if self.changeController:
                print("Controller desconectado")
                root.quit()
                return

            if dado is not None:
                if len(dado) == 1:
                    self.update_output(dado)
                else:
                    for d in dado:
                        self.update_output(d)
            time.sleep(1)

    def stop_thread_func(self):
        self.stop_thread = True

    def update_output(self, text):
        try:
            self.output_text.insert(tk.END, text + "\n")
            self.output_text.see(tk.END)
        except Exception as ex:
            pass

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
        vetor = []
        try:
            time.sleep(0.5)
            return self.proxy.root.monitorar()
        except Exception as ex:
            self.stop_thread_func()
            self.changeController = True
            return vetor

        # if len(vetor) == 1:
        #     return [vetor[-1]]
        # elif len(vetor) > 1:
        #     return vetor[-2:]
        # else:
        return vetor


def menu(client: Client):
    try:
        print(
            '1 - Monitorar o sistema'
            '\n2 - Acender/Apagar manualmente a lâmpada'
            '\n3 - Sair...'
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
                                client.start_thread()
                                root.mainloop()
                            except Exception as ex:
                                print(ex)
                                break
                            except KeyboardInterrupt:
                                client.stop_thread_func()
                                pass
                        elif op == '2':
                            comando = input('Digite o comando: ')
                            client.ligar_desligar_lampada(comando)
                        elif op == '3':
                            print("Saindo...")
                            time.sleep(2)
                            exit(0)
                    except Exception as ex:
                        print(ex)
                        break

                    if client.changeController:
                        client.changeController = False
                        root.quit()
                        print("Mudando de controller")
                        break
        print("Controller não está disponível")
    except KeyboardInterrupt:
        exit(0)
    except Exception as ex:
        print("Controller não está disponível")
        print(ex)
        exit(0)


if __name__ == '__main__':
    name = input('Digite seu nome: ')
    client = Client(name, root)

    client.join_system('localhost', 18850)

    main(client)
