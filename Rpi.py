import RPi.GPIO as GPIO 
import serial 
import http.client 
import urllib

import threading 
  
import string 
import imaplib 
import smtplib
from datetime import datetime

from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
import time 
import email
from time import strftime

import requests 
from email.parser import Parser 

cntTemp = 0
cntOsv = 0
cntRaz = 0

i = 0
ii = 0

prosecnaTemp = 0
prosecnaOsv = 0
prosecnaRaz = 0

data=0
flagStart = 0
flagZelena = 0
flagPrviPodatak = 0
PodaciCnt = 0
proveraEnabled = 1

flagPeriodTemp = 0
flagPeriodOsv = 0
flagPeriodRaz = 0

prosecnaTemp = 0
prosecnaOsv = 0
prosecnaRaz = 0
#vremena za slanje izvestaja 
vremeTemperature   = 0    
vremeRazdaljina   = 0    
vremeOsvetljenosti = 0     

# srednje vrednosti podataka  
temperaturaSrednja = 0     
razdaljinaSrednja   = 0     
osvetljenostSrednja = 0    

#brojac 
brojac = 0 
# merenje vremena 

timerTemp = 0
timerRaz = 0
timerOsv = 0

#lsusb
#cd /dev pa onda ls tty* pa ukljucim Arduino u USB pa opet ls tty* i vidim razl.
ser = serial.Serial('/dev/ttyACM0',9600)
LEDCrvena = 3 
LEDZelena = 21

mail = imaplib.IMAP4_SSL('imap.gmail.com') 
mail.login("singidunumrpi@gmail.com", "password")

GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False) 
GPIO.setup(LEDCrvena, GPIO.OUT) 
GPIO.output(LEDCrvena, GPIO.LOW)  
GPIO.setup(LEDZelena, GPIO.OUT) 
GPIO.output(LEDZelena, GPIO.LOW)

def ZelenaUgasi():
    GPIO.output(LEDZelena, GPIO.LOW)

def CrvenaUgasi():
    global proveraEnabled
    GPIO.output(LEDCrvena, GPIO.LOW)
    proveraEnabled = 1
    
def izvestajTemperatura():
 
  #funkcija za slanje izvestaja putem imejla 
    fromaddr = "singidunumrpi@gmail.com" 
    toaddr = "singidunumrpi@gmail.com" 
    msg = MIMEMultipart() 
    msg['From'] = fromaddr 
    msg['To'] = toaddr 
    msg['Subject'] = "Temperatura" 
      #vremeTemperature uzimamo iz konf maila, a temperaturaKonfig je prosecna temp 
    body = "Средња температура у последњих "+str(vremeTemperature) +" минута је " + str(temperaturaSrednja) + " степени С." 
    msg.attach(MIMEText(body, 'plain'))               
    server = smtplib.SMTP('smtp.gmail.com', 587) 
    server.starttls() 
    server.login(fromaddr, "password") 
    text = msg.as_string() 
    server.sendmail(fromaddr, toaddr, text) 
    server.quit()

def izvestajOsvetljenost(): 
  #funkcija za slanje izvestaja putem imejla
    fromaddr = "singidunumrpi@gmail.com" 
    toaddr = "singidunumrpi@gmail.com" 
    msg = MIMEMultipart() 
    msg['From'] = fromaddr 
    msg['To'] = toaddr 
    msg['Subject'] = "Osvetljenost"        
    body = "Средња осветљеност у последњих "+str(vremeOsvetljenosti) +" минута је "+str(osvetljenostSrednja) + " lux." 
    msg.attach(MIMEText(body, 'plain'))      
    server = smtplib.SMTP('smtp.gmail.com', 587) 
    server.starttls() 
    server.login(fromaddr, "password") 
    text = msg.as_string() 
    server.sendmail(fromaddr, toaddr, text) 
    server.quit()  

def izvestajRazdaljina(): 
  #funkcija za slanje izvestaja putem imejla 
    fromaddr = "singidunumrpi@gmail.com" 
    toaddr = "singidunumrpi@gmail.com" 
    msg = MIMEMultipart() 
    msg['From'] = fromaddr 
    msg['To'] = toaddr 
    msg['Subject'] = "Razdaljina"       
    body = "Средње растојање у последњих "+str(vremeRazdaljina) +" минута је "+str(razdaljinaSrednja) + " cm." 
    msg.attach(MIMEText(body, 'plain'))          
    server = smtplib.SMTP('smtp.gmail.com', 587) 
    server.starttls() 
    server.login(fromaddr, "password") 
    text = msg.as_string() 
    server.sendmail(fromaddr, toaddr, text) 
    server.quit()

