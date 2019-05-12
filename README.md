## Python Remove Control Telegram Bot

Introduction
---
---
This is a telegram bot project for remote control of your computer, smart home and anything you want.

In addition to the bot, this project has an ability to use your own plugins. To do this, use the plugin and property classes. Description of the classes can be found in bot/plugins.

Telegram API support
---
---
Below you can find the documentation for the python-telegram-bot library

 [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - GitHub
 
 [python-telegram-bot documentation](https://github.com/python-telegram-bot/python-telegram-bot) -  Documentation

Installation
---
---
Install python, pip, setuptools:
```sh
$ sudo apt-get install python3
$ sudo apt install python3-pip
$ pip3 install setuptools
```
Install bot:
```sh
$ sudo python3 setup.py install
```
Further configuration is described in the next command.
```sh
$ sudo telegram_bot_settings
```
Start:
```sh
$ sudo telegram_bot_start
```

Plugins
---
---
| Module name | Description                    |
| ------------- | ------------------------------ |
| Сamera     | Takes a picture from the camera     |
| S.M.A.R.T.   | Сhecks the attributes of the hard disk |
| Tasmota   | Control of Sonoff devices |

Simple plugin example
---
---
```python
from Plugin import Property, Plugin

class Test(Plugin):
	def __init__(self,name):
		self.name = name
		self.properties = list()
		self.information = dict()
		self.add_property("test", self.test_function, answer_type = 'text')

	def test_function(self):
		answer = "Hello, World!"
		return answer


def get_plugins():
	plugins = []
	test_plugin = Test("Hello_World")
	plugins.append(test_plugin)
	return plugins
```
