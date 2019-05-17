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


def cdnsCallback(client, userdata, msg):
    data = str(msg.payload.decode('utf8')
    myTopic = msg.topic
    deviceNo = myTopic.split('/')[2]
    
    if 'Q' in eval(data).keys():
        sendTopic = 'cdnc/' + myTopic[1] + '/' + myTpic[2]
        qry= 'select MAX(time) from jeju_ack where deviceNo = %s'
    
        with conn.cursor(sql.cursors.DictCursor) as cursor:
            cursor.execute(qry, deviceNo)
            rows = cursor.fetchone()
            now = time.time()
            result = {'t':now, 'cdn':'ON', ackt : row['time']}
    pass


def setCallback(client, userdata, msg): # managing max, min of hm, hx, cm, cx, tm, tx, t, nt (noti_time)
    data = str(msg.payload.decode('utf8'))
    myTopic = msg.topic
    deviceNo = myTopic.split('/')[2]
    data = json.dumps(data)
    qry = 'insert into setting (deviceNo, nt, hm, hx, cm, cx, tm, tx, t) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
    param = (deviceNo, data['nt'], data['hm'], data['hx'], data['cm'], data['cx'], data['tm'], data['tx'], data['t'])
    with conn.cursor() as cursor:
       cursor.execute(qry, param)
       cursor.commit()
    except TypeError as e:
        print(e)
        pass



def recvData():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

#    client.message_callback_add("cdns/S002/#", cdnsCallback)
    client.message_callback_add("set/S002/#", setCallback)
#    client.message_callback_add("")

    client.connect(brkIp, brkPort, brkKeepAlive)
    client.loop_forever()
