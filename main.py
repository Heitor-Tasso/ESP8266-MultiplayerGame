from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

Builder.load_file('main.kv')

class GamePad(BoxLayout):
	pass

class Program(App):
	def build(self):
		return GamePad()

if __name__ == '__main__':
	Program().run()