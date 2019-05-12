#!/usr/bin/env python
# -*- coding: utf8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackQueryHandler,ConversationHandler,RegexHandler
import logging
import os
import json
import sys
from ctypes import *
import threading
import time
from pySMART import Device
from .plugins.Plugin import Property, Plugin

MODULE, PROPERTY,TIME,DAY,STOP,NONE = range(6)
THREAD_WORKS = False
current_module = None
task_list = []

mutex = threading.RLock()

# Basic configurations
filename = '/etc/Bot/config.json'
file = open(filename,"r+")
pars_string = json.load(file)
file.close()

# Logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
	"""Send a message when the command /start is issued."""
	update.message.reply_text('Hi!')


def help(bot, update):
	"""Send a message when the command /help is issued."""
	update.message.reply_text('Help!')


def echo(bot, update):
	"""Echo the user message."""
	update.message.reply_text(update.message.text)


def error(bot, update, error):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, error)

def check_level(update):
	i = 0
	user = update.message['chat']
	while i < len(pars_string['whitelist']):
		if user['username'] == pars_string['whitelist'][i]['tlg_username']:
			return pars_string['whitelist'][i]['level']
		i+=1
	return -1


def start_property(update,module_n,property_n):
	current_time = time.localtime()
	user_level = check_level(update)
	if(user_level < 0):
		update.message.reply_text("Sorry, you're not on the whitelist")
		task_list[module_n].properties[property_n].active_flag = False
	else:
		if(task_list[module_n].properties[property_n].level <= check_level(update)):
			if(task_list[module_n].properties[property_n].answer_type == "photo"):
				answer = task_list[module_n].properties[property_n].function()
				update.message.reply_photo(photo = open(answer, 'rb'))
				task_list[module_n].properties[property_n].time = current_time.tm_sec
			else:
				answer = task_list[module_n].properties[property_n].function()
				update.message.reply_text(answer)
				task_list[module_n].properties[property_n].time = current_time.tm_sec
		else:
			update.message.reply_text("Sorry, your level is lower than required")
			task_list[module_n].properties[property_n].active_flag = False



# Starting functions with time checking
def worker(bot, update):
	while True:
		with mutex:
			if task_list_is_empty() == True:
				global THREAD_WORKS
				THREAD_WORKS = False
				logger.info("The Worker is stopped, task_list is empty.")
				return 0
			current_time = time.localtime()
			for i in range(len(task_list)):
				for j in range(len(task_list[i].properties)):
					if(task_list[i].properties[j].active_flag == True):
						if(task_list[i].properties[j].delay == None):
							continue
						if(task_list[i].properties[j].time == None):
							start_property(update,i,j)
						elif(task_list[i].properties[j].time != None):
							if((current_time.tm_sec < task_list[i].properties[j].time and ((60 - task_list[i].properties[j].time) + current_time.tm_sec)>task_list[i].properties[j].delay)):
								start_property(update,i,j)
							if(current_time.tm_sec > task_list[i].properties[j].time and ((current_time.tm_sec - task_list[i].properties[j].time) > task_list[i].properties[j].delay)):
								start_property(update,i,j)
					elif(task_list[i].properties[j].timer == True):
						if(task_list[i].properties[j].day != None) and (task_list[i].properties[j].hour != None):
							if((task_list[i].properties[j].day == current_time.tm_wday)):
								if((task_list[i].properties[j].hour <= current_time.tm_hour)):
									if((task_list[i].properties[j].min <= current_time.tm_min)):
										if(check_level(update) < 0):
											update.message.reply_text("Sorry, you're not on the whitelist")
											task_list[i].properties[j].timer = False
										elif(check_level(update) < task_list[i].properties[j].level):
											update.message.reply_text("Sorry, your level is lower than required")
											task_list[i].properties[j].timer = False
										else:
											answer = task_list[i].properties[j].function()
											if(task_list[i].properties[j].answer_type == "photo"):
												update.message.reply_text("TIMER\n")
												update.message.reply_photo(open(answer,'rb'))
											else:
												update.message.reply_text("TIMER\n" + answer)
											task_list[i].properties[j].day = None
											task_list[i].properties[j].hour = None
											task_list[i].properties[j].min = None
											task_list[i].properties[j].timer = False




# Main thread
def start_thread(bot, update):
		t = threading.Thread(target = worker, args = (bot,update,))
		t.daemon = True
		t.start()

def stop_thread(bot, update):
	with mutex:
		del task_list[:]




