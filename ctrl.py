# -*- coding: utf-8 -*-

import serial
import pymysql as sql
import ucu,myMqtt as my
import time, json
import packetUtil as util
import crcCCITT

ser = serial.Serial(port='/dev/ttyUSB1', baudrate=9600, stopbits=1, parity=serial.PARITY_EVEN, bytesize=serial.EIGHTBITS, timeout=3) #Serial 연결정보
conn= sql.connect(host='127.0.0.1', user='root', password='ziumks', db='jeju', charset='utf8') # mysql 연결정보
exitThread = False
line=[]
m=0
result = {'state':None, 'mode':None, 'windVolume':None, 'sTemp':None, 'nTemp':None}
siteNm = "s002" # siteName

# monitoring할때 돌아가는 함수
def readThread(): 
    global exitThread
    
    if ser.is_open:
        while not exitThread:
            buff = int(ser.in_waiting)

            while buff>0:
                recv = ser.read(buff)

                for c in recv:

                    line.append(c)
                    if hex(c) == '0x34':
                       recvParsing(line)
    time.sleep(0.005)
    
# readThread에서 들어오는 데이터를 파싱하여 처리
def recvParsing(rcvPacket: list):
    packetTotalLen = len(rcvPacket)
    try:
        for i in range(0, packetTotalLen):
            stx = rcvPacket[i]

            if stx == 0x32:
                packetLen = util.bytes2ToInt(rcvPacket[i+1:i+3],0) + 2
                if (i+packetLen-1) < packetTotalLen:
                    etxIdx = i + packetLen - 1
                    etx = rcvPacket[etxIdx]
                    if etx == 0x34:
                        body = rcvPacket[i+3: etxIdx-2]
                        crc = rcvPacket[etxIdx-2:etxIdx]
                        crcRcv = util.bytes2ToInt(crc,0)
                        crcCal = crcCCITT.crcb(body)
                        if crcRcv == crcCal:
                            rcvMsg = rcvPacket[i:etxIdx +1]
                            sa = rcvMsg[3:6]
                            da = rcvMsg[6:9]
                            cmd = rcvMsg[9:12]
                            msgLen = rcvMsg[12:13]
                            msg = rcvMsg[13:-3]
                            packetProcess( (m%6)+1, sa, da, cmd, msgLen, msg) 
                            
    except Exception as e:
        print(e)
        pass

# recvParsing에서 파싱한 데이터를 처리하는 함수. DB에 넣거나 mqtt broker로 전송
def packetProcess(num, sa, da, cmd, msgLen, msg):
    global result
    global m
#    print(result)
    if num==sa[1]:
#        print(str(intArrayToHexArray(msg)))

        valueFlag = True
        mqTopic = "mntr/" + siteNm + "/" + str(num) # mqtt Topic
        for i in result.values():
            valueFlag = i and valueFlag # 값이 하나라도 none이 있으면 valueFlag는 None 
        if valueFlag is not None: #result 의 값이 모두 생겼을 때
            try:
                my.mqClient.publish(topic=mqTopic, payload=json.dumps(result), qos=0) # mqtt로 result를 json으로 변환하여 전송
                qry = 'insert into monitoring (time, deviceNo, state, mode, windVolume, sTemp, nTemp)'
                qry += 'values (%s, %s, %s, %s, %s, %s, %s)'
                param = (time.time()*1000, num, result['state'], result['mode'], result['windVolume'], result['sTemp'], result['nTemp']) #DB에 넣을 값으로 sql의 파라미터로 들어간다.

                try:
                    with conn.cursor() as cursor:
                        cursor.execute(qry, param)
                        conn.commit()
                except TypeError as e:
                    print(e)
                    pass
                print(num)
                print(result) 
                result['state']=None
                result['mode']=None
                result['windVolume']=None
                result['sTemp']=None
                result['nTemp']=None # 한 사이클 실행 후 모든result의 값을 초기화
                m+=1 # 한 사이클에 공조기 하나씩 실행한다. 1번->2번 ... -> 6번 순
                time.sleep(60)    
            except ConnectionError as e:
                print(e)
                pass
        else:
#            print(result)
            if sa[0] == 0x20 and sa[1] == num: # 모니터링 데이터를 보고 원하는 데이터의 위치를 찾아 값을 넣음.
                if msgLen[0] == 0x0C and msg[38] == 0x40 and msg[39] == 0x00:
                    result['state'] = str(msg[40])
                    result['mode'] = str(msg[43])
                elif msgLen[0] == 0x10 and  msg[0] == 0x40 and msg[1] == 0x06:
                    result['windVolume']= str(msg[2])
                elif msgLen[0] == 0x0d and msg[18]== 0x42 and msg[19]==0x01:
                    result['sTemp'] = hex2Value(msg[20], msg[21])
                    result['nTemp'] = hex2Value(msg[28], msg[29])



def hex2Value(num1, num2):
    return ((num1 * 256) + num2)

def intArrayToHexArray(b):
   msg = []
   for i in b:
        msg.append("0x%02X" %i)
   return msg 
