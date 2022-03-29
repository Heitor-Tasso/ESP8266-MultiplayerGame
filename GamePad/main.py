
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Line
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp

import socket
import json

from utils import get_path, config_path
from functools import partial
from threading import Thread

ip_esp = "192.168.4.2"
gateway_esp = "192.168.4.1"
port_esp = 80

Builder.load_file(get_path('main.kv'))

class GamePad(Screen):

	can_move = True
	move_layout = ObjectProperty(False)
	username = ''
	index_player = '-1'

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		Clock.schedule_once(self.config)
	
	def config(self, *args):
		self.load_json_pos()
		# para deixar a bolinha do joystick dentro dele (para resolver o bug)
		self.ids.joystick.on_pos(self.ids.joystick.pos)
		# receber os dados do joystick quando mudar de posição internamente
		self.ids.joystick.bind(pad=self.update_coordinates)
		Clock.schedule_interval(lambda *a: setattr(self.ids.fps_lbl, 'text', str(Clock.get_fps())), 0.1)

		self.username = input('Seu nome de usuario: ')
		th = Thread(target=self.login_game)
		th.start()

	def login_game(self, *args):
		sucessfull = True
		esp = self.connect_to_esp()
		if esp is None:
			return False
		try:
			esp.send(f'{self.index_player}:np:{self.username}\n'.encode('utf-8'))
		except (ConnectionAbortedError, socket.timeout, TimeoutError):
			self.close_connection_esp(esp)
			return False

		msg = esp.recv(1024).decode('utf-8').strip("\n").split(":")
		print(msg)
		if len(msg) < 2:
			sucessfull = False
		elif msg[0] == "ERRO":
			sucessfull = False
		elif msg[0] == "index":
			self.index_player = msg[1]
		
		self.close_connection_esp(esp)
		return sucessfull
	
	def exit_game(self, *args):
		self.send_informations_with_thread('exit:save')

	def get_json(self, name, *args):
		with open(config_path(name), 'r', encoding='utf-8') as file:
			return json.load(file)

	def set_default_json(self, default_name, update_name, *args):
		default = self.get_json(name=default_name)
		self.update_json(default, name=update_name)

	def update_json(self, new_json, name):
		with open(config_path(name), 'w', encoding='utf-8') as file:
			file.write(json.dumps(new_json, indent=4))

	def load_json_pos(self, *args):
		dic_hints = self.get_json('position')
		for id, hints in dic_hints.items():
			wid = getattr(self.ids, id)
			setattr(wid, 'name', id)
			setattr(wid, 'hint_x', hints['hint_x'])
			setattr(wid, 'hint_y', hints['hint_y'])
	
	def connect_to_esp(self, *args):
		esp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		esp.settimeout(2)
		try:
			esp.connect((gateway_esp, port_esp))
		except (socket.timeout, TimeoutError, OSError):
			print('Não foi conectar ao ESP8266!!')
			return None
		return esp

	def close_connection_esp(self, esp, *args):
		esp.close()

	def send_informations(self, msg, *args):
		esp = self.connect_to_esp()
		if esp is None:
			self.can_move = True
			return None

		try:
			esp.send(f'{self.index_player}:{msg}\n'.encode('utf-8'))
			if msg.find('atk') != -1:
				print('Atacou!!')
			elif msg.find('mov') != -1:
				print('Moveu!!')
				Clock.schedule_once(lambda *a: setattr(self, 'can_move', True), 0.05)
		except (ConnectionAbortedError, socket.timeout, TimeoutError):
			print(f'Tentando mandar: [ {msg} ] novamente!')
			Clock.schedule_once(partial(self.send_informations_esp, msg))
		self.close_connection_esp(esp)
	
	def send_informations_with_thread(self, msg, *args):
		th = Thread(target=self.send_informations, args=(msg, ))
		th.start()

	def update_coordinates(self, joystick, pad):
		if not self.can_move:
			return None
		x, y = tuple(map(lambda n: round(n, 2), pad))
		self.send_informations_with_thread(f'mov:{x},{y}')
		self.can_move = False

	def do_ataque(self, *args):
		self.send_informations_with_thread('atk:espd')

	def on_move_layout(self, *args):
		if not self.move_layout:
			self.clear_grid()
			return None
		self.add_grid()
	
	def update_grid(self, *args):
		self.clear_grid(unbind=False)
		self.add_grid(bind=False)

	def add_grid(self, bind=True, *args):
		content_pad = self.ids.content_pad
		add = content_pad.canvas.before.add
		add(Color(rgba=[0, 0, 1, 1], group='grid_background'))
		# vertical lines
		for x in range(1, round(content_pad.width/dp(10))+1):
			new_x = content_pad.x+(dp(10)*x)
			add(Line(
				points=[new_x, content_pad.y, new_x, content_pad.y+content_pad.height],
				group='grid_background'))
		# horizontal lines
		for y in range(1, round(content_pad.height/dp(10))+1):
			new_y = self.y+(dp(10)*y)
			add(Line(
				points=[content_pad.x, new_y, content_pad.x+content_pad.width, new_y],
				group='grid_background'))
		
		if bind:
			self.bind(size=self.update_grid)
			self.bind(pos=self.update_grid)

	def clear_grid(self, unbind=True, *args):
		content_pad = self.ids.content_pad
		content_pad.canvas.before.remove_group('grid_background')
		if unbind:
			self.unbind(size=self.update_grid)
			self.unbind(pos=self.update_grid)


class Program(App):
	def build(self):
		return GamePad()
	
	def on_stop(self):
		self.root.exit_game()
		return super().on_stop()

if __name__ == '__main__':
	Program().run()
