
__all__ = ['AnchorIcon', 'Icon', 'ButtonIcon', 'ToggleButtonIcon']

from kivy.graphics import Color, Rectangle
from .behaviors.button import ButtonBehavior, ToggleButtonBehavior, FloatBehavior
from .behaviors.touch_effecs import EffectBehavior

from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.properties import (
    ListProperty, StringProperty,
)

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from utils import icon

Builder.load_string('''

<AnchorIcon>:
    size_hint_x:None
    width:'70dp'
    radius: [0, 0, 0, 0]
    background_color: [0, 0, 0, 0]
    anchor_x:'center'
    anchor_y:'center'
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius: self.radius or [0]

<Icon>:
    anchor_y: 'center'
    anchor_x: 'center'
    source: ''
    icon_size: '30dp', '30dp'
    color: [1, 1, 1, 1]
    BoxLayout:
        padding: ('5dp', '5dp', '5dp', '5dp')
        size_hint: None, None
        size:root.icon_size
        Image:
            source:root.source
            allow_stretch:True
            keep_ratio:False
            mipmap:True
            color:root.color

<ButtonIcon>:
    color_icon:[1, 1, 1, 1]
    size_hint:None, None
    size:'40dp', '40dp'
    mipmap:True
    allow_strech:True
    keep_ratio:False
    canvas:
        Clear
    canvas.after:
        Color:
            rgba:self.color_icon
        Rectangle:
            texture:self.texture
            pos:self.pos
            size:self.size

<ToggleButtonIcon>:
    size:'30dp', '30dp'

<FloatButtonIcon>:
    size:'100dp', '100dp'

<FloatToggleButtonIcon>:
    size:'100dp', '100dp'

<FloatLifes>:
    size_hint:None, None
    size:'100dp', '30dp'

''', filename="icons.kv")

class AnchorIcon(AnchorLayout):
    background_color = ListProperty([0, 0, 0, 0])
    radius = ListProperty([0, 0, 0, 0])

class Icon(AnchorLayout):
    pass

class ButtonIcon(EffectBehavior, ButtonBehavior, Image):
    # Internal use
    color_icon = ListProperty([1, 1, 1, 1])
    enter_pos = False

    # Properties
    icon_color = ListProperty([1, 1, 1, 1])
    pos_color = ListProperty([-1, -1, -1, -1])
    pos_source = StringProperty('')
    icon_source = StringProperty('')
    state_sources = ListProperty(['', ''])
    
    def __init__(self, **kwargs):
        self.register_event_type('on_mouse_inside')
        self.register_event_type('on_mouse_outside')
        super(ButtonIcon, self).__init__(**kwargs)
        self.type_button = 'rounded'
        Window.bind(mouse_pos=self.on_mouse_pos)
        Clock.schedule_once(self.set_color)
    
    def set_color(self, *args):
        if self.icon_source != '':
            self.source = self.icon_source
        elif len(self.state_sources) > 0:
            self.source = self.state_sources[0]
        self.color_icon = self.icon_color

    def on_state(self, widget, state):
        if self.state_sources != ['', '']:
            if state == 'normal':
                self.source = self.state_sources[0]
            elif state == 'down':
                self.source = self.state_sources[1]

    def on_mouse_pos(self, window, mouse_pos):
        if self.collide_point(*self.to_widget(*mouse_pos)):
            self.enter_pos = True
            self.dispatch('on_mouse_inside')

            if self.pos_source != '':
                self.source = self.pos_source
            if self.pos_color != [-1, -1, -1, -1]:
                self.color_icon = self.pos_color
            return None

        if self.icon_source != '':
            self.source = self.icon_source

        self.color_icon = self.icon_color
        if self.enter_pos:
            self.enter_pos = False
            self.dispatch('on_mouse_outside')

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        elif self in touch.ud:
            return False
        elif not self.collide_point(*self.to_widget(*touch.pos)):
            return False
        
        touch.grab(self)
        self.ripple_show(touch)
        super(ButtonIcon, self).on_touch_down(touch)
        return False

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.ripple_fade()
        
        if not self.collide_point(*self.to_widget(*touch.pos)):
            return False

        return super(ButtonIcon, self).on_touch_up(touch)
    
    def on_mouse_inside(self):
        pass
    def on_mouse_outside(self):
        pass

class ToggleButtonIcon(ToggleButtonBehavior, ButtonIcon):
    pass

class FloatButtonIcon(FloatBehavior, ButtonIcon):
    pass

class FloatToggleButtonIcon(FloatBehavior, ToggleButtonIcon):
    pass

class FloatLifes(FloatBehavior, BoxLayout):
    life_size = ListProperty([dp(25), dp(25)])
    lifes = 5
    img = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.img = Image(size_hint=(None, None), size=self.life_size, source=icon('life'))
        self.show_lifes(self.lifes)

    def update_back_lifes(self, *args):
        self.clear_lifes(unbind=False)
        self.show_lifes(self.lifes, bind=False)

    def show_lifes(self, life, bind=True, *args):
        self.lifes = life
        add = self.canvas.add
        space = dp(5)
        x = self.x
        y = self.center_y - (self.life_size[0]/2)
        add(Color(rgba=[1, 1, 1, 1], group='lifes'))
        for _ in range(life):
            add(Rectangle(
                pos=(x, y), size=self.img.size,
                texture=self.img.texture, group='lifes'))
            x += self.life_size[0] + space

        if bind:
            self.bind(size=self.update_back_lifes)
            self.bind(pos=self.update_back_lifes)

    def clear_lifes(self, unbind=True, *args):
        self.canvas.remove_group('lifes')
        if unbind:
            self.unbind(size=self.update_back_lifes)
            self.unbind(pos=self.update_back_lifes)
