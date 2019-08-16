# -*- coding: utf-8 -*-
from serial import Serial
import myMqtt as mqtt
import time, json
import pymysql as sql
# import airQ

co2 = 0
temperature = 0
humidity = 0
ser = Serial("/dev/ttyUSB0", 9600, timeout=1) # zigbee serial을 가져옴.
conn = sql.connect(host='127.0.0.1', user='root', password='ziumks', db='jeju', charset='utf8')
siteNm = "s002" #site name

def sensingData():
    row = '' # 밑에서 select한 결과를 넣기 위한 변수
    try:
        while True:
            wn1, wn2, wn3 = 0,0,0 #1,2,3번 컨네이터에 대한 warning
            # db에서 사용자가 설정한 온습도의 최대 최소를 select
            arr = []
            try:
                data = ser.readline().decode('utf-8')
#                print(data)
            except UnicodeDecodeError as e :
                continue
            # 한 디바이스에서 날라오는 데이터의 길이는 111
            if data.__len__() != 111:
                pass
            else:
                print(data)
#                ser.write(str(row).encode('utf8'))
                cNum = (data[0:4]).lower()
                # cNum에 맞는 정보를 zigbee로 전송. 여기서 해당 컨테이너에 정보가 들어간다.
                with conn.cursor(sql.cursors.DictCursor) as cursor:
                    qry = 'select * from setting where deviceNo = %s and t = (select MAX(t) from setting where deviceNo=%s) '
                    cursor.execute(qry,(cNum,cNum))
                    row = cursor.fetchone()
                    if row:
                        row = json.dumps(row)
                        print("ROW : ", row)
                        print("ROW endcode : ", str(row).encode('utf-8'))
                        ser.write(str(row).encode('utf-8'))
                #zigbee로 송신된 데이터를 파싱하여 각각의 변수에 담음
                rawC1 = (data[4:12])
                rawT1 = (data[14:24])
                rawH1 = (data[26:34])
                # data[34:38] 은 crc코드

                rawC2 = (data[38:46])
                rawT2 = (data[48:58])
                rawH2 = (data[60:68])
                
                rawC3 = (data[72:80])
                rawT3 = (data[82:92])
                rawH3 = (data[94:102])

                c1 = (int(rawC1[0:2]) - 0x30) * 1000 + (int(rawC1[2:4]) - 0x30) * 100 + (int(rawC1[4:6]) - 0x30) * 10 + (int(rawC1[6:8]) - 0x30)
                t1 = ((int(rawT1[2:4]) - 0x30) * 10 + (int(rawT1[4:6]) - 0x30) * 1 + (int(rawT1[8:10]) - 0x30) * 0.1) * 10
                h1 = ((int(rawH1[0:2]) - 0x30) * 10 + (int(rawH1[2:4]) - 0x30) * 1 + (int(rawH1[6:8]) - 0x30) * 0.1) * 10
                
                c2 = (int(rawC2[0:2]) - 0x30) * 1000 + (int(rawC2[2:4]) - 0x30) * 100 + (int(rawC2[4:6]) - 0x30) * 10 + (int(rawC2[6:8]) - 0x30)
                t2 = ((int(rawT2[2:4]) - 0x30) * 10 + (int(rawT2[4:6]) - 0x30) * 1 + (int(rawT2[8:10]) - 0x30) * 0.1) * 10
                h2 = ((int(rawH2[0:2]) - 0x30) * 10 + (int(rawH2[2:4]) - 0x30) * 1 + (int(rawH2[6:8]) - 0x30) * 0.1) * 10
                
                c3 = (int(rawC3[0:2]) - 0x30) * 1000 + (int(rawC3[2:4]) - 0x30) * 100 + (int(rawC3[4:6]) - 0x30) * 10 + (int(rawC3[6:8]) - 0x30)
                t3 = ((int(rawT3[2:4]) - 0x30) * 10 + (int(rawT3[4:6]) - 0x30) *1 + (int(rawT3[8:10]) - 0x30) * 0.1) * 10  
                h3 = ((int(rawH3[0:2]) - 0x30) * 10 + (int(rawH3[2:4]) - 0x30) *1 + (int(rawH3[6:8]) - 0x30) * 0.1) * 10  
                # co2, temperature, humidity 값 사용방법은 매뉴얼 참고

#                c3 += int((c1-c2)/2)
#                t3 += int((t1-t2)/2)
#                h3 += int((h1-h2)/2)
                
                # 해당 컨테이너 장비가 켜져 있는지 꺼져 있는지에 대한 값으로 0이면 off, 1이면 on
                hq = int(data[-5])
                cq = int(data[-4])
                tq = int(data[-3])
              
                # 데이터가 꼬여서 들어오는 경우가 있기 때문에 이를 확인하는 과정이 필요.
                if data[-6] != str(0):
                    continue
                elif data[-6] == str(0):
                    wn = 0

#                 value3 = None
#                 if cNum == 'c0O1':
#                     value3 = airQ.senAirQ(3)
#                 elif cNum == 'c002':
#                     value3 = airQ.senAirQ(6)
#                 elif cNum == 'c003':
#                     value3 = airQ.senAirQ(9)
                    # 이상한 값으로 들어왔을 경우 서버에서 에러처리를 쉽게 하기위해 -999로 담아 전송
                    # -999로 값을 보내고, wn에 에러가 있음을 표시. 위와 마찬가지로 에러가 없으면 0, 있으면 1
                    if int(c1) < 0 and int(t1) < 0 and int(h1) < 0:
                        c1 = -999
                        t1 = -999
                        h1 = -999
                        wn1 = 1
                    if int(c2) < 0 and int(t2) < 0 and int(h2) < 0:
                        c2 = -999
                        t2 = -999
                        h2 = -999
                        wn2 = 1
                    if int(c3) < 0 and int(c3) < 0 and int(h3) < 0:
                        c3 = -999
                        t3 = -999
                        h3 = -999
                        wn3 = 1

                    # wn 1,2,3,을 비트연산
                    wn = (wn3 << 2) + (wn2 << 1) + (wn1 << 0)
                    now = round(time.time())
                    result = {'tm': now, 't1': int(t1), 't2': int(t2), 't3': int(t3),
                              'h1': int(h1), 'h2': int(h2), 'h3': int(h3),
                              'c1': int(c1), 'c2': int(c2), 'c3': int(c3),
                              'wn': int(wn), 'hq': hq, 'cq': cq, 'tq': tq
                              }  # 0 : off, 1: on
                    #센싱된 결과값을 DB에저장
                    qry = 'insert into jeju_sensor(id, area, time, humidity, temperature1, temperature2, co2, checking) values(%s, %s, %s, %s, %s, %s, %s, %s)'
                    param = (cNum, cNum, now, humidity, temperature, temperature, co2, 0)
                    mqTopic = 'msr' + '/' + siteNm + '/' + cNum
                    print(str(cNum) + str(result))

                # mqtt로 데이터를 서버에 전송
                    try:
                        mqtt.mqClient.publish(topic=mqTopic, payload=json.dumps(result), qos=0)
                        print("MQTT sending Sucess")
                    except ConnectionError as e:
                        print("error : " + str(e))
                        pass

                # 데이터를 GW db에 저장
                    try:
                        with conn.cursor() as cursor:
                            cursor.execute(qry, param)
                            conn.commit()
                    except TypeError as e:
                        print(str(e))
                    time.sleep(10)
    except KeyboardInterrupt:
        ser.close()