# Plugins
def add_plugins():
	#from .plugins import tasmota_plugin
	#task_list.extend(tasmota_plugin.get_plugins())
	from .plugins import camera_plugin
	task_list.extend(camera_plugin.get_plugins())
	from .plugins import SMART_plugin
	task_list.extend(SMART_plugin.get_plugins())
	logger.info("Plugins:\n{0}".format(task_list))


def search_module(name):
	for module in task_list:
		if module.name == name:
			return module
		else:
			continue
	logger.error("Module not found")
	return -1

def search_property(name):
	for module in task_list:
		for prop in module.properties:
			if prop.name == name:
				return prop
			else:
				continue
	logger.error("Property not found")
	return -1



# Buttons
def show_modules(bot,update):
	keyboard = [[]]
	for i in range(len(task_list)):
		keyboard[0].append(task_list[i].name)
	update.message.reply_text(
		'Hi! Please choice module: ',
		reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
	return MODULE


def show_properties(bot, update):
	user = update.message.from_user
	keyboard=list()
	button = list()
	logger.info("Module of %s: %s", user.first_name, update.message.text)
	global current_module
	current_module = search_module(update.message.text)
	for i in range(len(current_module.properties)):
		button.append(current_module.properties[i].name)
		keyboard.append(button)
		button = list()
	update.message.reply_text(
		'Hi! Please choice property: ',
		reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
	return PROPERTY


def timeing(bot, update):	
	user = update.message.from_user
	logger.info("Property of %s: %s", user.first_name, update.message.text)
	global current_module
	for i in range(len(current_module.properties)):
		if current_module.properties[i].name == update.message.text:
			current_module.properties[i].active_flag = True

	keyboard = [[InlineKeyboardButton("3 sec", callback_data='3'),
				 InlineKeyboardButton("5 sec", callback_data='5')],
				[InlineKeyboardButton("10 sec", callback_data='10')],
				[InlineKeyboardButton("Once", callback_data='0')]]

	reply_markup = InlineKeyboardMarkup(keyboard)

	update.message.reply_text('Please choose the time:', reply_markup=reply_markup)
	return ConversationHandler.END


def button_time(bot, update):
	query = update.callback_query
	global current_module
	for i in range(len(current_module.properties)):
		if current_module.properties[i].active_flag == True and current_module.properties[i].delay == None:
			if int(query.data) == 0:
				# TODO: add level check
				answer = current_module.properties[i].function()
				logger.info("Time for %s: %s",current_module.properties[i].name , query.data)
				if current_module.properties[i].answer_type == "photo":
					query.message.reply_photo(open(answer,'rb'))
				else:
					bot.edit_message_text(text=answer,chat_id=query.message.chat_id,message_id=query.message.message_id)
				current_module.properties[i].active_flag = False
			else:
				current_module.properties[i].delay = int(query.data)
				logger.info("Time for %s: %s",current_module.properties[i].name, query.data)
				task_start(bot,query)
				bot.edit_message_text(text="Selected time: {} sec.".format(query.data),
						  chat_id=query.message.chat_id,
						  message_id=query.message.message_id)
	current_module = None


def keyboard_day(bot,update):
	user = update.message.from_user
	logger.info("Property of %s: %s", user.first_name, update.message.text)
	global current_module
	for i in range(len(current_module.properties)):
		if current_module.properties[i].name == update.message.text:
			current_module.properties[i].timer = True

	keyboard = [[InlineKeyboardButton("Monday", callback_data='0')],
				[InlineKeyboardButton("Tuesday", callback_data='1')],
				[InlineKeyboardButton("Wednesday", callback_data='2')],
				[InlineKeyboardButton("Thursday", callback_data='3')],
				[InlineKeyboardButton("Friday", callback_data='4')],
				[InlineKeyboardButton("Saturday", callback_data='5')],
				[InlineKeyboardButton("Sunday", callback_data='6')]]

	reply_markup = InlineKeyboardMarkup(keyboard)

	update.message.reply_text('Please choose the day:', reply_markup=reply_markup)
	return TIME




def button_day(bot, update):
	with mutex:
		query = update.callback_query
		global current_module
		for i in range(len(current_module.properties)):
			if current_module.properties[i].timer == True and current_module.properties[i].day == None:
				current_module.properties[i].day = int(query.data)
				logger.info("Day for %s: %s",current_module.properties[i].name, query.data)
				task_start(bot,query)
				bot.edit_message_text(text="Selected day: {}.\nTime: ".format(query.data),
						  chat_id=query.message.chat_id,
						  message_id=query.message.message_id)
		return DAY


def timer(bot,update):
	with mutex:
		time = update.message.text
		global current_module
		for i in range(len(current_module.properties)):
			if current_module.properties[i].timer == True and current_module.properties[i].hour == None:
				current_module.properties[i].hour = int(time[0:2:1])
				current_module.properties[i].min = int(time[-2::1])
				update.message.reply_text('Module: {0}\nProperty: {1}\nDay: {2}\nTime: {3}:{4}\n'.format(current_module.name,
																									current_module.properties[i].name,
																									current_module.properties[i].day,
																									current_module.properties[i].hour,
																									  current_module.properties[i].min))
				
		current_module = None
		task_start(bot,update)
		return ConversationHandler.END
	

def task_start(bot,update):
	global THREAD_WORKS
	with mutex:
		if(not THREAD_WORKS):
			start_thread(bot,update)
			
			THREAD_WORKS = True
		#else:
			#print("thread works")





# Stop functions
def show_active_properties(bot,update):
	keyboard = [[]]
	keyboard[0].append("All")
	for i in range(len(task_list)):
		for j in range(len(task_list[i].properties)):
			if task_list[i].properties[j].active_flag == True:
				keyboard[0].append(task_list[i].properties[j].name)
			elif task_list[i].properties[j].timer == True:
				keyboard[0].append(task_list[i].properties[j].name)
		
	update.message.reply_text(
		'Hi! Please choice function to stop: ',
		reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
	return STOP


def stop_property(bot,update):
	with mutex:
		if(update.message.text == "All"):
			for i in range(len(task_list)):
				for j in range(len(task_list[i].properties)):
					if(task_list[i].properties[j].active_flag == True):
						task_list[i].properties[j].active_flag = False
						task_list[i].properties[j].delay = None
						task_list[i].properties[j].time = None
					elif(task_list[i].properties[j].timer == True):
						task_list[i].properties[j].timer = False
						task_list[i].properties[j].day = None
						task_list[i].properties[j].hour = None
						task_list[i].properties[j].min = None
			user = update.message.from_user
			logger.info("All functions of %s are stopped", user.first_name)
		else:
			current_property = search_property(update.message.text)
			current_property.active_flag = False
			current_property.timer = False
			current_property.delay = None
			current_property.time = None
			current_property.day = None
			current_property.hour = None
			current_property.min = None
			user = update.message.from_user
			logger.info("Function of %s: %s - STOP", user.first_name, update.message.text)
	return ConversationHandler.END

def task_list_is_empty():
	flag = True
	for i in range(len(task_list)):
			for j in range(len(task_list[i].properties)):
				if task_list[i].properties[j].delay != None or task_list[i].properties[j].day !=None:
					flag = False
	return flag









def main():
	"""Start the bot."""
	logger.info("START")

# PROXY	
	if(pars_string['proxy_url'] != "http://proxy_ip:port/"):
		REQUEST_KWARGS = {
			'proxy_url': pars_string['proxy_url'],
			'read_timeout': 10,
			'connect_timeout': 10
		}
		updater = Updater(pars_string["token"], request_kwargs = REQUEST_KWARGS)
	else:
		updater = Updater(pars_string["token"])


	# Get the dispatcher to register handlers
	dp = updater.dispatcher
	add_plugins()
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("echo", echo))

	# Timer
	check_handler_timer = ConversationHandler(
		entry_points=[CommandHandler('timer', show_modules)],
		states={
			PROPERTY:  [MessageHandler(Filters.text, keyboard_day)],
			MODULE: [MessageHandler(Filters.text, show_properties)],
			TIME: [CallbackQueryHandler(button_day)],
			DAY: [MessageHandler(Filters.text, timer)]
		},fallbacks =[CommandHandler("help", help)]
		)

	# Modules
	check_handler_modules = ConversationHandler(
		entry_points=[CommandHandler('modules', show_modules)],
		states={
			PROPERTY:  [MessageHandler(Filters.text, timeing)],
			MODULE: [MessageHandler(Filters.text, show_properties)]},
		fallbacks =[CommandHandler("help", help)])



	stop_handler = ConversationHandler(
		entry_points=[CommandHandler('stop', show_active_properties)],
		states={
			STOP: [MessageHandler(Filters.text, stop_property)]},
		fallbacks =[CommandHandler("help", help)])

	dp.add_handler(check_handler_timer)
	dp.add_handler(check_handler_modules)
	dp.add_handler(stop_handler)
	dp.add_handler(CallbackQueryHandler(button_time))


	# log all errors
	dp.add_error_handler(error)


	# Start the Bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':

	if settings.main() == 0:
		main()
	else:
		print("Error settings")
		print("Check the file /etc/Bot/config.json")
		