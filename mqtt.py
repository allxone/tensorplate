import paho.mqtt.client as mqtt
import time
import requests
import io
import os

# Network configuration
if os.environ.get('MQTT_SERVER') is not None:
    mqtt_broker_address = os.environ['MQTT_SERVER']
else:
	mqtt_broker_address = "127.0.0.1"

if os.environ.get('MQTT_SERVER_PORT') is not None:
    mqtt_broker_port = int(os.environ['MQTT_SERVER_PORT'])
else:
	mqtt_broker_port = 1883

if os.environ.get('FLASK_PORT') is not None:
    scoring_server_address = "http://localhost:" + os.environ['FLASK_PORT']
else:
    scoring_server_address = "http://localhost:8888"

# Instantiate Mosquitto client
client = mqtt.Client("P1")
client.connect(mqtt_broker_address, port=mqtt_broker_port)


# Mosquitto callbacks
def on_log(client, userdata, level, buf):
    print("log: ", buf)


def on_message(client, userdata, message):
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)
    f = open('./test.jpg', 'wb')
    f.write(message.payload)
    f.close()
    foto = {'image': open('./test.jpg', 'rb')}
    response = requests.post(scoring_server_address + '/scoreImage', files=foto)
    print(response.status_code, response.reason)
    client.publish("tensorplate/samantha/out", str(response.json()))
    print(response.json())


# Start Mosquitto loop
client.loop_start()
client.subscribe("tensorplate/samantha/in")
client.on_message = on_message
client.on_log = on_log

#client.publish("coverage-hackathon", "OFF")

_never_true = False
while not _never_true:
    time.sleep(1)

client.loop_stop()
