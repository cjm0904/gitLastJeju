import serial, json, time
import ucu, mymqtt as my

ser = serial.Serial(port='', baudrate=9600, stopbits=1, parity=serial.PARITY_EVEN, bytesize=serial.EIGHTBITS)

buff = 1024

ackFront = 0x32, 0x00, 0x0E, 0x20
ackBack = 0x6A, 0xEE, 0xC0, 0x16, 0x00, 0x00

def gencrc(input):
    out = ucu.crcb(input)
    out1 = int(out / 16**2)
    out2 = int(out % 16**2)
    out += out1
    out += out2
    out += ox34
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
        dataset += order['contorlMode']

    if 'airVolume' in eval(order).keys():
        dataset += 0x40, 0x06
        dataset += order['airVolume']

    if 'swing' in eval(order).keys():
        dataset += 0x40, 0x11
        dataset += order['swing']

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
        ack = ackFront + outdoor + indoor + ackBack
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
    ser.write(dta)
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

