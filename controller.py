import serial, json, time
import ucu, mymqtt as my
import gc

ser = serial.Serial(port='', baudrate=9600, stopbits=1, parity=serial.PARITY_EVEN, bytesize=serial.EIGHTBITS, timeout=3)

buff = 1024

ackFront = 0x32, 0x00, 0x0E, 0x20
ackBack = 0x6A, 0xEE, 0xC0, 0x16, 0x00, 0x00

def gencrc(input):
    out = ucu.crcb(input)
    out1 = int(out / 16**2)
    out2 = int(out % 16**2)
    out += out1
    out += out2
    out += 0x34
    return out


def monitoringCommonData():
    outAddr = 0
    msg = ser.readline().decode()
    data = msg.split(' ')
    msgSet = data[13:-3]

    if data[9] == 'C0' and data[10] == '14':
        outAddr = data[11]
    rslt = json.dumps({'outdoorAddr': outAddr, 'msgSet': msgSet})
    return rslt


def ctrlIndoorUnit(outdoor, indoor, order):
    data = [0x32, 0x00, 0x32, 0x6A, 0xEE, 0xFF, 0x20, outdoor, indoor, 0xC0, 0x13, 0x00, 0x0A]
    dataset = []

    if 'buzzer' in eval(order).keys():
        dataset += 0x40, 0x50
        dataset += order['buzzer']

    if 'control' in eval(order).keys():
        dataset += 0x40, 0x00
        dataset += order['control']

    if 'controlMode' in eval(order).keys():
        dataset += 0x40, 0x01
        dataset += order['controlMode']

    if 'airVolume' in eval(order).keys():
        dataset += 0x40, 0x06
        dataset += order['airVolume']

    if 'swing' in eval(order).keys():
        dataset += 0x40, 0x11
        dataset += order['swing']

    if 'alarmReset' in eval(order).keys():
        dataset += 0x40, 0x25
        dataset += order['alarmReset']

    if 'temperature' in eval(order).keys():
        dataset += 0x42, 0x01
        dataset += order['temperature']

    if 'coolTemperature' in eval(order).keys():
        dataset += 0x42, 0x2A
        dataset += order['coolTemperature']

    if 'warmTemperature' in eval(order).keys():
        dataset += 0x42, 0x2B
        dataset += order['warmTemperature']

    if 'restrictRemocon' in eval(order).keys():
        dataset += 0x04, 0x09
        dataset += order['restrictRemocon']

    if 'SPI' in eval(order).keys():
        dataset += 0x40, 0x43
        dataset += order['SPI']

    if 'windFree' in eval(order).keys():
        dataset += 0x40, 0x60
        dataset += order['windFree']

    if 'fan' in eval(order).keys():
        dataset += 0x40, 0x12
        dataset += order['fan']

    data += dataset
    data = gencrc(data)

    ser.write(data)
    recv = ser.readline()
    if not recv:
        #TODO : ERROR MSG
        pass
    else:
    iii    ack = ackFront + outdoor + indoor + ackBack
        ack = gencrc(ack)
        if recv == ack:
            msg = json.dumps({'t':time.time(), 'ack':'T'})
            my.mqClient.publish(topic='', payload=msg, qos=0)
            #TODO :save ACK log in DB 
            #TODO : use jemalloc
            pass
        else:
            msg = json.dumps({'t':time.time(), 'ack':'F'})
            my.mqClient.publish(topic='', payload=msg, qos=0)
            #TODO : save ACK log in DB
            pass


