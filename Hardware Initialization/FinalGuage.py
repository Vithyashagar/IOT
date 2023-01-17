import RPi.GPIO as GPIO
import time
import board
import adafruit_dht
import psutil
import signal
#import sys
from numpy import transpose

GPIO.setmode(GPIO.BCM)
#Pins for stepper
ControlPin = [17,18,27,22]

#Variable Initialization
position = 0 #1=cool, 2=warm, 3=hot
go_to_position = 0
temp = 0

for pin in ControlPin:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,0)
    
#forward stepping    
seq = [[1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1],
       [1,0,0,1]]

#reverse stepping
seq_rev = [[0,0,0,1],
       [0,0,1,1],
       [0,0,1,0],
       [0,1,1,0],
       [0,1,0,0],
       [1,1,0,0],
       [1,0,0,0],
       [1,0,0,1]]

def direction_finder(direct):
    """This method will return the direction
        input : 1, output : seq(fw)
        input : 2, output : seq_rev(rev)"""
    if direct == 1:
        direction = seq # FW
    elif direct == 2:
        direction = seq_rev # REV  
    return direction


def rotate(angle_step, direct):
    """This method will rotate the motor when the direction and the angle is given"""
    direction = direction_finder(direct) 
    for i in range(angle_step):
        for halfstep in range(8): #Half stepping
            for pin in range(4):
                GPIO.output(ControlPin[pin], direction[halfstep][pin])
                time.sleep(0.0008)

def init_motor_position():
    """This method will rotate the motor in 180 deg back and forth and
        set the initial motor position at 30 deg"""
    #>>
    rotate(256, 1)
    #<<
    rotate(256, 2)
    #init position
    rotate(43, 1)
    return 1

def position_finder(temp):
    """This method will return the position to rotate
        input : temp < 20, position : 1(COOL)
        input : 20 < temp <=30, position : 2(WARM)
        input : temp > 30, position : 3(HOT)"""
    if int(temp) < 20:
        print("COOL")
        position = 1
    elif int(temp) >= 20 and int(temp)<= 30:
        print("WARM")
        position = 2
    elif int(temp) > 30:
        print("HOT")
        position = 3
    return position

def motor_angle(position, temp):
    """Ths method will rotate the guage according to the temperature in fw and rev
        input : position - current position of Guage
                temp - temperature of the room
        output : position to move"""
    go_to_position = position_finder(temp)
    angle_move = int(go_to_position) - int(position)
    #print("go_to_position : "+ str(go_to_position)+ "; "+"position :"+str(position)+"; "+"angle_move :"+ str(angle_move))
    #one position to anotherposition is 60 deg
    angle_step = angle_move * 86
    
    if (angle_step > 0):
        print("Temperature: {}*C".format(temp))
        rotate(angle_step,1)
    
    elif(angle_step < 0):
        print("Temperature: {}*C".format(temp))
        angle_step = int(angle_step)*-1
        rotate(angle_step,2)
    
    elif(angle_step == 0):
        print("Temperature: {}*C".format(temp))
        
    return go_to_position

def position_zero(position):
    """This method will reset the dials position after program ends"""
    print("Going offline. Position Zero")
    if(position == 1):
        rotate(43,2)
    elif(position == 2):
        rotate(128,2)
    elif(position == 3):
        rotate(214,2)
    #return position

#Method to capture the keyboard interrupt and close the program and cleaning
def sigint_handler(signal, frame):
    print("Keyboard interrupt detected.")
    position_zero(position)
    GPIO.cleanup()

#Calling the method to isten to keyboard interrupt
signal.signal(signal.SIGINT, sigint_handler)

#Initial rotation
position = init_motor_position()

#Temperature capture
# We first check if a libgpiod process is running. If yes, we kill it!
for proc in psutil.process_iter():
    if proc.name() == 'libgpiod_pulsein' or proc.name() == 'libgpiod_pulsei':
        proc.kill()
sensor = adafruit_dht.DHT11(board.D23)
while True:
    try:
        temp = sensor.temperature
        position = motor_angle(position,temp)
    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
        continue        
    time.sleep(2.0)
