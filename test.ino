#include <SoftwareSerial.h>
#define CNUM "C001"

SoftwareSerial mySerial(2,3);
int stdCo = 600;
int stdhmd = 600;
unsigned long coTime = 0;
unsigned long hmTime = 0;

void setup()
{
  Serial.begin(9600);
  while (!Serial){
  ;
  }
  mySerial.begin(9600);
}
    

void loop(){
  int arr[17];
  int i=0;
  unsigned long now = millis();
  String data = "";
  data += CNUM;
  
  int co2 = 0, temp = 0, humid = 0;
  
  boolean coFlag = false; //False :  off, True : on
  boolean hmFlag = false;
  
  if(mySerial.available()){
    for(i=0; i<sizeof(arr)/sizeof(int);i++){
      arr[i] = mySerial.read();
      data += arr[i];
//      Serial.print(arr[i]);
      if(i == 16){
        if(arr[16] != 10){
          i=0;
          arr[17] = {0,}; 
        }
        else{
          Serial.print(data);
          co2 = (arr[0]-48)*1000 + (arr[1]-48)*100 + (arr[2]-48)*10 + (arr[3]-48);
          temp = (arr[6]-48)*100 + (arr[7]-48)*10 + (arr[9]-48)*1; // nature temp * 10
          humid = (arr[11]-48)*100 + (arr[12]-48)*10 + arr[14] *1; // nature humidty * 10
          
          if(co2<stdCo){
            if(!coFlag){
              //function of operating co2 generator is needed.
              coFlag = true;
              coTime = millis();
            }else{
              if(now-coTime>(5*1000*60)){ // 5 min
                coFlag = false;
              }
            }          
          }

          if(humid<stdhmd){
            if(!hmFlag){
              //function of operationg hm generator is needed.
              hmFlag = true;
              hmTime = millis();
            }else{
              if(now-hmTime>(5*1000*60)){ //5 min
                hmFlag = false;
              }
            }
          }
          
        }
      }
    }
  }
  arr[17] = {0,};
  delay(3000);
}