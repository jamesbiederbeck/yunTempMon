#yunTempMon: A python3 script that does a few things, but mostly 
#serves my use case for the arduino yun. Monitor the temperature, and 
#upload it to a google drive 'sheet' via IFTTT for statistical analysis 
#later.
#By James Biederbeck {james@jamesbiederbeck.com}
import os
import requests
import time
import argparse

from math import log as ln #To make things less confusing


#------------------------Handle arguments------------------------------- 
parser = argparse.ArgumentParser(description="Fetches temperature from an arduino yun REST API")
    
parser.add_argument(
        '--host',type=str,
        help ="Hostname/ip of the arduino. Default is arduino.local", 
        action='store'
        )

parser.add_argument(
        '-v','--verbose',help="print other stuff",action='store_true')

parser.add_argument(
        '-m','--monitor',help="periodically check the value",
        action='store_true'
        )

parser.add_argument(
        '-u','--upload', help="upload to IFTTT", action='store_true'
        )

parser.add_argument(
        '-f','--fahrenheit', help="Output Fahrenheit", 
        action='store_true'
        )

parser.add_argument(
        '-i','--interval', type=int, help="How often to check the sensor",
        action='store'
        )
#actually get the arguments
args= parser.parse_args()

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
    if args.verbose:
        print("Arduino measured voltage", voltage, "on pin", pin)
    return voltage   

def calcResistance(voltage, r2,vin=5):
    """Calculates the r1 (positive end) value of a voltage divider"""
    r1 = r2*((vin/voltage)-1)
    return r1

def calcTemperature(resistance, a = 9.6564e-4, b = 2.1069e-4, c = 8.5826e-8):
    """Calculate temperature given resistance using steinhart hart equation.
    A, B, and C are constants for a given component. Yours will be different."""
    temp = a + b * ln(resistance) + (c*(ln(resistance)**3))
    temp = 1/temp
    temp -= 273.15 #convert from kelvin to celcius
    if args.fahrenheit: #convert to Fahrenheit
        temp = temp*1.8+32
    return temp


def getMeasurement(host, pin=0, seriesresistor=49100):
    """The bulk of the logic is actually in this function,
    at least, as far as the interesting bits for how it works"""
    if args.fahrenheit:
        unit = "Fahrenheit"
    else:
        unit = "Celsius"
    v = readAnalog(host,pin)
    r = calcResistance(v, seriesresistor)
    t = calcTemperature(r)
    if args.verbose:
        print("It is", t,"degrees", unit)
        print("Measured voltage:",v)
        print("calculated resistance:",r,"based on series resistor,",seriesresistor)
    return t
            
def upload(eventname, ifttt_key, value1='', value2='', value3=''):
    url = "https://maker.ifttt.com/trigger/"
    url += eventname+'/'
    url += 'with/key/'+ifttt_key
    data = {"value1": value1, "value2":value2, "value3":value3}
    r =requests.post(url,data)
    return r
    
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
        if mode == 'r':
            key = f.read()
        #user has provided a key, so let's save it
        elif mode == 'w':
            f.write(str(key))
    return key
            
def monitor(host, interval,key):
    iterations = 0
    successful_iterations = 0
    while True:
        iterations+=1
        try:
            temp = getMeasurement(host)
            upload("yuntemp",key, "Temperature",str(temp)+"°F")
            successful_iterations +=1
                
            #now wait until next time
            for i in range(interval):
                time.sleep(1)
                   
        except KeyboardInterrupt:
            break #exit loop
                   
        except error as e:
            if args.strict:
                raise
            print("Unexpected error:", sys.exc_info()[0])
            print("Turn on strict mode to see more errors.")
    if args.verbose:
        print("Monitor mode exiting.")
        print("Ran",iterations)
        print(successful_iterations,"were successful")
            
            
        
def main(host="http://arduino.local"):
    key=getKey()
    if args.monitor:
        if args.interval ==None:
            interval = 300
        else:
            interval = args.interval
        monitor(host, interval,key)
    else: 
        print(str(getMeasurement(host))+"°F")
    
if __name__ == "__main__":
        main()
