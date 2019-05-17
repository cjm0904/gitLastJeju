from multiprocessing import Process
import senData as sData
#import controller

if __name__ == '__main__':
    num = 3 # setting address
#    instll = controller.addressing(num)
#    installChk = controller.installtionChk(num)
#    p = Process(target = controller.keepAddressing, args=num)
#    q = Process(target = sData.sensingData)

    
#    p.start()
#    q.start()
    
#    p.join()
#    q.join()


    sData.sensingData()
