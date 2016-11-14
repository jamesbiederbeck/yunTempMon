#yunTempMon: A python3 script that does a few things, but mostly 
#serves my use case for the arduino yun. Monitor the temperature, and 
#upload it to a google drive 'sheet' via IFTTT for statistical analysis 
#later.
#By James Biederbeck {james@jamesbiederbeck.com}
import os
import requests
import math
import time
import argparse


#------------------------Handle arguments------------------------------- 
parser = argparse.ArgumentParser(description="Fetches temperature from an arduino yun REST API")
    
parser.add_argument(
    '--host',type=str,help ="Hostname/ip of the arduino", action='store')

parser.add_argument(
    '-v','--verbose',help="print other stuff",action='store_true')

parser.add_argument(
    '-m','--monitor',help="periodically check the value")

parser.add_argument(
    '-u','--upload', help="upload to IFTTT", action='store_true')

args= parser.parse_args()
print(args)

#----------------Helper Functions--------------------------------------

def readAnalog(host, pin):
    """Reads volatge of pin #pin at yun, and returns result as a float between 0 and 5,
    inclusive. """
    try:
        if args.verbose:
            print("Contacting arduino...")
        r = requests.get(host+"/arduino/analog/"+str(pin)).text
        if args.verbose:
            print(r)
        sensorvalue = float(r.split("analog ")[1].replace("\r",'').replace("\n",''))
    except requests.exceptions.MissingSchema:
        print("The request failed because you didn't include http(s)://")
    voltage=sensorvalue*5/1023 #the arduino has a resolution of 1024 bits on the ADC
    if args.verbose
        print("Arduino measured voltage", voltage, "on pin", pin)
    return voltage   

def calcResistance(voltage, r2,vin=5):
    """Calculates the r1 (positive end) value of a voltage divider"""
    r1 = r2*((vin/voltage)-1)
    return r1


def getTemperature(resistance, a = 9.6564e-4, b = 2.1069e-4, c = 8.5826e-8):
    """Calculate temperature given resistance using steinhart hart equation.
    A, B, and C are constants for a given component. Yours will be different."""
    #Sorry this next line is kind of long and ugly.
    temp=(1/(a+(b*math.log(resistance,math.e))+(c*(math.log(resistance,math.e)**3))))-273.15
    #Convert temp to fahrenheit, from celcius
    temp = temp*1.8+32 #comment out this line if you aren't a barbarian
    return temp

def getMeasurement(host, pin=0, seriesresistor=49100):
    v = readAnalog(host,pin)
    r = calcResistance(v, seriesresistor)
    t = getTemperature(r)
    if args.verbose:
        print("It is", t,"degrees Fahrenheit")
        print("Measured voltage:",v)
        print("calculated resistance:",r,"based on series resistor,",seriesresistor)
    return t
            
def post(eventname, ifttt_key, value1='', value2='', value3=''):
    url = "https://maker.ifttt.com/trigger/"
    url += eventname+'/'
    url += 'with/key/'+ifttt_key
    data = {"value1": value1, "value2":value2, "value3":value3}
    r =requests.post(url,data)
    
def getKey():
    #get key from user, one way or another
    if "ifttt_key.txt" in os.listdir():
        mode = 'r'
    else:
        mode = 'w'
        print("What is your ifttt key?")
        print("Get one at https://ifttt.com/maker")
        key = input("Paste your key here>")
        
    #We should now have access to a key, so let's make sure it's on disk
    with open("ifttt_key.txt", mode) as f:
        #read the key
        if mode = 'r':
            key = f.read()
        #user has provided a key, so let's save it
        elif mode = 'w':
            f.write(str(key))
        
def main(host="http://arduino.local"):
    if args.monitor:
        while True:
        try:
            temp = getMeasurement(host,pin,r2)
            for i in range(interval):
                time.sleep(1)
        except KeyboardInterrupt:
            break #exit loop
        except:
            print("An error was caught.")
            pass
    else:
        getMeasurement()
    
if __name__ == "__main__":
        main()
