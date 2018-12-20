import paho.mqtt.client as mqtt

brkIp = '45.120.69.86'
brkPort = 1883
brkKeepAlive = 60
tls_arr = ''

def on_connect(client, userdata, flags, rc):
    print("connected with result code " + str(rc))
    client.subscribe("sf/tsite/cntr001")


def on_message(client, userdata, msg):
    data = str(msg.payload.decode('utf8'))
    print(eval(data)['t1'])



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(brkIp, brkPort, brkKeepAlive)
client.loop_forever()


