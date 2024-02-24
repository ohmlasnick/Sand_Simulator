from time import sleep

def simulate():
	my_map = Map(floor=True)
	my_map.show_map()
	while True:
		# create new piece of sand
		sand = Sand(my_map)
		while (not sand.in_void()) and (not sand.is_settled()):
			sleep(0.01)
			if sand.free_below():
				sand.move('down')
			elif sand.free_left():
				sand.move('left-diag')
			elif sand.free_right():
				sand.move('right-diag')
			my_map.frame_counter += 1
			my_map.show_map()
		if sand.in_void():
			return sand.map.count_sand()

class Map():

	def __init__(self, dims=[10, 21], floor=False, platform=False, to_print=False):
		self.floor = floor
		self.scan_map = [[' '] * dims[1] for i in range(dims[0])]
		self.x = len(self.scan_map)
		self.y = len(self.scan_map[0])
		self.frame_counter = 0
		self.to_print = to_print

		# Add a hole in the ceiling for the sand to fall
		self.scan_map[0][dims[1] // 2] = '+'

		# Add a floor for the sand to fall on
		if floor:
			self.add_floor()

		# Add platform to middle 1/3rd of row at half height
		if platform:
			self.add_platform(dims[0] // 2, [dims[1] // 3 - 1, 2 * (dims[1] // 3) - 1])
				
	def count_sand(self):
		count = 0
		for row in self.scan_map:
			for cell in row:
				if cell == '⏺':
					count += 1
		return str(count) + ' grains of sand have fallen!'

	def show_map(self):
		if self.to_print:
			with open('frame{}.txt'.format(self.frame_counter), "a") as f:
				for row in self.scan_map:
					print("".join(row), file=f)
		for row in self.scan_map:
			print("".join(row))


	def expand_map(self, new_x, new_y):
		while new_x >= self.x:
			self.scan_map += [[' '] * self.y]
			self.x += 1
		while new_y >= self.y:
			for row in range(self.x):
				self.scan_map[row].append(' ')
			self.y += 1
		if new_y == -1:
			for row in range(self.x):
				self.scan_map[row] = [' '] + self.scan_map[row]
			self.y += 1

	def add_platform(self, level, span):
		for i in range(span[0], span[1]):
			self.scan_map[level][i] = '⏕'

	def add_floor(self):
		self.expand_map((self.x + 1), 0)
		self.scan_map[self.x - 1] = ['⏕'] * self.y

class Sand():

	def __init__(self, my_map):
		self.pos_x = 0
		self.pos_y = my_map.scan_map[0].index('+')
		self.map = my_map

	def free_below(self):
		if self.on_floor():
			return False
		return self.map.scan_map[self.pos_x + 1][self.pos_y] == ' '

	def free_left(self):
		# If there's no space, you can expand walls
		if self.on_floor():
			return False
		if self.pos_y == 0:
			# but only if right is also blocked
			if not self.free_right():
				self.map.expand_map(0, -1)
				if self.map.floor:
					self.map.scan_map[self.map.x - 1] = ['⏕'] * self.map.y
			else:
				return False
		return self.map.scan_map[self.pos_x + 1][self.pos_y - 1] == ' '

	def free_right(self):
		# If there's no space, you can expand walls
		if self.on_floor():
			return False
		try:
			return self.map.scan_map[self.pos_x + 1][self.pos_y + 1] == ' '
		except:
			self.map.expand_map(0, self.map.y)
			if self.map.floor:
				self.map.scan_map[self.map.x - 1] = ['⏕'] * self.map.y
			return self.map.scan_map[self.pos_x + 1][self.pos_y + 1] == ' '

	def move(self, direc):
		# free previous position if not origin
		if not self.map.scan_map[self.pos_x][self.pos_y] == '+':
			self.map.scan_map[self.pos_x][self.pos_y] = ' '
		self.pos_x += 1
		if direc == 'left-diag':
			self.pos_y -= 1
		elif direc == 'right-diag':
			self.pos_y += 1
		# move sand to new position
		self.map.scan_map[self.pos_x][self.pos_y] = '⏺'

	def is_settled(self):
		return self.on_floor() or ((not self.free_below()) and (not self.free_left()) and (not self.free_right()))

	def on_floor(self):
		if self.map.floor:
			return (self.pos_x + 1) == (self.map.x - 1)
		else:
			return False

	def in_void(self):
		# if there's a floor, no more sand can fall once the hole is clogged
		if self.map.floor:
			return self.is_settled() and self.pos_x == 0 and self.pos_y == self.map.scan_map[0].index('+')
		# if there's no floor, then the sand will keep falling out
		return self.pos_x == (len(self.map.scan_map) - 1)

print(simulate())
