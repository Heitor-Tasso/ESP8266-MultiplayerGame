from kivy.lang import Builder
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

import socket
from threading import Thread

Builder.load_string("""

#:import IconInput uix.inputs.IconInput
#:import ButtonEffect uix.buttons.ButtonEffect

#:import icon utils.icon
#:import background utils.background

<Login>:
    AnchorLayout:
        anchor_x: 'center'
        anchor_y: 'center'
        canvas:
            Color:
                rgba:[1,1,1,1]
            Rectangle:
                size:self.size
                pos:self.pos
                source:background('Fundo')
        BoxLayout:
            orientation:'vertical'
            id:box_principal
            size_hint:None,None
            size:root.width/1.8, root.height/1.1
            on_size:root.size_login(self, args[1])
            canvas:
                Color:
                    rgba:[0, 0.5, 0.7, .6]
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius:[30,30]
                    source:background('Plano_de_Fundo')
            AnchorLayout:
                Label:
                    text:'Login'
                    font_size:'30sp'
            AnchorLayout:
                size_hint_y:None
                height:'140dp'
                on_size:
                    self.padding= [self.width/9,dp(10),self.width/9,10] if \
                    self.width >= dp(600) else [dp(20),dp(10),dp(20),dp(10)]
                BoxLayout:
                    orientation:'vertical'
                    spacing:'10dp'
                    IconInput:
                        id: input
                        icon_left_source:icon('user1')
                        label_text:'Username'
                        label_pos_color:[0.6, 1.0, 1, 1]
                        
                    IconInput:
                        icon_left_source:icon('password1')
                        icon_right_state_sources:[icon('unsee_eye'), icon('see_eye')]
                        icon_right_color_pos:[0,10,0,1]
                        icon_right_color:[0.0, 0.4375, 0.7, 1]
                        icon_right_effect_color:[0.0, 0.6, 0.6, 1]
                        label_pos_color:[0.6, 1.0, 1, 1]
                        hide:True if self.ids.button_right.state == 'normal' else False
                        label_text:'Password'
                        radius:[dp(15),dp(19),1,dp(15)]
            AnchorLayout:
                size_hint_y:None
                height:'50dp'
                BoxLayout:
                    size_hint_x:None
                    width:'130dp'
                    CheckBox:
                        size_hint_x:0.18
                        id:r_check
                    Button:
                        background_color:[1,1,1,0]
                        text:'Lembrar Senha'
                        on_press:r_check.active = True if r_check.active == False else False
            AnchorLayout:
                padding:[dp(10),dp(20),dp(10),1]
                size_hint_y:None
                height:'60dp'
                ButtonEffect:
                    text:'Entrar'
                    size_hint_x:None
                    width:'150dp'
                    color_background:[[0.099, 0.32, 1, 1], [0,0.5,30,1]]
                    color_effect:[0,3,0,0.4]
                    radius:[dp(15),dp(15),dp(15),dp(15)]
                    on_press: root.start_thread_login()
            Widget:
                size_hint_y:0.3
            AnchorLayout:
                size_hint_y:None
                height:'40dp'
                Button:
                    text:'Esqueceu sua senha?'
                    color:[1,1,1,1] if self.state == 'normal' else [0,10,0,1]
                    size_hint_x:None
                    width:'200dp'
                    background_color:[1,1,1,0]
            Widget:
                size_hint_y:0.3

""")

class Login(Screen):
    started = False
    gamepad = ObjectProperty(None)

    def start_thread_login(self, *args):
        if self.started:
            return None
        
        username = self.ids.input.ids.input.text
        if not username:
            return None

        self.started = True
        self.gamepad.username = username
        th = Thread(target=self.login_game)
        th.start()
    
    def login_game(self, *args):
        sucessfull = True
        esp = self.gamepad.connect_to_esp()
        if esp is None:
            self.started = False
            return False
        try:
            esp.send(f'{self.gamepad.index_player}:np:{self.gamepad.username}\n'.encode('utf-8'))
            print('Iniciou!!')
            Clock.schedule_once(self.gamepad.start_game, 0.5)
        except (ConnectionAbortedError, socket.timeout, TimeoutError):
            sucessfull = False

        if sucessfull:
            values = esp.recv(1024).decode('utf-8').strip("\n").split(":")
            print(values)
            if len(values) < 2:
                sucessfull = False
            elif values[0] == "erro":
                sucessfull = False
            elif values[0] == "start":
                # values[1::] == INDEX, LIFES
                self.gamepad.index_player = values[1]
                self.gamepad.lifes = int(values[2])
        
        self.gamepad.close_connection_esp(esp)
        self.started = False
        
    def size_login(self, box, size):
        w, h = size
        if w <= dp(340):
            box.width = self.width/1.2
        if h >= dp(650):
            box.height = h/1.25
