from setuptools import setup,find_packages
from os.path import join,dirname

setup(
	name = "bot",
	version = "0.1",
	packages = find_packages(),
	long_description = open(join(dirname(__file__),"README.txt")).read(),
	install_requires = [
	'python-telegram-bot==11.1.0',
	'paho-mqtt==1.4.0',
	'opencv-python==3.4.0.12',
	'pySMART.smartx==0.3.9'],
	entry_points = {
		'console_scripts':
			['telegram_bot_settings = bot.configs.settings:main',
			 'telegram_bot_start = bot.core:main']
	}
)

