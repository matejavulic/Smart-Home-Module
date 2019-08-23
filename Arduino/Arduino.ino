#include <DHsT.h>

#include "TimerOne.h"
#include <LiquidCrystal.h> 
LiquidCrystal lcd(12, 11, 5, 4, 3, 2); 
float temperatura=0; 
int tempPin = A1; 
int fotoPin = A0; 
int sensorValue = 0; 
int trigPin = 7; 
int echoPin = 8; 
int br = 0;
long duration, distance; 
long staraVrednost = 0;
volatile int f = 1;

#define DHTTYPE DHT11
#define DHTPIN 10
DHT dht(DHTPIN, DHTTYPE);


void flag(){
  
  f = 1;
  
  }

void setup() { 

Timer1.initialize(500000);
Timer1.attachInterrupt(flag);

 
 Serial.begin(9600); 
 pinMode(trigPin, OUTPUT); 
 
 
 pinMode(echoPin, INPUT); 
 
 lcd.begin(16,2); 
 lcd.print("POSLEDNJA KONF:"); 
 lcd.setCursor(0, 1); 
 dht.begin();

} 

 
void tempSenzor(){ 
 //temperatura = analogRead(tempPin); 
 //temperatura = temperatura * 0.48828125;
 //Serial.println(temperatura); 
 Serial.println(dht.readTemperature());
 } 
 
void ultraZvucniSenzor() { 
 digitalWrite(trigPin, LOW); 
 delayMicroseconds(2); 
 digitalWrite(trigPin, HIGH); 
 delayMicroseconds(10); 
 digitalWrite(trigPin, LOW); 
 duration = pulseIn(echoPin, HIGH); 
 distance = duration*0.034/2;
 if (distance<250){
  Serial.println(distance);
  staraVrednost = distance;
  br = 0;  
 }
 else{
  br = br + 1;
  if (br<=20)
    Serial.println(staraVrednost);
  else
    Serial.println(1001);
 }
  
} 
 
void fotootpornikSenzor() { 
sensorValue = analogRead(fotoPin);  
Serial.println(sensorValue);  
 
} 
 
 
void loop() { 

 if(f == 1){
   Serial.println("Novi podaci: ");
   tempSenzor(); 
   fotootpornikSenzor();
   ultraZvucniSenzor();
   f = 0;
   }  
 if(Serial.available()){ 
  lcd.setCursor(1, 1); 
  lcd.print(Serial.readString()); 
  } 
 delay(500); 
}
