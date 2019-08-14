import paho.mqtt.client as mqtt
import myMqtt as my
import pymysql as sql
import packetUtil as util
import ctrl
import json

ser = ctrl.ser
brkIp = my.brkIp
brkPort = my.brkPort
brkKeepAlive = my.brkKeepAlive
tls_arr = my.tls_arr  

conn = sql.connect(host = '127.0.0.1', user = 'root', password = 'ziumks', db = 'jeju', charset = 'utf8')

def on_connect(client, userdata, flags, rc):
    print("connected with result code " + str(rc))
    client.subscribe("mss/#")
    client.subscribe("cntrl/#")


def on_message(client, userdata, msg):
    data = str(msg.payload.decode('utf8'))
    print(data)

def cdnsCallback(client, userdata, msg):
    data = str(msg.payload.decode('utf8'))
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
            my.mqClient.publish(topic=sendTopic, payload=json.dumps(result), qos=0 )
    pass


def setCallback(client, userdata, msg): # managing max, min of hm, hx, cm, cx, tm, tx, t, nt (noti_time)
    data = str(msg.payload.decode('utf8'))
    myTopic = msg.topic
    deviceNo = myTopic.split('/')[2]
    data = json.loads(data)
    qry = 'insert into setting (deviceNo, hm, hx, cm, cx, tm, tx, t) values (%s, %s, %s, %s, %s, %s, %s, %s)'
    param = (deviceNo, data['hd'], data['hu'], data['cd'], data['cu'], data['td'], data['tu'], data['tm'])
    try:
        with conn.cursor() as cursor:
            cursor.execute(qry, param)
            conn.commit()
    except TypeError as e:
        print("ERROR:")
        print(e)
        pass


def cntrl(client, userdata, msg):
    data = json.loads(str(msg.payload.decode('utf8')))
    myTopic = msg.topic
    deviceNo = myTopic.split('/')[2]
    setTemp = data['sTemp']
    setTempHead = int(data['sTemp'] / 256)
    setTempTail = int(data['sTemp'] % 256)

    if data['state'] == 0:
        sa = [0x6A, 0xEE, 0xFF]
        cmd = [0xC0, 0x13, 0x00]
        numMsg = [0x01]
        msgSet = [0x40,0x00, 0x00]
        da = [0x20, deviceNo, deviceNo]
        packet = util.gen_packet(sa, da, cmd, numMsg, msgSet, True)
        sendMsg = bytes(packet)
        ser.write(sendMsg)

    if data['state'] == 1:
        sa = [0x6A, 0xEE, 0xFF]
        cmd = [0xC0, 0x13, 0x00]
        numMsg = [0x01]
        msgSet = [0x40, 0x00, 0x01]
        da = [0x20, deviceNo, deviceNo]
        packet = util.gen_packet(sa, da, cmd, numMsg, msgSet, True)
        sendMsg = bytes(packet)
        ser.write(sendMsg)
     
        cSa = [0x6A, 0xEE, 0xFF]
        cCmd = [0xC0, 0x13, 0x00]
        cNumMsg = [0x02]
        cMsgSet = [0x40, 0x00, 0x01, 0x42, setTempHead, setTempTail]
        cDa = [0x20, deviceNo, deviceNo]
        cPacket = util.gen_packet(cSa, cDa, cCmd, cNumMsg, cMsgSet, True)
        cSendMsg = bytes(cPacket)
        ser.write(cSendMsg)


def recvData():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

#    client.message_callback_add("cdns/S002/#", cdnsCallback)
    client.message_callback_add("mss/#", setCallback)
    client.message_callback_add("cntrl/#", cntrl)
#    client.message_callback_add("")
    client.connect(brkIp, brkPort, brkKeepAlive)
    client.loop_forever()
