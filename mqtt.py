import paho.mqtt.client as mqtt

brkIp = '45.120.69.86'
brkPort = 1883
brkKeepAlive = 60
tls_arr = ''

mqClient = mqtt.Client()
try:
    mqClient.connect(brkIp, brkPort, brkKeepAlive)
    mqClient.reconnect()
except ConnectionError:
    print("cannot connect with MQTT Server")
