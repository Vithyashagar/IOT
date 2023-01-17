import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

ControlPin = [17,18,27,22]

for pin in ControlPin:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,0)
    
seq = [[0,0,0,1],
       [0,0,1,1],
       [0,0,1,0],
       [0,1,1,0],
       [0,1,0,0],
       [1,1,0,0],
       [1,0,0,0],
       [1,0,0,1]]

#512 for 360 deg
#since the gauge have 3 levels 180 deg is enough
for i in range(256):
    for halfstep in range(8):
        for pin in range(4):
            GPIO.output(ControlPin[pin], seq[halfstep][pin])
            time.sleep(0.0008)
            
GPIO.cleanup()


    except Exception as error:
        sensor.exit()
        position = position_zero(position)
        GPIO.cleanup()
        raise error
