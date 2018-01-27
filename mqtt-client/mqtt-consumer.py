import paho.mqtt.client as mqtt
from sense_hat import SenseHat 
import json

tracked_object = 'car'
threshold = 3

# The callback for when the client receives a CONNACK response from the server.
def on_connect( client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("tensorplate/samantha/out")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    process_message(str(msg.payload))

def process_message(message):
    
    try:
        payload = json.loads(message)

        if tracked_object in payload.keys():
            qta = payload[tracked_object]
            print_sense(qta >= threshold, qta)
        else:
            print_sense(False, 0)
    except:
        pass

def print_sense(result, qta):
    v = [36, 204, 30]
    r = [230, 5, 5]
    b = [255, 255, 255]

    foreground = b
    if (result):
        background = v
    else:
        background = r
    
    sense.show_letter(str(qta), foreground, background)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("130.211.134.220", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
sense = SenseHat()
client.loop_forever()
