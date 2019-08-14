from multiprocessing import Process
import senData as sData
import ctrl
import serial
import subMqtt
#import controller

if __name__ == '__main__':
#    ctrl.readThread()
#    instll = controller.addressing(num)
#    installChk = controller.installtionChk(num)
#    p = Process(target = controller.keepAddressing, args=num)
#    q = Process(target = sData.sensingData)
    
#    p.start()
#    q.start()
#    p.join()
#    q.join()

#    sData.sensingData()


    myread = Process(target=ctrl.readThread)
    sensingData = Process(target=sData.sensingData)
    readMqtt = Process(target=subMqtt.recvData)

    myread.start()
    sensingData.start()
    readMqtt.start()

    myread.join()
    sensingData.join()
    readMqtt.join()
    
