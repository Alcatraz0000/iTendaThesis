# Created at 2021-05-05 10:36:10.271778
# iTenda
# Sica Ferdinando 0612704522
# Turi Vito 0612704343


import streams
import hcsr04
#threading
import threading
import Timers
import buzzerSong
import stepperMotor
import json
import datetime


# import the http module
import requests


streams.serial()


from mqtt import mqtt
from wireless import wifi
from espressif.esp32net import esp32wifi as wifi_driver

#pin fotoresistore 
pinMode(D4, INPUT)

#funzione per il controllo dell'orario corrente con gli orari di chiusura e apertura della tenda
#ed eventuale set dell'operazione da effettuare.
def checkHours():
    while True:
         global operation
         global causa
         print("Verifico l'orario di chiusura e apertura")
         response = requests.get("http://just-the-time.appspot.com/")
         date = response.content
         date = date[:16] + "+00:00"
         date = (datetime.fromisoformat(str(date))).add(datetime.timedelta(hours=2)).tuple()
         if (date[3] - int(orariochiusura[:2])== 0) and (date[4] - int(orariochiusura[3:5]) == 0):
             print("chiudo tenda causa orario")
             causa = "Orario"
             operation = -1
         if (date[3] - int(orarioapertura[:2])== 0) and (date[4] - int(orarioapertura[3:5]) == 0):
             print("apro tenda causa orario")
             causa = "Orario"
             operation = 1
         print("Ho verificato l'orario di chiusura e apertura")
         sleep(50000)
     

wifi_driver.auto_init()

#credenziali per accesso ad adafruit
ADAFRUIT_IO_USERNAME = "ferdisca"
ADAFRUIT_IO_KEY = "aio_HAOz19teT87nUjDMEUpkQAqMSE66"
Adaclient = mqtt.Client("zerynth-mqtt",True)
Localclient = mqtt.Client("zerynth-mqtt",True)

api_key = "4764a5fe50f436e82b6549401576b198"

ip = "http://82.48.172.49:3308/connessionedb.php" 


username = "asdasd" #quì puoi cambiare l'username

causa = ""



#funzione per l'inizializzazione della tenda in cui vengono prelevate le informazioni
#di controllo dal database per il funzionamento delle varie modalità. 

sleep(100)
def inizializzazioneTenda():
    print("inizializzazione")
    global flag_lux
    global flag_movimento
    global city
    global flag_weather
    global flag_sensore
    global orariochiusura
    global orarioapertura
    global high_tenda
    response = requests.post(ip, {"function":"settings","username":username})
    js = json.loads(response.content)
    print(js)
    if js[0]['funzionamentotenda'] == 'f':
        flag_movimento = 0
        flag_lux = 0
        flag_weather = 0
        flag_sensore = 0
    else:
        flag_movimento = 1
        if js[0]['luminosita'] == 't':
           flag_lux = 1
        else:
            flag_lux = 0
        if js[0]['gesture'] == 't':
           flag_sensore = 1
        else:
            flag_sensore = 0
        if js[0]['meteo'] == 't':
           flag_weather = 1
        else:
            flag_weather = 0
        city = js[0]['citta']
        orarioapertura = js[0]['orarioapertura']
        orariochiusura = js[0]['orariochiusura']
        high_tenda = float (js[0]['altezzatenda']) *30000
        print("inizializzazione completata")
        
        

        
     

#funzione per l'inserimento nel database di un'operazione effettuata sulla tenda 

def sendToDb():
    global operation
    global causa
    if operation == 1:
       requests.post(ip, data={"function":"operation","username":username, "operazione":"apertura", "causa":causa})
    else:
       requests.post(ip, data={"function":"operation","username":username, "operazione":"chiusura", "causa":causa})
    print("Salvataggio dell'operazione nel database completato")
  
#funzione per effettuare l'aggiornamento dell'altezza attuale della tenda nel database
def updateStatus():
    global high_tenda
    if high_tenda > 30000:
        high_tenda = 30000
    if high_tenda < 0 :
        high_tenda = 0
    print("aggiorno il database con un'altezza di ", high_tenda)
    high = round(high_tenda/30000,2)
    response = requests.post(ip, data={"function":"updateHigh","username":username,"high":high})
    print("valore inviato al db: ",high)
    print(json.loads(response.content))
    sleep(1000)

#connessione al wi-fi 
print("Connessione al wi-fi...")
try:
    wifi.link("TIM-19133657",wifi.WIFI_WPA,"TuriFibra2020")
    print("Link Established")
    
except Exception as e:
    print("Problema durante la connessione al wi-fi", e)
    while True:
        sleep(1000)
        
#Questa è la funzione che viene richiamata quando si riceve un messaggio mqtt, in questa funzione è stata aggiunta la chiamata a publish_to_self passando il payload del messaggio e il valore 0 
#vedremo in seguito il significato di quest'ultimo
def print_other(client,data):
    global causa
    message = data['message']
    print("topic: ", message.topic)
    print("payload received: ", message.payload)
    if message.payload == "aggiornamento impostazioni":
        inizializzazioneTenda()
    publish_to_self(message.payload,0)
    causa = "MQTT"
   