def CheckMail():
    global i, ii, vremeTemperature,vremeRazdaljina, vremeOsvetljenosti
    global osvetljenostSrednja, temperaturaSrednja, razdaljinaSrednja
    global prosecnaTemp, prosecnaOsv, prosecnaRaz
    global cntTemp, cntOsv, cntRaz, flagZelena
    global timerTemp, timerRaz, timerOsv
    global flagPeriodTemp, flagPeriodOsv, flagPeriodRaz
    mail.list() 
    mail.select('inbox')
    
    result, podaci = mail.uid('search', None, '(SUBJECT "Posalji" UNSEEN)')
    result1, podaci1 = mail.uid('search', None, '(SUBJECT "Konfiguracija" UNSEEN)')
    i = len(podaci[0].split())
    ii = len(podaci1[0].split()) 
    for x in range(i):
        latest_email_uid = podaci[0].split()[x]
      #uzimanje mejla 
        result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)') 
        raw_email = email_data[0][1] 
        raw_email_string = raw_email.decode('utf-8') 
        email_message = email.message_from_string(raw_email_string)
      #prolazak kroz mejl 
        for part in email_message.walk():  
            if part.get_content_type() == "text/plain": 
                body = part.get_payload(decode=True) 
                #telo mejla 
                bodystr=str(body)
                prvi,drugi = bodystr.split("b'")
                split = drugi.split("\\r\\n")
                count = split.__len__()
                for z in range(count-1):
                    word = split[z]
                    if word=="Temperatura":
                        if flagPeriodTemp==1:
                            print("Температура у режиму периода")
                        else:
                            print("Температура послата")
                            vremeTemperature = int(timerTemp/60)
                            temperaturaSrednja = prosecnaTemp/cntTemp
                            temperaturaSrednja = round(temperaturaSrednja,2)
                            izvestajTemperatura()
                            timerTemp = 0
                            temperaturaSrednja = 0
                            prosecnaTemp = 0
                            cntTemp = 0

                    if word=="Razdaljina":
                        
                        if flagPeriodRaz==1:
                            print("Раздаљина у режиму периода")
                        else:
                            print("Растојање послато")
                            vremeRazdaljina = int(timerRaz/60)
                            razdaljinaSrednja =  prosecnaRaz/cntRaz
                            razdaljinaSrednja = round(razdaljinaSrednja,2)
                            izvestajRazdaljina()
                            timerRaz = 0
                            razdaljinaSrednja = 0
                            prosecnaRaz = 0
                            cntRaz = 0

                    if word=="Osvetljenost":
                        if flagPeriodOsv==1:
                            print("Осветљеност у режиму периода")
                        else:
                            print("Осветљеност послата")
                            vremeOsvetljenosti = int(timerOsv/60)
                            osvetljenostSrednja =  prosecnaOsv/cntOsv
                            osvetljenostSrednja = round(osvetljenostSrednja,2)
                            izvestajOsvetljenost()
                            timerOsv = 0
                            osvetljenostSrednja = 0
                            prosecnaOsv = 0
                            cntOsv = 0
 
    for x in range(ii):
        
        latest_email_uid = podaci1[0].split()[x]
      #uzimanje mejla
        result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)') 
        raw_email = email_data[0][1] 
        raw_email_string = raw_email.decode('utf-8') 
        email_message = email.message_from_string(raw_email_string)
      #prolazak kroz mejla 
        for part in email_message.walk():  
            if part.get_content_type() == "text/plain": 
                body = part.get_payload(decode=True) 
                #telo mejla
                bodystr=str(body)
                prvi,drugi = bodystr.split("b'")
                split = drugi.split("\\r\\n")
                count = split.__len__()
                konftime = datetime.now().strftime("%H:%M:%S")
                ser.write(konftime.encode())
                flagZelena = 1
                for z in range(count-1):
                    word = split[z]
                    a,b = word.split(":")
                    b,c = b.split(",")
                    if a =="Temperatura":
                        if b=="zahtev":
                            vremeTemperature = 0
                            flagPeriodTemp = 0
                            prosecnaTemp = 0
                            cntTemp = 0
                            temperaturaSrednja = 0
                            timerTemp = 0
                            print("Температура [захтев]")
    
                            
                        elif b=="period":
                            vremeTemperature = int(c)
                            flagPeriodTemp = 1
                            timerTemp = 0
                            temperaturaSrednja = 0
                            prosecnaTemp = 0
                            cntTemp = 0
                            print("Температура [период]")

                    if a =="Osvetljenost":
                        if b=="zahtev":
                            vremeOsvetljenosti = 0
                            flagPeriodOsv = 0

                            prosecnaOsv = 0
                            cntOsv = 0
                            osvetljenostSrednja = 0
                            timerOsv = 0
                            print("Осветљеност [захтев]")
        
                        elif b=="period":
                            flagPeriodOsv = 1
                            vremeOsvetljenosti = int(c)

                            timerOsv = 0
                            osvetljenostSrednja = 0
                            prosecnaOsv = 0
                            cntOsv = 0
                            print("Оветљеност [период]")

                    if a =="Razdaljina":
                        if b=="zahtev":
                            vremeRazdaljina = 0
                            flagPeriodRaz = 0

                            timerRaz = 0
                            razdaljinaSrednja = 0
                            prosecnaRaz = 0
                            cntRaz = 0
                            print("Раздаљина [захтев]")

                        elif b=="period":
                            
                            vremeRazdaljina = int(c)
                            flagPeriodRaz = 1
                            timerRaz = 0
                            razdaljinaSrednja = 0
                            prosecnaRaz = 0
                            cntRaz = 0
                            print("Раздаљина [период]")
                            
    threading.Timer(5,CheckMail).start()

