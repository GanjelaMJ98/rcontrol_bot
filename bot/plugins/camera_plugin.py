from .Plugin import Property, Plugin
from cv2 import *
import os, shutil
import time as t


class Camera(Plugin):
	def __init__(self,name):
		self.name = name
		self.properties = []
		self.information = dict()
		self.add_property("photo", self.send_photo,answer_type = 'photo')
		self.cnt = 0
		self.cnt_max = 5
		try:
			os.mkdir("/etc/Bot/images")
		except FileExistsError:
			shutil.rmtree("/etc/Bot/images")
			os.mkdir("/etc/Bot/images")

	def __str__(self):
		return("Camera - " + self.name)

	def take_photo(self):
		if(self.cnt>self.cnt_max):
			shutil.rmtree("/etc/Bot/images")
			os.mkdir("/etc/Bot/images")
			self.cnt = 0
		cam = VideoCapture(0)
		s, img = cam.read()
		if s:
			imwrite("/etc/Bot/images/image{0}.jpg".format(self.cnt),img)
			self.cnt+=1
		cam.release()
		s,img = 0,0

	def send_photo(self):
		self.take_photo()
		return("/etc/Bot/images/image{0}.jpg".format(self.cnt - 1))


	
def get_plugins():
	plugins = []
	camera = Camera("Camera")
	plugins.append(camera)
	return plugins



def test():
	camera = Camera("Camera")
	for j in range(camera.cnt_max +2):
		for i in range(len(camera.properties)):
			ans = camera.properties[i].function()
			print(ans)
			t.sleep(3)


if __name__ == '__main__':
	test()