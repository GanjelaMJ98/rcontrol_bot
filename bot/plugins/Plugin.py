class Property:
	def __init__(self,name,function,answer_type):
		self.name = name
		self.function = function

		self.timer = False
		self.day = None
		self.hour = None
		self.min = None

		self.active_flag = False
		self.time = None
		self.delay = None

		self.answer_type = answer_type
		self.level = 1


class Plugin:
	def __init__(self, name):
		self.properties = []
		self.name = name
	def add_property(self,name, function,answer_type = 'text'):
		new_prorety = Property(name, function,answer_type)
		self.properties.append(new_prorety)
	def delete_property(self,name):
		pass

