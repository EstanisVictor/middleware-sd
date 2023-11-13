import time

import paho.mqtt.client as mqtt

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC_ATUADOR = "/Atuador"
TOPIC_CONTROLLER = "/Controller"

class AtuadorLampada:
    def __init__(self):
        self.broker = mqtt.Client()
        self.messageController = ""

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Atuador conectou-se ao Controller MQTT.")
            client.subscribe(TOPIC_CONTROLLER)
        else:
            print(f"Erro de conexão: {rc}")

    def on_message(self, client, userdata, message):
        self.messageController = message.payload.decode()
        print(f"Mensagem Controller: {message.payload.decode()}")

        if self.messageController == "on":
            mensagem = "ligada"
            self.broker.publish(MQTT_TOPIC_ATUADOR, mensagem.encode())
        elif self.messageController == "off":
            mensagem = "desligada"
            self.broker.publish(MQTT_TOPIC_ATUADOR, mensagem.encode())

if __name__ == '__main__':
    atuador = AtuadorLampada()
    atuador.broker.on_connect = atuador.on_connect
    atuador.broker.on_message = atuador.on_message
    try:
        atuador.broker.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    except ConnectionRefusedError:
        print("Erro ao conectar ao servidor MQTT.")
        exit(1)

    atuador.broker.loop_forever()