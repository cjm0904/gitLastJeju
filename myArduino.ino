#include <SoftwareSerial.h>
#include <Arduino_JSON.h>

#define CNUM "C001"

SoftwareSerial mySerial(2,3);
int stdCo = 600;
int stdhmd = 600;
unsigned long coTime = 0;
unsigned long hmTime = 0;
unsigned long tmTime = 0;

int hm=0, hx=0; //습도 최대,최소
int cm=0, cx=0; //이산화탄소 최대 최소
int tm=0, tx=0; //온도 최대,최소

int notiTime = 3000;

int coFlag = false; //0 :  off, 1 : on
int hmFlag = false;
int tmFlag = false;

int relayVentil1 = 5;
int relayVentil2 = 6;
int relayCo = 7;
int relayHm1 = 8;
int relayHm2 = 9;


//GW에서 min, max 값 등의 유저지정값 받아오는 함수
void readStd(){
  String myStd = mySerial.readString();
  JSONVar myObject =  JSON.parse(myStd);
  if(CNUM==myObject["deviceNo"]){
    hm = atoi(myObject["hm"]);
    hx = atoi(myObject["hx"]);
    cm = atoi(myObject["cm"]);
    cx = atoi(myObject["cx"]);
    tm = atoi(myObject["tm"]);
    tx = atoi(myObject["tx"]);
    notiTime = atoi(myObject["notiTime"]);
  }
}

void setup()
{
  Serial.begin(9600);
  while (!Serial){
  ;
  }
  mySerial.begin(9600);

  pinMode(relayVentil1, OUTPUT);
  pinMode(relayVentil2, OUTPUT);
  pinMode(relayCo, OUTPUT);
  pinMode(relayHm1, OUTPUT);
  pinMode(relayHm2, OUTPUT);
}
    

void loop(){
  int arr[17];
  int i=0;
  unsigned long now = millis();
  String data = "";
  data += CNUM;
  
  int co2 = 0, temp = 0, humid = 0;
  
  if(mySerial.available()){
    for(i=0; i<sizeof(arr)/sizeof(int);i++){
      arr[i] = mySerial.read();//온습도, CO2 받아옴
      data += arr[i];
//      Serial.print(arr[i]);
//    데이터 깨질 경우 복구처리
      if(i == 16){
        if(arr[16] != 10){
          i=0;
          arr[17] = {0,}; 
        }
        else{
          data += hmFlag;
          data += coFlag;
          Serial.print(data); //데이터 송신
          readStd();
          
          //온습도,이산화탄소 계산
          co2 = (arr[0]-48)*1000 + (arr[1]-48)*100 + (arr[2]-48)*10 + (arr[3]-48); //단위 ppm
          temp = (arr[6]-48)*100 + (arr[7]-48)*10 + (arr[9]-48)*1; // nature temp * 10
          humid = (arr[11]-48)*100 + (arr[12]-48)*10 + arr[14] *1; // nature humidty * 10
          //co2, 가습기 제어 필요
          
          if(co2<cm){
            if(!coFlag){
              //function of operating co2 generator is needed.
              coFlag = true;
              coTime = millis();
              digitalWrite(relayCo,HIGH);
            }else{
              if(now-coTime>(300000)){ // 5 min
                coFlag = false;
                digitalWrite(relayCo,LOW);
              }
            }          
          }

          if(humid<hm){
            if(!hmFlag){
              //function of operationg hm generator is needed.
              hmFlag = true;
              hmTime = millis();
              digitalWrite(relayHm1, HIGH);
              digitalWrite(relayHm2, HIGH);
            }else{
              if(now-hmTime>(300000)){ //5 min
                hmFlag = false;
                digitalWrite(relayHm1, LOW);
                digitalWrite(relayHm2, LOW);
              }
            }
          }

          if(temp<tm){
            if(!tmFlag){
              //function of operating tmgerator is needed.
              tmFlag = true;
              hmTime = millis();
              digitalWrite(relayVentil1, HIGH);
              digitalWrite(relayVentil2, HIGH);
            }else{
              if(now-tmTime>(300000)){
                hmFlag = false;
                digitalWrite(relayVentil1, LOW);
                digitalWrite(relayVentil2, LOW);
              }
            }
          }
          
        }
      }
    }
  }
  arr[17] = {0,}; //초기화
  
  delay(notiTime);
}
