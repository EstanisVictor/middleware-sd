import os
import time
import uuid
import paho.mqtt.client as mqtt
import rpyc
from cryptography.fernet import Fernet
from pymongo import MongoClient

from module import key

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
TOPIC_CONTROLLER = "/Controller"
SENSOR = "/Sensor"
ATUADOR = "/Atuador"
MONGO_HOST = os.environ.get("MONGO_URI")
MONGO_NAME = "IOT"
DADOS_COLLECTION = "DADOS"
comandoCliente = ""

class Controller2(rpyc.Service):
    def __init__(self):
        self.broker = mqtt.Client()
        self.broker.on_connect = self.on_connect_mqtt
        self.broker.on_message = self.on_message_mqtt
        self.conn = None
        self.messageCLientMonitorar = None
        self.mongo_cliente = MongoClient(MONGO_HOST)
        self.mongo_db = self.mongo_cliente[MONGO_NAME]
        self.mongo_collection = self.mongo_db[DADOS_COLLECTION]
        self.key = key

    def on_connect_rpc(self, conn):
        print(f'Conexão RPC recebida {conn}')
        self.conn = conn

    def encrypt_data(self, data):
        return Fernet(self.key).encrypt(data.encode())

    def exposed_join_system(self, name):
        user_id = uuid.uuid4()
        print(f' {user_id} Usuário {name} conectado')
        return str(user_id)

    def on_connect_mqtt(self, client, userdata, flags, rc):
        if rc == 0:
            print("Controller conectou-se ao servidor MQTT.")
            client.subscribe(ATUADOR)
            client.subscribe(SENSOR)
        else:
            print(f"Erro de conexão MQTT: {rc}")

    def on_message_mqtt(self, client, userdata, message):
        global comandoCliente
        if comandoCliente == "":
            if message.topic == SENSOR:
                mensagemSensor = message.payload.decode().split("/")
                if int(mensagemSensor[1]) <= 40:
                    self.broker.publish(TOPIC_CONTROLLER, "on".encode())
                    print(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% ligada")
                    data = f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% ligada"
                    self.save_data({"Sensor": self.encrypt_data(data)})
                    # with open("../log.txt", "a") as file:
                    #     file.write(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% ligada\n")
                else:
                    self.broker.publish(TOPIC_CONTROLLER, "off".encode())
                    print(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% desligada")
                    data = f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% desligada"
                    self.save_data({"Sensor": self.encrypt_data(data)})
                    # with open("../log.txt", "a") as file:
                    #     file.write(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% desligada\n")
            elif message.topic == ATUADOR:
                mensagemAtuador = message.payload.decode()
                print(f"Lâmpada: {mensagemAtuador}")
                data = f"{mensagemAtuador}\n"
                self.save_data({"Lâmpada": self.encrypt_data(data)})
                # with open("../log.txt", "a") as file:
                #     file.write(f"Atuador: {mensagemAtuador}\n")
        elif comandoCliente == "on":
            if message.topic == SENSOR:
                self.broker.publish(TOPIC_CONTROLLER, "on".encode())
                mensagemSensor = message.payload.decode().split("/")
                if int(mensagemSensor[1]) == 100:
                    comandoCliente = ""
                    self.broker.publish(TOPIC_CONTROLLER, "off".encode())
                    print(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% desligada")
                    data = f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% desligada"
                    self.save_data({"Sensor": self.encrypt_data(data)})
                else:
                    print(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% ligada")
                    data = f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% ligada"
                    self.save_data({"Sensor": self.encrypt_data(data)})
            elif message.topic == ATUADOR:
                mensagemAtuador = message.payload.decode()
                data = f"{mensagemAtuador}"
                self.save_data({"Lâmpada": self.encrypt_data(data)})
                print(f"Lâmpada: {mensagemAtuador}")

        elif comandoCliente == "off":
            if message.topic == SENSOR:
                self.broker.publish(TOPIC_CONTROLLER, "off".encode())
                mensagemSensor = message.payload.decode().split("/")
                print(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% desligada")
                data = f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% desligada"
                self.save_data({"Sensor": self.encrypt_data(data)})
                if int(mensagemSensor[1]) == 35:
                    comandoCliente = ""
            elif message.topic == ATUADOR:
                mensagemAtuador = message.payload.decode()
                data = f"{mensagemAtuador}\n"
                self.save_data({"Lâmpada": self.encrypt_data(data)})
                print(f"Lâmpada: {mensagemAtuador}")

    def exposed_ligar_desligar_lampada(self, comando):
        global comandoCliente
        comandoCliente = comando

    def exposed_conectar_mqtt(self):  # Método que faz o controller se conectar ao broker
        self.broker.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
        self.start_mqtt_loop()

    def exposed_monitorar(self):
        dados_monitorados = self.obter_dados_monitorados()
        return dados_monitorados
        # with open("../log.txt", "r") as file:
        #     return file.read()

    def start_mqtt_loop(self):
        self.broker.loop_start()

    def start_rpc_server(self):
        from rpyc.utils.server import ThreadedServer
        t = ThreadedServer(Controller2, port=18862)
        t.start()

    def save_data(self, data):
        try:
            self.mongo_collection.insert_one(data)
        except Exception as e:
            print(f"Erro ao salvar no banco de dados: {e}")

    def obter_dados_monitorados(self):
        dados_monitorados = list(self.mongo_collection.find())
        resultado = []

        for documento in dados_monitorados:
            for chave, valor_criptografado in documento.items():
                if chave == '_id':
                    pass
                else:
                    # Descriptografar os dados usando a chave
                    fernet = Fernet(self.key)
                    valor_descriptografado = fernet.decrypt(valor_criptografado).decode()
                    # Verificar se a chave está relacionada a um Sensor ou Atuador
                    tipo = 'Sensor' if 'Sensor' in chave else 'Lâmpada'
                    value = tipo + ": " + valor_descriptografado
                    resultado.append(value)

        return resultado

if __name__ == '__main__':

    atuador = Controller2()
    atuador.start_rpc_server()