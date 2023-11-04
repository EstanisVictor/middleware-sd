import paho.mqtt.client as mqtt

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
TOPIC_CONTROLLER = "/Controller"
SENSOR = "/Sensor"
ATUADOR = "/Atuador"

class Controller:
    def __init__(self):
        self.broker = mqtt.Client()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Controller conectou-se ao servidor MQTT.")
            client.subscribe(ATUADOR)
            client.subscribe(SENSOR)
        else:
            print(f"Erro de conexão: {rc}")

    def on_message(self, client, userdata, message):

        if message.topic == SENSOR:
            mensagemSensor = message.payload.decode().split("/")
            if int(mensagemSensor[1]) <= 40:
                self.broker.publish(TOPIC_CONTROLLER, "on".encode())
                print(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% ligada")
            else:
                self.broker.publish(TOPIC_CONTROLLER, "off".encode())
                print(f"Hora: {mensagemSensor[0]} | Luminosidade: {mensagemSensor[1]}% desligada")

        elif message.topic == ATUADOR:
            mensagemAtuador = message.payload.decode()
            print(f"Atuador: {mensagemAtuador}")


if __name__ == '__main__':
    atuador = Controller()
    atuador.broker.on_connect = atuador.on_connect
    atuador.broker.on_message = atuador.on_message
    try:
        print("Conectando ao servidor MQTT...")
        atuador.broker.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    except ConnectionRefusedError:
        print("Erro ao conectar ao servidor MQTT.")
        exit(1)

    atuador.broker.loop_forever()