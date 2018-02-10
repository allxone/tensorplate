import paho.mqtt.client as mqtt
import time
import requests
import io
import os
import sys

# Network configuration
if os.environ.get('MQTT_SERVER') is not None:
    mqtt_broker_address = os.environ['MQTT_SERVER']
else:
	mqtt_broker_address = "127.0.0.1"

if os.environ.get('MQTT_SERVER_PORT') is not None:
    mqtt_broker_port = int(os.environ['MQTT_SERVER_PORT'])
else:
	mqtt_broker_port = 1883

if os.environ.get('SCORING_ADDRESS') is not None:
    scoring_server_address = os.environ['SCORING_ADDRESS']
else:
	scoring_server_address = "http://127.0.0.1:80"

# Mosquitto callbacks
def on_log(client, userdata, level, buf):
    print("log: ", buf)


def on_message(client, userdata, message):
    try:
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
    except:
        print("Unexpected error:", sys.exc_info())
        sys.exit()

def on_disconnect(client, userdata,rc=0):
    client.loop_stop()

# Instantiate Mosquitto client
client = mqtt.Client("P1")

client.on_message = on_message
client.on_log = on_log
client.on_disconnect = on_disconnect

# Start Mosquitto loop
client.connect(mqtt_broker_address, port=mqtt_broker_port)
client.subscribe("tensorplate/samantha/in")
client.loop_forever()