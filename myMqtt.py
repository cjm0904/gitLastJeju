import paho.mqtt.client as mqtt

brkIp = 'mqtt.mirae-eco.com'
brkPort = 1883
brkKeepAlive = 60
tls_arr = ''

mqClient = mqtt.Client()

try:
    mqClient.connect(brkIp, brkPort, brkKeepAlive)
    mqClient.reconnect()
except ConnectionError as e:
    print("cannot connect with MQTT server")
