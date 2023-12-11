import streams

import pwm


#flag che determinerà l'avvio o meno del motore.
flag = 0
flag_orario = 0 
# pin ai quali è collegato il motore
pinMode(D5, OUTPUT)
pinMode(D18, OUTPUT)
pinMode(D19, OUTPUT)
pinMode(D21, OUTPUT)

 


pins = [
    D5, D18, D19, D21,
]

 
# sequenza di pin da attivare per sollevamento e abbassamento
steps = [
    [D5],
    [D5, D18],
    [D18],
    [D18, D19],
    [D19],
    [D19, D21],
    [D21],
    [D21, D5],
]
steps2 = [
    [D21, D5],
    [D21],
    [D19, D21],
    [D19],
    [D18, D19],
    [D18],
    [D5, D18],
    [D5],
]
current_step = 0

 

#funzioni per asserire o disattivare i pin.
def set_pins_low(pins):
    [digitalWrite(pin, LOW) for pin in pins]



def set_pins_high(pins):
    [digitalWrite(pin, HIGH) for pin in pins]
    
    
    
#funzioni per la rotazione oraria e antioraria.    
def movimento():
    global flag_orario
    global flag
    while True:
        sleep(1000)
        while flag:
            if flag_orario == 1:
                high_pins = steps[current_step]
                set_pins_low(pins)
                set_pins_high(high_pins)
                current_step += 1
                if current_step == len(steps):
                    current_step = 0
                sleep(2)
            else:
                high_pins = steps2[current_step]
                set_pins_low(pins)
                set_pins_high(high_pins)
                current_step += 1
                if current_step == len(steps):
                    current_step = 0
                sleep(2)
             