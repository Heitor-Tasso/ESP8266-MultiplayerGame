
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from uix.floatwidget import BaseFloat

import socket
from utils import get_path
from functools import partial
from threading import Thread

ip_esp = "192.168.4.2"
gateway_esp = "192.168.4.1"
port_esp = 80

Builder.load_file(get_path('main.kv'))

class CustomButton(BaseFloat, ButtonBehavior, Image):
	pass

class GamePad(FloatLayout):

	can_move = True
	move_layout = False

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		Clock.schedule_once(self.config)
	
	def config(self, *args):
		# para deixar a bolinha do joystick dentro dele (para resolver o bug)
		self.ids.joystick.on_pos(self.ids.joystick.pos)
		# receber os dados do joystick quando mudar de posição internamente
		self.ids.joystick.bind(pad=self.update_coordinates)
		Clock.schedule_interval(lambda *a: setattr(self.ids.fps_lbl, 'text', str(Clock.get_fps())), 0.1)
	
	def connect_to_esp(self, *args):
		esp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		esp.settimeout(2)
		try:
			esp.connect((gateway_esp, port_esp))
		except (socket.timeout, TimeoutError):
			return None
		return esp

	def close_connection_esp(self, esp, *args):
		esp.close()

	def send_informations_esp(self, msg, *args):
		esp = self.connect_to_esp()
		if esp is None:
			print('Não foi conectar ao ESP8266!!')
			self.can_move = True
			return None

		try:
			esp.send(f'{msg}\n'.encode('utf-8'))
			if msg.find('atk') != -1:
				print('Atacou!!')
			elif msg.find('mov') != -1:
				print('Moveu!!')
				Clock.schedule_once(lambda *a: setattr(self, 'can_move', True), 0.05)
		except (ConnectionAbortedError, socket.timeout, TimeoutError):
			print(f'Tentando mandar: [ {msg} ] novamente!')
			Clock.schedule_once(partial(self.send_informations_esp, msg))
		self.close_connection_esp(esp)
	
	def send_with_thread(self, msg, *args):
		th = Thread(target=self.send_informations_esp, args=(msg, ))
		th.start()

	def update_coordinates(self, joystick, pad):
		if not self.can_move:
			return None
		
		x, y = tuple(map(lambda n: round(n, 2), pad))
		self.send_with_thread(f'mov:{x},{y}')
		self.can_move = False

	def do_ataque(self, *args):
		self.send_with_thread('atk:espd')

class Program(App):
	def build(self):
		return GamePad()

if __name__ == '__main__':
	Program().run()
