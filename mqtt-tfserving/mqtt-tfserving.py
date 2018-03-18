import paho.mqtt.client as mqtt
import tfs_client as tfs
import time
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
	scoring_server_address = "127.0.0.1:9000"

if os.environ.get('MODEL_NAME') is not None:
    scoring_model = os.environ['MODEL_NAME']
else:
	scoring_model = "model"

if os.environ.get('MODEL_VERSION') is not None:
    scoring_model_version = os.environ['MODEL_VERSION']
else:
	scoring_model_version = "1"


# Mosquitto callbacks
def on_log(client, userdata, level, buf):
    print("log: ", buf)


def on_message(client, userdata, message):
    try:
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)

        # Call the predict_service via gRPC
        response = tfs_client.predict(message.payload)

        # Process response
        processed_response = self.build_response(response)

        # Return result
        mqtt_client.publish("tensorplate/samantha/out", processed_response)

    except:
        print("Unexpected error:", sys.exc_info())
        sys.exit()

def build_response(response):
    return "{cars: 4}"

def on_disconnect(client, userdata,rc=0):
    mqtt_client.loop_stop()

# Instantiate Mosquitto client
mqtt_client = mqtt.Client("P1")
mqtt_client.on_message = on_message
mqtt_client.on_log = on_log
mqtt_client.on_disconnect = on_disconnect

# Instantiate Tensorflow Serving client
tfs_client = tfs.Client(scoring_server_address, scoring_model, 1, True)     # Client(hostport, model, version, check_status)

# Start Mosquitto loop
mqtt_client.connect(mqtt_broker_address, port=mqtt_broker_port)
mqtt_client.subscribe("tensorplate/samantha/in")
mqtt_client.loop_forever()