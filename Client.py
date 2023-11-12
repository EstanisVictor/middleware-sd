import os
import time
import rpyc
import subprocess
import tkinter as tk
from threading import Thread

root = tk.Tk()

class Client:
    def __init__(self, name, master):
        self.proxy = None
        self.name = name
        self.id_client = None
        self.master = master
        self.master.title("OUTPUT")
        self.output_text = tk.Text(master, wrap="word")
        self.output_text.pack(expand=1, fill="both")
        self.start_thread()
    def start_thread(self):
        self.thread = Thread(target=self.read_input, daemon=True)
        self.thread.start()

    def read_input(self):
        while True:
            for dado in client.monitorar():
                self.update_output(dado)
                print(dado)

    def update_output(self, text):
        self.output_text.insert(tk.END, text+"\n")
        self.output_text.see(tk.END)

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

    def abrir_terminal(self):
        comando = "echo 'Olá, mundo!'"
        try:
            # Executa o comando no terminal
            subprocess.run(comando, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            # Trata erros, se houver
            print(f"Erro ao executar o comando: {e}")

def menu(client: Client):
    # limpar_console()
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
                                while True:
                                    for dado in client.monitorar():
                                        print(dado)
                                    time.sleep(1)
                                client.abrir_terminal()
                            except KeyboardInterrupt:
                                pass
                        elif op == '2':
                            comando = input('Digite o comando: ')
                            client.ligar_desligar_lampada(comando)
                        elif op == '3':
                            print("Saindo...")
                            time.sleep(2)
                            break
                    except Exception as ex:
                        print(ex)
                        break
        print("Controller não está disponível")
    except Exception as ex:
        print("Controller não está disponível")
        print(ex)
        exit(0)

    root.mainloop()

if __name__ == '__main__':

    name = input('Digite seu nome: ')
    client = Client(name, root)

    client.join_system('localhost', 18850)

    main(client)