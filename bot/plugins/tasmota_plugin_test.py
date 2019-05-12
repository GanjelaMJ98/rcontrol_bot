import tasmota_plugin
import time as t
plugins = list()

def get_plugins_test():
	plugins.extend(tasmota_plugin.get_plugins())
	print("_____GET PLUGINS_____")
	for plugin in plugins:
		print(plugin.name)

def sensor_test():
	print("________SENSOR_______")
	sonoff = tasmota_plugin.Tasmota("th16")
	#sensor = sonoff.sensor()
	#print(sensor["Time"])
	#print(sensor["TempUnit"])
	#print(sensor["Sensor"]["Temperature"])
	#print(sensor["Sensor"]["Humidity"])
	print(sonoff.sensor_info())

def power_test():
	print("________POWER________")
	for plugin in plugins:
		print(plugin.name)
		print(plugin.power_on())
		t.sleep(1)
		print(plugin.power_off())
		t.sleep(1)
		print(plugin.power_on())





def main():
	get_plugins_test()
	sensor_test()
	power_test()

if __name__ == '__main__':
	main()