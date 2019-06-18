import serial
import myMqtt as mqtt
import time, json
import pymysql as sql
# import airQ

co2 = 0
temperature = 0
humidity = 0
ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
conn = sql.connect(host='127.0.0.1', user='root', password='ziumks', db='jeju', charset='utf8')
siteNm = 's002'


def sensingData():
    row = ''
    wn1, wn2, wn3 = 0,0,0
    try:
        while True:
            # db에서 사용자가 설정한 온습도의 최대 최소를 select
            #            arr = []
            #            selQry = 'select deviceNo, nt, hm, hx, cm, cx, tm, tx, t from setting where t =(select max(t) from setting)'
            #            with conn.cursor(sql.cursors.DictCursor) as cursor:
            #                cursor.execute(selQry)
            #                row = cursor.fetchone()
            try:
                data = ser.readline().decode('utf-8')
            except UnicodeDecodeError as e:
                continue
            # 한 디바이스에서 날라오는 데이터의 길이는 77
            if data.__len__() != 77:
                pass
            else:
                #                ser.write(row)
                cNum = (data[0:4]).lower()
                rawC1 = (data[4:12])
                rawT1 = (data[14:24])
                rawH1 = (data[26:34])
                # data[34:38] 은 crc코드

                rawC2 = (data[38:46])
                rawT2 = (data[48:58])
                rawH2 = (data[60:68])

                c1 = (int(rawC1[0:2]) - 0x30) * 1000 + (int(rawC1[2:4]) - 0x30) * 100 + (int(rawC1[4:6]) - 0x30) * 10 + (int(rawC1[6:8]) - 0x30)
                t1 = ((int(rawT1[2:4]) - 0x30) * 10 + (int(rawT1[4:6]) - 0x30) * 1 + (int(rawT1[8:10]) - 0x30) * 0.1) * 10
                h1 = ((int(rawH1[0:2]) - 0x30) * 10 + (int(rawH1[2:4]) - 0x30) * 1 + (int(rawH1[6:8]) - 0x30) * 0.1) * 10
                c2 = (int(rawC2[0:2]) - 0x30) * 1000 + (int(rawC2[2:4]) - 0x30) * 100 + (int(rawC2[4:6]) - 0x30) * 10 + (int(rawC2[6:8]) - 0x30)
                t2 = ((int(rawT2[2:4]) - 0x30) * 10 + (int(rawT2[4:6]) - 0x30) * 1 + (int(rawT2[8:10]) - 0x30) * 0.1) * 10
                h2 = ((int(rawH2[0:2]) - 0x30) * 10 + (int(rawH2[2:4]) - 0x30) * 1 + (int(rawH2[6:8]) - 0x30) * 0.1) * 10
                # co2, temperature, humidity 값 사용방법은 매뉴얼 참고
                hq = data[72]
                cq = data[73]
                tq = data[74]

                wn = 0

#                 value3 = None
#                 if cNum == 'c0O1':
#                     value3 = airQ.senAirQ(3)
#                 elif cNum == 'c002':
#                     value3 = airQ.senAirQ(6)
#                 elif cNum == 'c003':
#                     value3 = airQ.senAirQ(9)

                if int(c1) == 0 and int(t1) == 0 and int(h1) == 0:
                    c1 = None
                    t1 = None
                    h1 = None
                    wn1 = 1
                if int(c2) == 0 and int(t2) == 0 and int(h2) == 0:
                    c2 = None
                    t2 = None
                    h2 = None
                    wn2 = 1

                if value3 is None:
                    wn3 = 1
                wn = (wn3 << 3) + (wn2 << 2) + (wn1 << 1)
                now = round(time.time())
                result = {'tm': now, 't1': int(t1), 't2': int(t2), 't3': 0,
                          'h1': int(h1), 'h2': int(h2), 'h3': 0,
                          'c1': int(c1), 'c2': int(c2), 'c3': 0,
                          'wn': bin(wn), 'hq': hq, 'cq': cq, 'tq': tq
                          }  # 0 : off, 1: on
                #               print(result)

                qry = 'insert into jeju_sensor(id, area, time, humidity, temperature1, temperature2, co2, checking) values(%s, %s, %s, %s, %s, %s, %s, %s)'
                param = (cNum, siteNm, now, humidity, temperature, temperature, co2, 0)
                mqTopic = 'msr' + '/' + siteNm + '/' + cNum
                #                print(str(cNum) + str(result))

                # mqtt로 데이터를 서버에 전송
                try:
                    mqtt.mqClient.publish(topic=mqTopic, payload=json.dumps(result), qos=0)
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

    except KeyboardInterrupt:
        ser.close()
