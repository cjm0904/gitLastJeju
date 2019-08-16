#information about mqtt
import paho.mqtt.client as mqtt

#mqtt정보가 들어가있음.
brkIp = 'mqtt.mirae-eco.com'
brkPort = 1883
brkKeepAlive = 60

#mqtt인증서를사용할 경우 변수에 인증서 경로를 넣으면 됨.
tls_arr = ''

mqClient = mqtt.Client()

try:
    mqClient.connect(brkIp, brkPort, brkKeepAlive)
    mqClient.reconnect()
except ConnectionError as e:
    print("cannot connect with MQTT server")
