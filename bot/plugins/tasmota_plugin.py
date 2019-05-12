from .Plugin import Property, Plugin
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import time as t
import os
import json

filename = '/etc/Bot/config.json'
file = open(filename,"r+")
pars_string = json.load(file)
file.close()

HOSTNAME = pars_string['host_name']
HOSTPORT = pars_string['host_port']


class Tasmota(Plugin):
	def __init__(self,name):
		self.name = name
		self.properties = []
		self.information = dict()
		self.sensor_information = dict()
		self.add_property("power_on", self.power_on)
		self.add_property("power_off", self.power_off)
		self.add_property("info", self.get_information)
		if(name == "th16"):
			self.add_property("sensor_info",self.sensor_info)

	def __str__(self):
		return("Tasmota - " + self.name)

	def power_on(self):
		publish.single("cmnd/{0}/POWER".format(self.name) , "ON", hostname = HOSTNAME)
		return("Power ON")

	def power_off(self):
		publish.single("cmnd/{0}/POWER".format(self.name) , "OFF", hostname = HOSTNAME)
		return("Power OFF")

	def device_status(self,msg):
		if msg.topic == "stat/{0}/STATUS".format(self.name):
			message = eval(msg.payload.decode("utf-8"))
			for key,value in message['Status'].items():
				self.information.update({str(key):str(value)})

	def	wifi_status(self,msg):
		if msg.topic == "stat/{0}/STATUS3".format(self.name):
			message = eval(msg.payload.decode("utf-8"))
			for key,value in message['StatusLOG'].items():
				self.information.update({str(key):str(value)})

	def network_status(self,msg):
		if msg.topic == "stat/{0}/STATUS5".format(self.name):
			message = eval(msg.payload.decode("utf-8"))
			for key,value in message['StatusNET'].items():
				self.information.update({str(key):str(value)})

	def mqtt_status(self,msg):
		if msg.topic == "stat/{0}/STATUS6".format(self.name):
			message = eval(msg.payload.decode("utf-8"))
			for key,value in message['StatusMQT'].items():
				self.information.update({str(key):str(value)})

	def sensor_status(self,msg):
		if msg.topic == "stat/{0}/STATUS8".format(self.name):
			message = eval(msg.payload.decode("utf-8"))
			for key,value in message['StatusSNS'].items():
				self.information.update({str(key):str(value)})
				if(str(key)!="Time")and(str(key)!="TempUnit"):
					self.sensor_information.update({"Name":str(key)})
					self.sensor_information.update({"Sensor":dict(value)})
				else:
					self.sensor_information.update({str(key):str(value)})


				

	
	def on_message_information(self,mqttc, obj, msg):
		self.sensor_status(msg)
		self.device_status(msg)
		self.wifi_status(msg)
		self.network_status(msg)
		self.mqtt_status(msg)

	def get_information(self):
		publish.single("cmnd/{0}/STATUS".format(self.name),"0", hostname=HOSTNAME)
		mqttc = mqtt.Client()
		mqttc.on_message = self.on_message_information
		mqttc.connect(HOSTNAME,HOSTPORT, 60)
		mqttc.subscribe("#", 0)
		mqttc.loop_start()
		t.sleep(1)
		mqttc.loop_stop()
		return(self.information)

	def sensor(self):
		publish.single("cmnd/{0}/STATUS".format(self.name),"8", hostname=HOSTNAME)
		mqttc = mqtt.Client()
		mqttc.on_message = self.on_message_information
		mqttc.connect(HOSTNAME,HOSTPORT, 60)
		mqttc.subscribe("#", 0)
		mqttc.loop_start()
		t.sleep(1)
		mqttc.loop_stop()
		return(self.sensor_information)
	def sensor_info(self):
		self.sensor()
		answer = """Time: {0}\nSensor: {1}\nTemperature: {2} {3}\nHumidity: {4} %\n""".format(self.sensor_information["Time"],
																						self.sensor_information["Name"],
																						self.sensor_information["Sensor"]["Temperature"],
																						self.sensor_information["TempUnit"],
																						self.sensor_information["Sensor"]["Humidity"])
		return answer




modules = []

def get_active_modules(mqttc, obj, msg):
		if msg.topic.endswith("STATUS"):
			message = eval(msg.payload.decode("utf-8"))
			global modules
			modules.append(message["Status"]["Topic"])



def get_plugins():
	publish.single("cmnd/sonoffs/STATUS","", hostname=HOSTNAME)
	
	global modules
	mqttc = mqtt.Client()
	mqttc.on_message = get_active_modules
	mqttc.connect(HOSTNAME, HOSTPORT, 60)
	mqttc.subscribe("stat/+/STATUS", 0)
	mqttc.loop_start()
	t.sleep(1)
	mqttc.loop_stop()
	for i in range(len(modules)):
		modules[i] = Tasmota(str(modules[i]))

	return(modules)



def test():
	sonoff = Tasmota("sonoff")
	j = 0
	for j in range(5):
		for i in range(len(sonoff.properties)):
			sonoff.properties[i]()
			t.sleep(3)
		j+=1


if __name__ == '__main__':
	test()