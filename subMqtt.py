import paho.mqtt.client as mqtt
import myMqtt as my
import pymysql as sql


brkIp = my.brkIp
brkPort = my.Port
brkKeepAlive = my.brkKeepAlive
tls_arr = my.tls_arr

conn = sql.connect(host = '127.0.0.1', user = 'root', password = 'ziumks', db = 'jeju', charset = 'utf8')

def on_connect(client, userdata, flags, rc):
    print("connected with result code " + str(rc))
    client.subscribe("cdns/T12/#")


def on_message(client, userdata, msg):
    data = str(msg.payload.decode('utf8'))

    if 'period' in eval(data).keys():
        print("check period")
        qry = 'update response set period = (%s)'
        param = data['period']

        try:
            with conn.cursor() as cursor:
                cursor.execute(qry, param)
                conn.commit()
        except TypeError as e:
            print(e)
    
    if 'abc' not in eval(data).keys():
        pass


def recvData():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(brkIp, brkPort, brkKeepAlive)
    client.loop_forever()

