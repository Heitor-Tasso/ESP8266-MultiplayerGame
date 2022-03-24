from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, NumericProperty, ObjectProperty, OptionProperty 

Builder.load_file('main.kv')

class FloatRectangleButton(FloatLayout):
    float = OptionProperty('left-middle', options=('left-bottom', 'left-top', 'right-middle', 'right-bottom', 'right-top'))
    pos_y = NumericProperty(0)

class FloatEllipseButton(FloatLayout):
    pass

class GamePad(BoxLayout):
	pass

class Program(App):
	def build(self):
		return GamePad()

if __name__ == '__main__':
	Program().run()