#funzione per il controllo delle previsioni meteo tramite richiesta http   
   
def check_weather():
    global city
    try:
            print("Connessione all'url per le previsioni meteo...")
            params = {
                "APPID":api_key,
                "q":city   # <-----  your city
            }
            url="http://api.openweathermap.org/data/2.5/weather"
            return requests.get(url,params=params)
            break
    except Exception as e:
            print(e)

flag_lux=1
flag_weather=1
flag_movimento = 1
flag_sensore = 1
city = "Eboli"
orariochiusura = "07:30"
orarioapertura = "18:30"

#funzione per il controllo della luminosità e delle previsioni meteorologiche

def check_lux_weather():
    global high_tenda
    global flag_weather
    global operation
    global flag_lux
    global causa
    try:
        while True:
            if  high_tenda > 0 and flag_weather:
                response = check_weather()
                if response.status==200:
                    print("Richiesta http per le previsioni meteo andata a buon fine")
                    js = json.loads(response.content)
                    print("Weather:",js["weather"][0]["id"],js["main"]["temp"]-273,"degrees")
                    print("-------------")
                    if(js["weather"][0]["id"] >= 200  and js["weather"][0]["id"] < 800):
                        operation = -1
                        causa = "meteo"
                        print("Abbassamento tenda a causa delle previsioni meteorologiche") 
                        publish_to_self("It's raining, closing the roller blind",1)
            if high_tenda > 0 and flag_lux:
                sleep(2000)
                if digitalRead(D4) == 0:
                    operation = -1
                    causa = "luminosita"
                    print("Luce rilevata, abbassamento della tenda")
                    publish_to_self("Light detected",1)
                    sleep(30000)
            sleep (5000)
    except Exception as e:
        print("Problema durante il controllo delle previsioni meteo",e)



#type definisce il tipo di messaggio, se type vale 0 allora il messaggio deriva da Adafruit altrimenti sarà un messaggio di log.
#Questa funzione prende come parametri un obj e un integer, tramite l'integer riusciamo a capire da dove è arrivato il messaggio
#infatti con il codice 0 identifichiamo i messaggi ricevuti tramite mqtt (nel caso specifico da Adafruit), mentre con codice 1 identifichiamo i messaggi di log da inoltrare MQTT
#il funzionamento della funzione varia sulla base di questo parametro. Il primo caso può essere richiamato solo dalla funzione print_other che si attiva quando si ricevono messaggi mqtt.
#Di conseguenza i messaggi ricevuti con type 0 saranno quelli ricevuti da Adafruit e saranno sicuramente degli interi 1 o -1.
#Nel primo caso,quindi, si procederà con un cast esplicito della variabile e corrispetiva identificazione dell'operazione in modo da mandare informazioni su cosa eseguire tramite mqtt.
#Nel secondo caso invece, procediamo con l'invio diretto al mosquitto server poichè questi sono messaggi di log.

def publish_to_self(obj, type):
    global operation
    print("Sending ", str(obj), " to local")
    if type == 0:
        if obj != "aggiornamento impostazioni":
            code = int(obj)
            codemessage = "Command not recognized"
            if code == 1:
                codemessage = "Open the roller blind"
            if code == 0:
                codemessage = "Stop the roller blind"
            if code == -1:
                codemessage = "Close the roller blind"
            #changing the operation 
            operation = code
        #sending change to Local
        Localclient.publish("desktop/iTenda", codemessage)
    else:
        Localclient.publish("desktop/iTenda/info",str(obj))
        updateStatus()


#In questa parte procediamo prima con la connesisone al server mosquitto, in modo da poter inviare le informazioni di log, e in seguito con la connessione ad adafruit
#Possiamo notare che prima della connesisone abbiamo creato Adaclient come oggetto client di mqtt e in seguito abbiamo settato un ID e una password per l'accesso, questo perche
# per accedere ai feeds di Adafruit abbiamo la necessità di utilizzare appunto id e passwrod, per evitare accessi malevoli.

