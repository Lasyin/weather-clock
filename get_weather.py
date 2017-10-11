#Used by weather_clock.py to return weather stats from open weather map, sign up for an API key !
import urllib
import json

MAX_TEMP = 31 #Set to the maximum amount of degrees your clock can handle
CITY = "INSERT CITY HERE"
COUNTRY_CODE = "INSERT COUNTRY CODE HERE"
API_KEY = "INSERT API KEY HERE"

def get_weather():
	url ='http://api.openweathermap.org/data/2.5/weather?q={' + CITY + '},{' + COUNTRY_CODE + '}&appid=' + API_KEY
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	dict = {'temp': 0, 'rain': False, 'cloud': False, 'snow': False, 'wind': False, 'negative': False}

	#CONVERT FROM KELVIN TO CELSIUS (default)
	temp = (float(data['main']['temp'])) - (273.15)

	#CONVERT FROM KELVIN TO FAHRENHEIT (uncomment line below (and comment line above) to convert to F instead of C)
	#temp = ((float(data['main']['temp'])) * (9/5)) - (459.67)

	#If temperature is below 0, change the negative variable in dictionary to True and multiply by -1
	#This is so the clock displays the 'positive' temperature, but lights up the negative display LED
	if(int(temp) < 0):
		dict['negative'] = True
		temp = temp * -1
	if(int(temp) > MAX_TEMP):
		temp = MAX_TEMP
	dict['temp'] = int(temp)

	#Check JSON output for rain, if the 'main' weather says "Rain" that means it is raining
	rain = data['weather'][0]['main']
	if(rain == "Rain"):
		dict['rain'] = True
	else:
		print("Not raining: " + str(rain))

	#Check JSON output for cloud coverage, if it is over 25 it is considered 'cloudy'
	cloud = data['clouds']['all']
	print("cloud coverage: " + str(cloud))
	if(int(cloud) > 25):
		dict['cloud'] = True
	else:
		print(str(cloud) + " is not very cloudy")

	#Check JSON output for snowfall, if the 'main' weather says "Snow" that means it is snowing
	snow = data['weather'][0]['main']
	if(snow == "Snow"):
		dict['snow'] = True
	else:
		print("Not snowing: " + str(snow))

	#Check JSON output for wind speeds, if it is over 20 it is considered "windy"
	wind = data['wind']['speed']
	if(float(wind) > 20):
		dict['wind'] = True
	else:
		print(str(wind) + " not very windy")

	return(dict)


#print(get_weather()) #To test output of function
