from kivy.app import App
from kivy.graphics import Rectangle, Color
from kivy.properties import NumericProperty

class BaseFloat(object):
	hint_x = NumericProperty(0.5)
	hint_y = NumericProperty(0.5)
	move_layout = False

	def on_touch_down(self, touch):
		root = App.get_running_app().root
		if self.collide_point(*touch.pos):
			if root.move_layout:
				self.move_layout = True
				self.draw_background()
				return False
		return super().on_touch_down(touch)
	
	def on_touch_up(self, touch):
		if self.move_layout:
			self.move_layout = False
		return super().on_touch_up(touch)
	
	def on_touch_move(self, touch):
		root = App.get_running_app().root
		if root.move_layout and self.move_layout:
			print('Movendo')
			tx, ty = touch.pos
			self.hint_x =  (tx + (self.width*0.5)) / root.width
			self.hint_y =  (ty + (self.height*0.5)) / root.height
			
			self.x = root.x+(root.width*self.hint_x)-(self.width*0.5)
			self.y = root.y+(root.height*self.hint_y)-(self.height*0.5)
			return False
		return super().on_touch_move(touch)
	
	def draw_background(self, *args):
		pass