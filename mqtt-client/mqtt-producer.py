import paho.mqtt.publish as publish

publish.single("tensorplate/samantha/out", "payload", hostname="130.211.134.220")
