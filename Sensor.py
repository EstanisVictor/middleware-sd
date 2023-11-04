import paho.mqtt.client as mqtt
import time
import random

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
TOPIC_SENSOR = "/Sensor"
TOPIC_CONTROLLER = "/Controller"

class SensorLuminosidade:
    def __init__(self):
        self.broker = mqtt.Client()
        self.broker.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
        self.hora = 6
        self.luminosidade = 100

    def publicar_luminosidade(self):
        while True:

            if self.hora == 24:
                mensagem = f"00:00/{self.luminosidade}"
            else:
                mensagem = f"{self.hora}:00/{self.luminosidade}"
            self.broker.publish(TOPIC_SENSOR, mensagem.encode())
            print(f"Sensor: Publicando -> {mensagem}")

            if self.hora == 24:
                self.hora = 0
            if self.hora >= 2 and self.hora < 3:
                self.luminosidade += 15
            elif self.hora >= 3 and self.hora < 4:
                self.luminosidade += 20
            elif self.hora >= 4 and self.hora < 5:
                self.luminosidade += 25
            elif self.hora >= 5 and self.hora < 6:
                self.luminosidade += 40
            else:
                self.luminosidade -= 5

            self.hora += 1
            time.sleep(1.5)

    def assinar_luminosidade(self):
        self.broker.subscribe(TOPIC_SENSOR)
        self.broker.loop_forever()

if __name__ == '__main__':
    sensor = SensorLuminosidade()
    sensor.publicar_luminosidade()