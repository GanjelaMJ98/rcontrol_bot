import os
import socket
import json

# Basic configurations
config = dict(
	host_name	=	None,
	host_port	=	None,
	token 		=	None,
	whitelist	=	[
		{
			"tlg_username": None,
			"level": None
		}
	])

# Check MQTT broker installation
def mosquitto_check():
	df = os.popen("dpkg-query -l mosquitto |grep ii")
	line = []
	line.append(df.readline())
	if(line[0] == ""):
		print("-----------------------------------------")
		print("Please, install mosquitto MQTT broker (https://mosquitto.org)")
		print("-$ sudo apt-get install mosquitto mosquitto-clients")
		print("-----------------------------------------")
		return -1
	else:
		print("mosquitto is installed")
		return 0 
 
def check_in():
	f = os.popen('hostname -I')
	ip = f.read().rstrip()
	config['proxy_url'] = "http://proxy_ip:port/"
	config['host_name'] = ip
	config['host_port'] = 1883
	print("""
		Please, create a new bot in BotFather.

		Go to the BotFather (@BotFather), then create new bot by sending the /newbot command.
		Follow the steps until you get the username and token for your bot.
		You can go to your bot by accessing this URL: https://telegram.me/YOUR_BOT_USERNAME and
		token should looks like this: 704418931:AAETcZ************** """)
	token = input("Bot Token:\n")
	config['token'] = token
	tlg_username = input("Your Telegram Username:\n")
	config['whitelist'][0]['tlg_username'] = tlg_username
	config['whitelist'][0]['level'] = 1
	return 0


def main():
	i = 0
	i += mosquitto_check()
	i += check_in()
	if(i == 0):
		try:
			os.mkdir("/etc/Bot")
		except FileExistsError:
			print('Folder /etc/Bot exists')

		with open('/etc/Bot/config.json', 'w') as outfile:
			json.dump(config,outfile,indent=4)

		print("Check the file /etc/Bot/config.json if you want to change the settings of the bot")
		os.popen("gedit /etc/Bot/config.json")
		return 0 
	else:
		return -1

if __name__ == '__main__':
	main()