try:
    #Client for External Message
    Adaclient = mqtt.Client("zerynth-mqtt",True)
    #client for Local Message
    Localclient = mqtt.Client("zerynth-mqtt",True)
    for retry in range(10):
        try:
            #connection to mosquitto for local message
            Localclient.connect("test.mosquitto.org", 60)
            break
        except Exception as e:
            print("connecting to mosquitto...")
    print("connected to mosquitto.")
    Localclient.subscribe([["desktop/iTenda",0]])
    Localclient.loop(print_other)
    publish_to_self("Link Established",1)
    for retry in range(10):
        try:
            #Adding username and pw for the connection to adafruit
            Adaclient.set_username_pw(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
            Adaclient.connect("io.adafruit.com" , 0, 1883)
            break
        except Exception as e:
            print("connecting to adafruit...")
            publish_to_self("connecting to adafruit...",1)
    print("connected to adafruit.")
    publish_to_self("connected to adafruit.",1) 
    # subscribe to channels
    Adaclient.subscribe([["ferdisca/feeds/test",0]])
    Adaclient.loop(print_other)
except Exception as e:
    print(e)    

# qui creiamo un oggetto di tipo hcsr04 e come parametri passiamo i pin che utilizzeremo come trig e come echo. 

#D23 trig, D22 echo 
sens = hcsr04.hcsr04(D23, D22)

operation = 0
high_tenda = 1000
max_high_tenda = 30000 #ms


#la funzione action controlla ogni secondo lo stato della variabile "operation" che definisce appunto l'operazione da eseguire. All'interno di questa in base all'operazione andiamo a richiamare
#attraverso dei thread, la funzione per far suonare la melodia e la funzione per far ruotare lo stepper motor. Si è scelto di bloccare l'esecuzione di queste due thread attraverso una flag,
#instanziata nella classe e modificata quando necessario. Possiamo notare che prima di azionare i thread viene settata ad 1 e quando le operazioni si devono fermare viene settata a 0 
#Al termine di ogni operazione viene mandato un messaggio mqtt contenente il valore dell'altezza della tenda, opportunamente calcolato.
#L'operazione di apertura/chiusura tenda in totale impiega circa 30 secondi, modificabili dalla variabile max_high_tenda.
#Inoltre viene instanziato un timer per verificare quanto tempo è passato dall'inizio dell'operazione al suo termine, in questo modo possiamo ricavare l'altezza della tenda, basandoci 
#appunto, sul tempo passato.




def action():
    global operation
    global high_tenda
    global max_high_tenda
    thread(stepperMotor.movimento)
    thread(buzzerSong.suoneria)
    while True:
        sleep(1000)
        print("High of iTenda:" , round(high_tenda,0), "\n")
        #chiusura tenda
        if operation == -1:
            if high_tenda > 0:
                #start timer
                tm = Timers.timer()
                stepperMotor.flag_orario = 0
                stepperMotor.flag = 1
                buzzerSong.flag = 1
                buzzerSong.section = 1
                sleep(10)
                print("Closing the roller blind")
                tm.start()
                sendToDb()
                while operation == -1 and (high_tenda - tm.get()) > 0:
                    sleep(1000)
                high_tenda = high_tenda - tm.get() 
                stepperMotor.flag= 0
                buzzerSong.flag=0
                publish_to_self(str(high_tenda),1)
            operation = 0
        if operation == 0:
            print("waiting for op\n")
        #apertura tenda
        if operation == 1:
            if high_tenda < max_high_tenda:
                tm = Timers.timer()
                stepperMotor.flag_orario = 1
                stepperMotor.flag = 1
                buzzerSong.flag = 1
                buzzerSong.section = 2
                sleep(10)
                print("Open the roller blind")
                tm.start()
                sendToDb()
                while operation == 1 and (high_tenda + tm.get()) < max_high_tenda:
                    sleep(1000)
                high_tenda = high_tenda + tm.get()
                stepperMotor.flag = 0
                buzzerSong.flag = 0
                publish_to_self(str(high_tenda),1)
            operation = 0
        

#si procede con l'attivazione di una delle due funzioni sottostanti attraverso thread,
#per motivi di sperimentazione si è preferito utilizzare uno solo di questi per volta.

inizializzazioneTenda()
thread(action)
sleep(10)
thread(checkHours)
sleep(10)
thread(check_lux_weather)



def onButtonFall():
    inizializzazioneTenda()


pinMode(BTN0,INPUT)
onPinFall(BTN0, onButtonFall)


#funzione main, ogni 60 ms viene calcolata la distanza in CM rilevata dal sensore hcsr04, se la distanza risulta essere minore di 50cm significa che la mano è vicina al sensore
#si procederà quindi con il calcolo dell'operazione. In base alla posizione rilevata rispetto alla prima rilevazione che ha fatto scattare
#il while, si capirà l'operazione da eseguire. Inoltre è stata esclusa l'attivazione involontaria perchè, se si effettua un movimento di passaggio involontario, quindi senza allontanarsi
# o avvicinarsi al sensore, esso non farà scattare nessuna operazione.




while True:
    global operation
    if flag_sensore:
        cm = sens.getDistanceCM()
        print("\n",cm)
       # print("Distance: %.2f" % cm)
        while cm<=50:
            global operation
            prima = cm 
            sleep(200)
            cm = sens.getDistanceCM()
            if cm > 80:
                break
            if prima > cm + 15:
                #publish_to_self("approaching",1)
                operation = -1
                causa = "sensore"
                print("approaching to ultrasonic sensor", operation)
                sleep(940)
            elif prima< cm-15:
                print("moving away from ultrasonic sensor")
               # publish_to_self("moving away",1)
                operation = 1
                causa = "sensore"
                sleep(940)
    sleep(60)
   
