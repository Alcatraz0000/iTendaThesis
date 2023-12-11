import pwm

#definizione di note che devono essere suonate dal buzzer.
c = 261
d = 294
e = 329
f = 349
g = 391
gS = 415
a = 440
aS = 455
b = 466
cH = 523
cSH = 554
dH = 587
dSH = 622
eH = 659
fH = 698
fSH = 740
gH = 784
gSH = 830
aH = 880

#flag che determinerà l'avvio o meno della suoneria.
flag = 0 
section = 0

#definizione del pin al quale è collegato il buzzer.
buzzerpin = D27.PWM 
pinMode(buzzerpin,OUTPUT)

def play(hz,duration):
    global flag
    if flag:
        if hz != 0:
            freq = 1000000//hz
            duty=freq//2
            pwm.write(buzzerpin,freq,duty,MICROS)
        sleep(duration)
    else:
        pwm.write(buzzerpin,0,0,MICROS)
        break
   
   
#funzioni che definiscono la canzone, in termini di sequenza di note.     


firstsection = [
    [a , 500],
    [a , 500],
    [a, 500],
    [f, 350],
    [cH , 150],
    [a , 500],
    [f , 350], 
    [cH ,150],
    [a,650],
    [0, 500],
    [eH , 500],
    [eH, 500],
    [eH, 500],
    [fH , 350],
    [cH,150],
    [gS , 500],
    [f , 350],
    [cH , 150],
    [a , 650],
    [0 , 500]
]
secondsection=[
    [aH,500],
    [a,300],
    [a,150],
    [aH,500],
    [gSH,325],
    [gH,175],
    [fSH,125],
    [fH,125],
    [fSH,250],
    [0,0],
    [aS,250],
    [dSH,500],
    [dH,325],
    [cSH,175],
    [cH,125],
    [b,125],
    [cH,250],
    [0,0]
]


def suoneria():
    
    global flag
    global section
    global firstsection
    while True:
        steps = 0
        while flag:
            if section == 1:
                
                if firstsection[steps][0] != 0:
                    play( firstsection[steps][0], firstsection[steps][1])
                else:
                    pwm.write(buzzerpin,0,0,MICROS)
                    sleep(500)
                steps+=1
            if section == 2:
                
                if secondsection[steps][0] != 0:
                    play( secondsection[steps][0], secondsection[steps][1])
                else:
                    pwm.write(buzzerpin,0,0,MICROS)
                    sleep(500)
                steps+=1
            if steps == len(firstsection) or steps == len(secondsection):
               break
        pwm.write(buzzerpin,0,0,MICROS)
        
