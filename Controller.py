import time
import uuid
import paho.mqtt.client as mqtt
import rpyc

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
TOPIC_CONTROLLER = "/Controller"
SENSOR = "/Sensor"
ATUADOR = "/Atuador"


class Controller(rpyc.Service):
    def __init__(self):
        self.broker = mqtt.Client()
        self.broker.on_connect = self.on_connect_mqtt
        self.broker.on_message = self.on_message_mqtt
        self.broker.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
        self.conn = None
        self.messageCLientMonitorar = None

    def on_connect_rpc(self, conn):
        print(f'Conexão RPC recebida {conn}')
        self.conn = conn

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

        if message.topic == SENSOR:
            mensagemSensor = message.payload.decode().split("/")
            if int(mensagemSensor[1]) <= 40:
                self.broker.publish(TOPIC_CONTROLLER, "on".encode())
                print(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% ligada")
                with open("log.txt", "a") as file:
                    file.write(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% ligada\n")
            else:
                self.broker.publish(TOPIC_CONTROLLER, "off".encode())
                print(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% desligada")
                with open("log.txt", "a") as file:
                    file.write(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% desligada\n")
        elif message.topic == ATUADOR:
            mensagemAtuador = message.payload.decode()
            print(f"Atuador: {mensagemAtuador}")
            with open("log.txt", "a") as file:
                file.write(f"Atuador: {mensagemAtuador}\n")

    def exposed_monitorar(self):
        with open("log.txt", "r") as file:
            return file.read()

    def exposed_rpc_method(self, arg1, arg2):
        # Lógica para operações RPC
        pass

    def start_mqtt_loop(self):
        self.broker.loop_start()

    def start_rpc_server(self):
        from rpyc.utils.server import ThreadedServer
        t = ThreadedServer(Controller, port=18861)
        t.start()

if __name__ == '__main__':
    atuador = Controller()
    atuador.start_mqtt_loop()
    atuador.start_rpc_server()