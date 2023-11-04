import paho.mqtt.client as mqtt
import json

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "/Controller"
timelive = 60

players = {}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Cliente conectou-se ao servidor MQTT.")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Erro de conexão: {rc}")

def on_message(client, userdata, message):
    data = message.payload.decode()
    print(data)

mqtt_server = mqtt.Client()
mqtt_server.on_connect = on_connect
mqtt_server.on_message = on_message

try:
    mqtt_server.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, timelive)
except ConnectionRefusedError:
    print("Erro de conexão: O servidor MQTT não está acessível.")
    exit(1)

mqtt_server.loop_forever()