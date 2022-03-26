from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout

import socket

ip_esp = "192.168.4.2"
gateway_esp = "192.168.4.1"
port_esp = 80

Builder.load_file('main.kv')

class GamePad(FloatLayout):
	esp = None

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		Clock.schedule_once(self.connect_to_esp)
	
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


class Program(App):
	def build(self):
		return GamePad()

if __name__ == '__main__':
	Program().run()