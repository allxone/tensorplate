import paho.mqtt.client as mqtt
import json

mqtthost = "104.154.62.50"
mqttqueue = "tensorplate/samantha/out"
tracked_object = 'car'
threshold = 3

# The callback for when the client receives a CONNACK response from the server.
def on_connect( client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(mqttqueue)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    process_message(str(msg.payload))

def process_message(message):
    try:
        payload = json.loads(message)
        print(payload)
        if tracked_object in payload.keys():
            qta = payload[tracked_object]
            print("{}: {}".format(tracked_object, qta))
        else:
            print("{}: {}".format(tracked_object, "missing"))
    except:
        print('exception')
        pass


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtthost, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
#sense.set_rotation(270)
client.loop_forever()
