1) myMQTT.py
   MQTT프로토콜을 이용하하여 데이터를 보내는 중앙 서버에 대한 정보를 포함.
   
2) controller.py
   삼성에서 사용하는 공조기 활용에 대한 function이 있는 코드
   
   (1) gencrc : crc코드를 만들어내는 함수
   (2) monitorinigCommonData : 삼성 공조기 매뉴얼 25페이지 참조
   (3) ctrlIndoorUnit : 삼성 공조기 매뉴얼 40페이지 참조
   (4) ctrlAhuUnit : 삼성 공조기 매뉴얼 49페이지 참조
   (5) addressing : 삼성 공조기 매뉴얼 12페이지 참조
   (6) keepAddressing : 삼성 공조기 매뉴얼 14페이지 참조
   (7) installationChk : 삼성 공조기 매뉴얼 22페이지 참조
   
3) senData.py
   MCU에서 연결된 센서들이 수집한 데이터를 게이트웨이 백업DB에 저장하고 중앙서버로 전송하는 코드 
   
4) subMqtt.py
   서버에서 전송된 설정값을 처리하는 코드
   
   (1) on_connect : topic를 구독하는 함수
   (2) cdnsCallback : cdns계층의 토픽을 구독하였을 때 실행되는 콜백함수
   (3) setCallback : set계층의 토픽을 구독하였을 때 실행되는 콜백함수
   (4) on_message : 토픽으로 들어오는 메시지를 처리하는 함수
   
5) ucu.py
    시리얼 통신을 하는데 필요한 CRC코드를 생성하는 알고리즘을 포함하는 코드 
    
6) __init__.py
    실행파일
    senData와 subMqtt, controller에 포함된 함수가 multiprocess를 통해 돌아간다.
   
       