def ctrlAhuUnit(outdoor, indoor, order):
    data = [0x32, 0x00, 0x26, 0x6A, 0xEE, 0xFF, 0x20, outdoor, indoor, 0xC0, 0x13, 0x00, 0x6]
    dataset = []

    if 'control' in eval(order).keys():
        dataset += 0x40, 0x00
        dataset += order['control']

    if 'controlMode' in eval(order).keys():
        dataset += 0x40, 0x01
        dataset += order['controlMode']

    if 'temperture' in eval(order).keys():
        dataset += 0x42, 0x01
        dataset += order['temperature']

    if 'coolTemperature' in eval(order).keys():
        dataset += 0x42, 0x2A
        dataset += order['coolTemperature']

    if 'warmTemperature' in eval(order).keys():
        dataset += 0x42, 0x2B
        dataset += order['warmTemperature']

    if 'restrictRemocon' in eval(order).keys():
        dataset += 0x04, 0x09
        dataset += order['restrictRemocon']

    data += dataset
    data = gencrc(data)
    ser.write(data)
    recv = ser.readline()
    if not recv:
        #TODO : Error MSG
        pass
    else:
        ack = ackFront + outdoor + indoor + ackBack
        ack = gencrc(ack)
        if recv == ack:
            msg = json.dumps({'t':time.time(), 'ack':'T'})
            my.mqClient.publish(topic='', payload=msg, qos=0)
            #TODO : save ACK log in DB
            #TODO : use jemalloc
            pass
        else:
            msg = json.dumps({'t':time.time(), 'ack':'F'})
            my.mqClient.publish(topic='', payload=msg, qos=0)
            #TODO : save ACK log in DB
            pass

def addressing(num):

    print('addressing starts')
    #STEP1
    addrData = [0x32, 0x00, 0x14, 0x6A, 0xEE, 0xFF, 0xB0, 0xFF, 0xFF, 0xC0, 0x01, num, 0x01, 0x04, 0x08, 0xff, 0xff, 0xff, 0xff]
    addrData = gencrc(addrData)
    priorAddr=-1

    for i in range(0:10):
        ser.write(addrData.encode())
        recv = ser.readline()
        outAddr = recv[17]
        if priorAddr==outAddr:
            print("installation error. check Address")
        #TODO : save outAddr Number

        priorAddr=outAddr
        time.sleep(3)
    #STEP2
    while True:
        reqAllUnitPckt = gencrc([0x32, 0x00, 0x11, 0x6A, 0xEE, 0xFF, 0xB0, 0xFF, 0xFF, 0xC0, 0x14, num, 0x01, 0x00 ])
        ser.write(reqAllUnitPckt.encode())
        #STEP3
        rev=ser.readline()
        
        if rev is None:
            print("Addressing is finished")
            break
        else:
            rndmAddr = [rev[19], rev[20], rev[21]]
            #STEP4
            sndPckt = 0x32, 0x00, 0x27, 0x6A, 0xEE, 0xFF
            sndPckt += rndmAddr
            sndPckt += 0xC0, 0x12, num, 0x05, 0x20, 0x04, 0x03, 
            sndPckt += 0x04, 0x18, rev[18], rev[19], rev[20], rev[21] #Random Address
            sndPckt += 0x02, 0x17, rev[24], rev[25] # Network Address
            sndPckt += 0x04, 0x17, rev[28], rev[29], rev[30], rev[31] # Origin Address
            sndPckt += 0x04, 0x19, rev[34], rev[35], rev[36], rev[37]
            ser.write(sndPckt.encode())
            #STEP5
            recvPckt = ser.readline()
            if recvPckt is not None:
                #TODO : save outAddr Num


    pass


def keepAddresing(num):
    while True:
        reqAllUnitPckt = gencrc([0x32, 0x00, 0x11, 0x6A, 0xEE, 0xFF, 0xB0, 0xFF, 0xFF, 0xC0, 0x14, num, 0x01, 0x00])
        ser.write(reqAllUnitPckt.encode())
        time.sleep(61)


def installationChk(outdoor):
    chkPckt = gencrc([0x32, 0x00, 0x11, 0x6A, 0xEE, 0xFF, 0xB0, 0xFF, 0x10, 0xC0, 0x11, outdoor, 0x01, 0x20, 0x10, 0xFF])
    ser.write(chkPckt.encode())
    recv = ser.readline()
    if 16 <= recv[-3] < 32:
        pass
    elif 32 <= recv[-3] < 64:
        pass
    elif 64 <= recv[-3] < 128:
        pass
    elif 128 <= recv[-3] < 256:
        pass


