import time
from rpi_ws281x import *
import random
import math
import RPi.GPIO as GPIO
import json
import os
import psutil
import requests

#thingspeak code
writeAPIkey = "1W359A5ROOO11MJ7" # Replace YOUR-CHANNEL-WRITEAPIKEY with your channel write API key
channelID = "1342579" # Replace YOUR-CHANNELID with your channel ID
#url = "https://api.thingspeak.com/channels/"+channelID+"/bulk_update.json" # ThingSpeak server settings

#functie om thingspeak te updaten
def updateThingspeak():
    url= "https://api.thingspeak.com/update"
    messageBuffer = []
    queries = {"api_key": "1W359A5ROOO11MJ7",
                "field1": GPIO.input(4),
                "field2": 0}

    r = requests.get(url, params=queries)
    if r.status_code == requests.codes.ok:
        print("Data Received!")
    else:
        print("Error Code: " + str(r.status_code))
 
#gpio pins voor de licht sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.IN)

 
# LED strip configuration:
LED_COUNT      = 120      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
strip.begin()


#alle onderstaande functies zijn geprogrameerde effecten voor mijn ledstrip
gravity = int()
height = []
Position = []
ImpactVelocityStart = int()
ImpactVelocity = []
dampening = []
ClockTimeSinceLastBounce = []
TimeSinceLastBounce = []
def setupBouncingBall(aantalBallen):
    global gravity, height, Position, ImpactVelocityStart, ImpactVelocity, dampening, ClockTimeSinceLastBounce, TimeSinceLastBounce
    for x in range(aantalBallen):
        gravity = -9.81 / 2
        height.append(1)
        Position.append(0)
        ImpactVelocityStart = math.sqrt(-2 * gravity * 4) # * 1 staat voor 1 meter hoog.
        ImpactVelocity.append(ImpactVelocityStart)
        dampening.append(0.90 - (x * 0.01)) # Hoeveel de snelheid van de bal afneemt per bounce.  - float(x)/pow(aantalBallen,2)
        ClockTimeSinceLastBounce.append(time.time())
        TimeSinceLastBounce.append(0)

def bouncingBall(aantalBallen):
    for x in range(aantalBallen):
        global gravity, height, Position, ImpactVelocityStart, ImpactVelocity, dampening, ClockTimeSinceLastBounce, TimeSinceLastBounce
        TimeSinceLastBounce[x] = time.time() - ClockTimeSinceLastBounce[x]
        height[x] = 0.5 * gravity * pow(TimeSinceLastBounce[x], 2) + ImpactVelocity[x] * TimeSinceLastBounce[x]

        if height[x] < 0:
            height[x] = 0
            ImpactVelocity[x] = dampening[x] * ImpactVelocity[x]
            ClockTimeSinceLastBounce[x] = time.time()

        if ImpactVelocity[x] < 0.01:
            ImpactVelocity[x] = ImpactVelocityStart

        Position[x] = round(height[x] * (29 - 1)) # aantal leds - 1
        strip.setPixelColor(Position[x], Color(150, 0, 0))
        strip.setPixelColor(Position[1], Color(0, 150, 0))
        strip.setPixelColor(Position[2], Color(0, 0, 150))
        strip.setPixelColor(Position[x] - 1, Color(0,0,0))
        strip.setPixelColor(Position[x] - 2, Color(0,0,0))
        strip.setPixelColor(Position[x] - 3, Color(0,0,0))
        strip.setPixelColor(Position[x] + 1, Color(0,0,0))
        strip.setPixelColor(Position[x] + 2, Color(0,0,0))
        strip.setPixelColor(Position[x] + 3, Color(0,0,0))
        strip.show()
        
def instantWipe():
    for x in range(0, LED_COUNT):
        strip.setPixelColor(x, Color(0,0,0))
    strip.show()

beginTijdStrook = time.time()
def strook(wachttijd):
    global beginTijdStrook
    reken = 1 / wachttijd
    nieuweTijd = (time.time() - beginTijdStrook) * reken
    strip.setPixelColor(int(nieuweTijd), Color(150, 0, 0))
    strip.show()
    if nieuweTijd > LED_COUNT:
        beginTijdStrook = time.time()
        instantWipe()
        
beginTijdSpear = time.time()
def spear(wachttijd, max_felheid = 200, stap = 20):
    global beginTijdSpear
    reken = 1 / wachttijd
    nieuweTijd = (time.time() - beginTijdSpear) * reken
    felheid = max_felheid
    for y in range(0, 9):
        strip.setPixelColor(round(nieuweTijd) - y, Color(0, 0, felheid))
        felheid = felheid - stap
    strip.show()
    if nieuweTijd > LED_COUNT + 9:
        beginTijdSpear = time.time()
        

beginTijdAanvullen = time.time()
VerminderingAanvullen = LED_COUNT
def aanvullen(wachttijd):
    global beginTijdAanvullen, VerminderingAanvullen
    reken = 1 / wachttijd
    nieuweTijd = (time.time() - beginTijdAanvullen) * reken
    strip.setPixelColor(round(nieuweTijd), Color(0, 0, 150))
    strip.setPixelColor(round(nieuweTijd - 1), Color(0, 0, 0))
    strip.show()
    if nieuweTijd >= VerminderingAanvullen:
        VerminderingAanvullen = VerminderingAanvullen - 1
        beginTijdAanvullen = time.time()
        if VerminderingAanvullen <= 0:
            VerminderingAanvullen = LED_COUNT
            
beginTijdMeteor = time.time()
def meteor(wachttijd, fadeValue, DecayKans):
    global beginTijdMeteor
    reken = 1 / wachttijd
    nieuweTijd = (time.time() - beginTijdMeteor) * reken
    strip.setPixelColor(round(nieuweTijd), Color(70, 70, 70))
    strip.show()
    for x in range(LED_COUNT):
        i = strip.getPixelColor(x)
        B = i % 256
        G = ((i-B)/256) % 256
        R = ((i-B)/256**2) - G/256
        
        if random.randint(1, 10) < DecayKans:
            if B <= 10:
                B = 0
            else:
                B = B-(B*fadeValue/256)
            if G <= 10:
                G = 0
            else:
                G = G-(G*fadeValue/256)
            if R <= 10:
                R = 0
            else:
                R = R-(R*fadeValue/256)
                
        strip.setPixelColor(x, Color(int(R), int(G), int(B)))
    strip.show()
    if nieuweTijd > LED_COUNT + 30:
        beginTijdMeteor = time.time()

setupBouncingBall(3)
klok = time.time()
#main functie van het programma
try:
    while True:
        tijdnu = time.time() - klok
        #als de lichtsensor meet dat het donker is en dus een output van 1 geeft dan gaat de ledstrip aan
        if GPIO.input(4) == 1:
            if tijdnu < 10:
                spear(0.03, 200, 20)
            if tijdnu >= 10 and tijdnu < 20:
                meteor(0.03, 80, 2)
            if tijdnu >= 20 and tijdnu < 30:
                aanvullen(0.02)
            if tijdnu >= 30 and tijdnu < 40:
                bouncingBall(3)
            if tijdnu >= 40 and tijdnu < 50:
                strook(0.05)
            if tijdnu >= 50:
                updateThingspeak()
                klok = time.time()
        else:
            instantWipe()
        if tijdnu >= 50:
            updateThingspeak()
            klok = time.time()
except KeyboardInterrupt:
    instantWipe()