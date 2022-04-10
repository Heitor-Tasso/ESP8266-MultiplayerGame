
from multiprocessing import parent_process
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty
from kivy.graphics import Color, Line
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from random import random, randint
from kivy.metrics import dp
from uix.joystick import Joystick
from uix.icons import (
    FloatButtonIcon, ToggleButtonIcon,
    ButtonIcon, AnchorIcon, FloatLifes)

import socket
import json, time

from utils import get_path, config_path
from functools import partial
from threading import Thread

ip_esp = "192.168.4.2"
gateway_esp = "192.168.4.1"
port_esp = 80

HOST = ip_esp
PORT = randint(1024, 65000)

print("HOST -> ", HOST)
print("PORT -> ", PORT)

Builder.load_file(get_path('gamepad.kv'))

class GamePad(Screen):
    conn = None
    can_move = True
    move_layout = ObjectProperty(False)
    username = ''
    connected = False
    index_player = -1
    lifes = 0
    name_players = ListProperty(['', '', '', '', ''])
    pos_players = ListProperty([[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]])
    players_color = ListProperty([[1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1]])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.config)
        self.start_server()
    
    def start_server(self, *args):
        self.conn = socket.socket()
        try:
            self.conn.bind((HOST, PORT))
        except OSError:
            self.conn = None
            Clock.schedule_once(self.start_server, 2)
            print("Não iniciou o server!!")
            return False
        self.conn.settimeout(2.0)
        Thread(target=self.start_listen).start()
        print(self.conn.getsockname())
        print("Server iniciou.")

    def config(self, *args):
        self.load_json_pos()
        # para deixar a bolinha do joystick dentro dele (para resolver o bug)
        self.ids.joystick.on_pos(self.ids.joystick.pos)
        # receber os dados do joystick quando mudar de posição internamente
        self.ids.joystick.bind(pad=self.update_coordinates)
    
    def start_listen(self, *args):
        if self.conn is None:
            print("Parou o server!!")
            return False
        try:
            self.conn.listen()
            conn, addr = self.conn.accept()
            data = conn.recv(1024)
            self.update_from_esp(data)
        except (socket.timeout, TimeoutError):
            pass
        Thread(target=self.start_listen).start()

    def start_game(self, *args):
        self.connected = True
        self.manager.current = 'gamepad'
        self.ids.lifes.clear_lifes()
        self.ids.lifes.show_lifes(self.lifes)
        self.players_color[self.index_player] = [0, 0, 1, 1]

    def exit_game(self, *args):
        self.manager.current = 'login'
        self.conn = None
        if not self.username:
            return None

        self.send_informations_with_thread('exit:save')

    def update_from_esp(self, data):
        resp = data.decode('utf-8').strip("\n").split(":")
        if len(resp) < 1:
            return None

        if resp[0] == 'life':
            if self.lifes != int(resp[1]):
                self.lifes = int(resp[1])
                self.ids.lifes.clear_lifes()
                self.ids.lifes.show_lifes(self.lifes)
                if self.lifes == 0:
                    print("MORRI!!")
                self.connected = True
                print(resp)
        if resp[2] == 'pos':
            dconv = lambda pos: [dp(float(pos[0])), dp(float(pos[1]))]
            self.pos_players = tuple(map(lambda p: dconv(p.split(',')), resp[3:-1]))
        else:
            print(resp)

    def get_json(self, name, *args):
        with open(config_path(name), 'r', encoding='utf-8') as file:
            return json.load(file)

    def reload_json_position(self, default_name, update_name, *args):
        default = self.get_json(name=default_name)
        self.update_json(default, name=update_name)
        self.load_json_pos()

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
            setattr(wid, 'width', dp(hints['width']))
            setattr(wid, 'height', dp(hints['height']))
    
    def connect_to_esp(self, force=False, *args):
        if not self.connected and not force:
            return None
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
                Clock.schedule_once(lambda *a: setattr(self, 'can_move', True), 0.01)
            elif msg.find('exit') != -1:
                self.connected = False
                print(self.username + " saiu!")
                self.username = ''
        except (ConnectionAbortedError, socket.timeout, TimeoutError):
            print(f'Tentando mandar: [ {msg} ] novamente!')
            dt = round(min(random(), random()), 2)
            Clock.schedule_once(partial(self.send_informations, msg), dt)
        self.close_connection_esp(esp)
    
    def send_informations_with_thread(self, msg, *args):
        th = Thread(target=self.send_informations, args=(msg, ))
        th.start()

    def update_coordinates(self, joystick, pad):
        if not self.can_move:
            return None
        x, y = tuple(map(lambda n: round(n, 2), pad))
        angle = round(joystick.angle)
        self.send_informations_with_thread(f'mov:{x},{y},{angle}')
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
        self.clear_grid(bind)
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
    
    def update_middle_line(self, *args):
        self.clear_middle_line(unbind=False)
        self.add_middle_line(bind=False)

    def add_middle_line(self, bind=True, *args):
        self.clear_middle_line(bind)
        content_pad = self.ids.content_pad
        add = content_pad.canvas.before.add
        add(Color(rgba=[1, 0, 0, 1], group='middle_background'))
        add(Line(
            points=[content_pad.x+(content_pad.width/2), content_pad.y,
                    content_pad.x+(content_pad.width/2), content_pad.y+content_pad.height],
            group='middle_background'))
        
        if bind:
            self.bind(size=self.update_middle_line)
            self.bind(pos=self.update_middle_line)
    
    def clear_middle_line(self, unbind=True, *args):
        content_pad = self.ids.content_pad
        content_pad.canvas.before.remove_group('middle_background')
        if unbind:
            self.unbind(size=self.update_middle_line)
            self.unbind(pos=self.update_middle_line)

    def add_line(self, pos, name, *args):
        content_pad = self.ids.content_pad
        add = content_pad.canvas.before.add
        add(Color(rgba=[1, 0, 0, 1], group=name))
        if name.endswith('x'):
            pos = [pos, content_pad.y, pos, content_pad.y+content_pad.height]
        elif name.endswith('y'):
            pos = [content_pad.x, pos, content_pad.x+content_pad.width, pos]
        add(Line(points=pos, group=name))
        
    def remove_line(self, name, *args):
        content_pad = self.ids.content_pad
        content_pad.canvas.before.remove_group(name)

    def animate_border_top(self, y, duration, wid, state):
        if wid.last_state == state:
            return y
        
        Animation(y=y, d=duration).start(wid)
        wid.last_state = state
        return wid.y