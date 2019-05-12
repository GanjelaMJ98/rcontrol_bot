from .Plugin import Property, Plugin
import time as t
import os
import sys
from pySMART import Device

class SMART(Plugin):
	def __init__(self,name):
		self.name = name
		self.properties = []
		self.information = dict()
		self.add_property("smart_check", self.smart_check)
		self.add_property("health_check", self.health_check)

	def __str__(self):
		return("SMART - " + self.name)

	def getDf(self,path):
		df = os.popen("df -h |grep " + path)
		i = 0
		line = []           # список точек монтирования с данными(в конце добавляются пустые строки)
		num = 0             # счетчик непустых строк
		while True:
			i = i + 1
			line.append(df.readline())          # читаем вывод df -h
			if i==5:                            # до 5ой строки
				for i in range(5):
					if(line[i] != ''):          # выявляем пустые строки
						num+=1
				return line,num

	def health_check(self):
		files = os.listdir('/dev')
		disks = list(filter(lambda x: x.startswith('sd'),files))
		disks = list(filter(lambda x: x.isalpha(),disks))
		disks.sort()
		i = 0
		while i < len(disks):
			sk = Device('/dev/' + disks[i])
			if(sk.assessment == "PASS"):
				return ("SMART status is good")
			else:
				return ("SMART status is not good")


	def smart(self,disk):
		diskname = ""
		disk_root = []
		num = 0
		disk_root,num = self.getDf(disk)
		sk = Device(disk)
		if(sk.assessment == "PASS" ):
			status = True
		else:
			status = False
		answer = str(disk) + "\n\n" + '''Serial -> {0}\n Firmware -> {1}\n Model -> {2}
        \nS.M.A.R.T. status is good: {3}\nDevice size: {4}'''.format(str(sk.serial),
                                                                    str(sk.firmware),
                                                                    str(sk.model),
                                                                    str(status),
                                                                    str(sk.capacity))
		for i in range(num):                              #проход по непустым строкам
			root_info = disk_root[i].split()[0:6]         #преобразование строки в список значений
            #формирование строки информации о разделе диска
			root_info_str = "\n\nPartition: {0}\nSize: {1}\nUsed: {2}\nAvail: {3}\nUse(%): {4}\nMount point: {5}\n\n".format(str(root_info[0]),
                                                                                                                    str(root_info[1]),
                                                                                                                    str(root_info[2]),
                                                                                                                    str(root_info[3]),
                                                                                                                    str(root_info[4]),
                                                                                                                    str(root_info[5]))
            #формирование окончательного ответа
			answer = answer + root_info_str
        
		return answer


	def smart_check(self):
		answer = ""
		files = os.listdir('/dev')
		disks = list(filter(lambda x: x.startswith('sd'),files))
		disks = list(filter(lambda x: x.isalpha(),disks))
		disks.sort()
		i = 0
		while i < len(disks):
			answer += self.smart('/dev/' + disks[i])
			i += 1
		return answer

def get_plugins():
	plugins = []
	smart = SMART("S.M.A.R.T")
	plugins.append(smart)
	return plugins



def test():
	smart = SMART("SMART")
	j = 0
	for j in range(5):
		for i in range(len(smart.properties)):
			ans = smart.properties[i].function()
			print(ans)
			t.sleep(3)
		j+=1


if __name__ == '__main__':
	test()