CheckMail()
while True:
    
    data = ser.readline()
    Podaci = str(data)
    #print(data)
    b,a = Podaci.split("b'")
    NoviPodaci,c = a.split("\\r\\n")

    if flagStart==1:
        PodaciCnt = PodaciCnt + 1
        if PodaciCnt==1:
            prosecnaTemp = prosecnaTemp + float(NoviPodaci)
            #print((NoviPodaci))
            cntTemp+=1
        if PodaciCnt==2:
            prosecnaOsv = prosecnaOsv + int(NoviPodaci)
            cntOsv+= 1
        if PodaciCnt==3:
            if proveraEnabled ==1:
                
                if (int(NoviPodaci) < 5):
                    GPIO.output(LEDCrvena, GPIO.HIGH)
                    proveraEnabled = 0
                    requests.post("https://maker.ifttt.com/trigger/RAZDALJINA/with/key/el_U2_uSB9g3xcCYZVfQMWSPRadAE6CgZA7nzHCqpaF") 
                    threading.Timer(15,CrvenaUgasi).start()
                
            prosecnaRaz = prosecnaRaz + int(NoviPodaci)
            print(int(NoviPodaci))
            cntRaz+= 1
            PodaciCnt=0
            flagStart=0
            flagPrviPodatak = 1
            
            brojac += 0.5        
            timerTemp += 0.5
            timerRaz += 0.5
            timerOsv += 0.5
            #print(brojac)

                    
    if NoviPodaci =="Novi podaci: ":
        flagStart = 1

    if flagZelena:
        GPIO.output(LEDZelena, GPIO.HIGH)
        threading.Timer(10,ZelenaUgasi).start()
        flagZelena = 0

        
    if flagPeriodTemp==1:    
        if (float(timerTemp) == int(vremeTemperature*60)):
            temperaturaSrednja =  prosecnaTemp/cntTemp
            temperaturaSrednja = round(temperaturaSrednja,2)
            izvestajTemperatura() 
            print("Слање температуре на",vremeTemperature,"минут/а")
            timerTemp = 0
            temperaturaSrednja = 0
            prosecnaTemp = 0
            cntTemp = 0

    if flagPeriodRaz==1:
        
        if (float(timerRaz) == int(vremeRazdaljina*60)):
            razdaljinaSrednja =   prosecnaRaz/cntRaz
            razdaljinaSrednja = round(razdaljinaSrednja,2)
            izvestajRazdaljina() 
            print("Слање раздаљине на",vremeRazdaljina,"минут/а") 
            timerRaz = 0
            razdaljinaSrednja = 0
            prosecnaRaz = 0
            cntRaz = 0

    if flagPeriodOsv==1:
        
        if (float(timerOsv) == int(vremeOsvetljenosti*60)):
            osvetljenostSrednja = prosecnaOsv/cntOsv
            osvetljenostSrednja = round(osvetljenostSrednja,2)
            izvestajOsvetljenost() 
            print("Слање осветљености на", vremeOsvetljenosti, "минут/а")
            timerOsv = 0 
            osvetljenostSrednja = 0
            prosecnaOsv = 0
            cntOsv = 0
        

