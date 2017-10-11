#Main file, run this!
import RPi.GPIO as GPIO
import time
import sys
import get_weather # Import our get_weather.py script !

GPIO.setmode(GPIO.BCM)

#Our output pins for the stepper motor
pins = [4,17,27,22]

#Our output pins for the LEDs
leds = [18,23,24,25]

FILE_LOCATION = "/home/pi/weather_clock_temp.txt" #Change this to the location of your text file !! (also, create an empty text file before this)

SLEEP_TIME = 0.001 #Controls the speed of the motor, changing this could result in the motor not moving
DEG_TO_STEP = 16   #How many steps per degree? There are 512 steps in MY motor, 16 steps in a degree allows me to displays 32 degrees
						#Can increase it to 8 to display 64 degrees, or 4 to display 128.. and so on..
							#Keep in mind that the lower the DEG_TO_STEP the less accurate the clock will be
								#So use as low as a DEG_TO_STEP as possible, this is easier with celsius (and a negative LED indicator) than fahrenheit
LOW_TEMP = 0		#Whats the lowest temperature you can display? Mine is 0 (anything below that will flip on the negative LED !)
HIGH_TEMP = 31		#Whats the highest temperature you can display? ((512/DEG_TO_STEP)-1)

#A 2d list storing the motors sequence, step through this sequence to move the motor forwards
	#Numbers represent turning the 4 inputs on the driver motor board on and off
sequence = [ 	[1,0,0,0],
		[1,1,0,0],
		[0,1,0,0],
		[0,1,1,0],
		[0,0,1,0],
		[0,0,1,1],
		[0,0,0,1],
		[1,0,0,1]	]

#setup both the motor and leds
def setup():
	setup_motor()
	setup_leds()

#setup the motor
def setup_motor():
	#Set GPIO pins to BCM (as opposed to BOARD)
	GPIO.setmode(GPIO.BCM)
	#for each pin, set it to out and its output as 0 (off)
	for pin in pins:
        	GPIO.setup(pin,GPIO.OUT)
        	GPIO.output(pin,0)

#setup leds
def setup_leds():
	#Set GPIO pins to BCM (as opposed to BOARD)
	GPIO.setmode(GPIO.BCM)
	#for each pin, set it to out and its output as False (off)
	for pin in leds:
		GPIO.setup(pin,GPIO.OUT)
		GPIO.output(pin,False)

#turn on a specific led, num represents its position in the leds list
def turn_on(num):
	GPIO.output(leds[num], True)

#turn off a specific led, num represents its position in the leds list
def turn_off(num):
	GPIO.output(leds[num], False)

#update all LEDs
def update_leds(status):
	#if wind is true, turn on wind led
	if(status['wind']):
		turn_on(0)
	else:
		turn_off(0)
	#if negative is true, turn on negative led
	if(status['negative']):
		turn_on(1)
	else:
		turn_off(1)
	#if rain is true, turn on rain led
	if(status['rain']):
		turn_on(2)
	else:
		turn_off(2)
	#if snow is true, turn on snow led
	if(status['snow']):
		turn_on(3)
	else:
		turn_off(3)

#Move FROM start (steps) TO end (steps)
def move_to(start, end):
	#If start is greater than end steps, move backwards
	if(start > end):
		#destination is the amount of steps START to END
		dest = start - end
		print("Move: " + str(dest) + " steps")
		#For every step...
		for i in range(dest):
			#For every halfstep...
			for halfstep in range(8):
				#For every output pin...
				for pin in range(4):
					#change the pin to the appropriate value in the sequence, we're doing 7-halfstep to make the motor go backwards!
					GPIO.output(pins[pin], sequence[7-halfstep][pin])
				#sleeeepppp, motor can't go too fast
				time.sleep(SLEEP_TIME)
	#If end is greater than start steps, move forwards
	elif(start < end):
		#destination is the amount of steps START to END
		dest = end - start
		print("Move: " + str(dest) + " steps")
		#For every step...
		for i in range(dest):
			#For every halfstep...
			for halfstep in range(8):
				#For every output pin...
				for pin in range(4):
					#Set the pins output value to the correct sequence value
					GPIO.output(pins[pin], sequence[halfstep][pin])
				#sleeeepppp, motor can't go too fast
				time.sleep(SLEEP_TIME)

def main_func():
	#Setup the motors GPIO pins
	setup_motor()
	#Return a dictionary of weather values
	weather = get_weather.get_weather()

	#The temperature, in celsius (by default) or fahrenheit (if you've uncommented the line)
	temp = int(weather['temp'])

	#The last recorded temperature from the text file, the stepper motor needs to know the distance between the
		#current position it is in to the position it needs to move to!
	last_temp = get_temp_from_file()

	#If the temperature doesnt exist (no last recorded temperature), set it to 0
	if(len(last_temp) < 1):
		last_temp = 0

	#Move the motor FROM the last recorded temperature, TO the new temperature
	move_to(DEG_TO_STEP*(int(last_temp)), DEG_TO_STEP*(int(temp)))
	#Store the new temperature on a text file so we know for the future
	store_temp_on_file(int(temp))

	#Reset the motor pins, if you keep the pins on the motor gets very hot!!!
	GPIO.cleanup()

	#Setup the LED pins
	setup_leds()
	#Update the LEDs to show current weather status (rain,snow,wind...)
	update_leds(weather)

def get_temp_from_file():
	#open our text file in read mode
	f = open(FILE_LOCATION, 'r')
	#read the line (theres only 1)
	line = f.readline()
	f.close()
	#return the line
	return(line)

def store_temp_on_file(temp):
	#open our text file in write mode, NOT APPEND, we only want to store the single last temperature we had !
	f = open(FILE_LOCATION, 'w')
	#write our temperature
	f.write(str(temp))
	f.close()
	return

if __name__ == "__main__":
	setup()
	if(len(sys.argv) == 2):
		#Move the stepper motor a certain number of steps,
		#this can be useful for repositioning the motor if accuracy is lost
		print("move : " + sys.argv[1] + " steps")
		move_to(0, int(sys.argv[1]))
		GPIO.cleanup()
	elif(len(sys.argv) == 3):
		#Move the stepper motor FROM a certain temperature, TO a certain temperature,
		#this can be useful for repositioning the motor AND storing the new temperature in the text file
		print("move from temp " + sys.argv[1] + " to " + sys.argv[2])
		move_to((int(sys.argv[1])*DEG_TO_STEP), (int(sys.argv[2])*DEG_TO_STEP))
		store_temp_on_file(int(sys.argv[2]))
		GPIO.cleanup()
	else:
		#Start
		main_func()
		print("done")
