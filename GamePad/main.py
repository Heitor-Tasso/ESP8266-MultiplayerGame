from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout

import socket
from utils import get_path

ip_esp = "192.168.4.2"
gateway_esp = "192.168.4.1"
port_esp = 80

Builder.load_file(get_path('main.kv'))

class GamePad(FloatLayout):
	esp = None

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		Clock.schedule_once(self.config)
	
	def config(self, *args):
		# para deixar a bolinha do joystick dentro dele (para resolver o bug)
		self.ids.joystick.on_pos(self.ids.joystick.pos)
		# receber os dados do joystick quando mudar de posição internamente
		self.ids.joystick.bind(pad=self.update_coordinates)
	
	def connect_to_esp(self, *args):
		self.esp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.esp.connect((gateway_esp, port_esp))
		
	def disconnect_esp(self, *args):
		self.esp.close()
	
	def send_informations_esp(self, *args):
		if self.esp is None:
			print('Esp não foi conectado')
			return None
		
		state = 'Teste'
		self.esp.sendall(f'{state}\n'.encode('utf-8'))
	
	def update_coordinates(self, joystick, pad):
		x = str(pad[0])[0:5]
		y = str(pad[1])[0:5]
		radians = str(joystick.radians)[0:5]
		magnitude = str(joystick.magnitude)[0:5]
		angle = str(joystick.angle)[0:5]
		text = "x: {}\ny: {}\nradians: {}\nmagnitude: {}\nangle: {}"
		print(text.format(x, y, radians, magnitude, angle))


class Program(App):
	def build(self):
		return GamePad()

if __name__ == '__main__':
	Program().run()