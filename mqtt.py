import paho.mqtt.client as mqtt
import time
import requests
import io

# Network configuration
mqtt_broker_address = "130.211.134.220"
mqtt_broker_port = 1883

scoring_server_address = "http://localhost:80"
scoring_server_port = 80

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
