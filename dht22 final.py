# import libraries
import RPi.GPIO as GPIO
import board
import adafruit_dht
from time import sleep
import json
import paho.mqtt.client as paho
from paho import mqtt

client = paho.Client( userdata=None, protocol=paho.MQTTv5)      #  creating an MQTT client
  

# enable TLS for secure connection
#client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password 
#client.username_pw_set("IOT_42", "password12A")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client.connect("broker.hivemq.com", 1883)

    



# declare pin
servoPin = 24
# create dht object
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

# set to use Broadcom GPIO numbers
GPIO.setmode(GPIO.BCM)
# disable warnings
GPIO.setwarnings(False)
# set servo pin as output
GPIO.setup(servoPin, GPIO.OUT)
# initialize PWM on pin at 50Hz
pwm = GPIO.PWM(servoPin, 50)
# start pwm with 0 duty cycle so it doesn't set any angles on start
pwm.start(0)

# create function so we can call this later
def Set_Angle(angle):
    # calculate duty cycle from angle
    duty = angle / 18 + 2
    # turn on servo pin
    GPIO.output(servoPin, True)
    # set duty cycle to pin
    pwm.ChangeDutyCycle(duty)
    # wait 1s for servo to move into position
    sleep(1)
    # turn off servo pin
    GPIO.output(servoPin, False)
    # set duty cycle to 0 to stop signal
    pwm.ChangeDutyCycle(0)

# main loop
while True:
    try:
        # Print the values to the serial port
        
        temperature_c = dhtDevice.temperature
        T = temperature_c * 9/5 + 32
        RH = dhtDevice.humidity
        HI = -42.379 + 2.04901523*T + 10.14333127*RH - .22475541*T*RH - .00683783*T*T - .05481717*RH*RH + .00122874*T*T*RH + .00085282*T*RH*RH - .00000199*T*T*RH*RH
        print("Temp: {:.1f} F / {:.1f} C    Humidity: {}%   Heat Index: {:.2f} F ".format(T, temperature_c, RH, HI))
        payload={
                    "HI":HI,
                    "Humidity":RH
                }
        json_payload=json.dumps(payload)       
        # publish
        client.publish("iot", json_payload)
        
        #print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity))
        
        if temperature_c <= 29:
            Set_Angle(165)
        elif temperature_c <= 30:
            Set_Angle(135)
        elif temperature_c <= 31:
            Set_Angle(105)
        elif temperature_c <= 32:
            Set_Angle(75)
        elif temperature_c <= 33:
            Set_Angle(45)
        elif temperature_c <= 34:
            Set_Angle(15)
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error
    
    sleep(1)
    
# stop pwm on exit
pwm.stop()
# release GPIOs on exit
GPIO.cleanup()
client.disconnect()
