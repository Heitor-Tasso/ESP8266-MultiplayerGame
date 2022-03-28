
__all__ = ['ButtonEffect', 'ButtonRectangle']

from .behaviors.touch_effecs import EffectBehavior
from .behaviors.button import ButtonBehavior
from kivy.animation import Animation
from kivy.uix.label import Label

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock

from kivy.properties import (
    ListProperty, NumericProperty,
)

Builder.load_string("""

<ButtonEffect>:
    background_color:[1, 1, 1, 0]
    radius: [0, 0, 0, 0]
    canvas.before:
        Color:
            rgba:self.background
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius:self.radius or [0]
    canvas.after:
        Color:
            rgba:self.background_line
        Line:
            rounded_rectangle:(self.pos + self.size + self.radius + [100])
            width:self.width_line

""", filename="buttons.kv")

class ButtonEffect(EffectBehavior, ButtonBehavior, Label):
    #Colors
    background_line = ListProperty([0, 0, 0, 0])
    background = ListProperty([0, 0, 0, 0])
    
    down_color_text = ListProperty([0, 0, 0, 0])
    down_color_line = ListProperty([0, 0, 0, 0])

    background_color = ListProperty([[0.05, 0.0, 0.4, 1], [0.0625, 0.0, 0.5, 1]])
    color_line = ListProperty([[1, 1, 1, 1], [0.8, 0.925, 1, 1]])
    color_text = ListProperty([[1, 1, 1, 1], [0.8, 0.925, 1, 1]])

    duration_back = NumericProperty(0.2)

    #Sizes
    width_line = NumericProperty(1.01)
    _pressed = False

    def __init__(self, **kwargs):
        self.bind(
            background_color=self.set_color,
            color_line=self.set_color,
            color_text=self.set_color)
        super(ButtonEffect, self).__init__(**kwargs)
        self.type_button = 'rounded'
        Window.bind(mouse_pos=self.on_mouse_pos)
        Clock.schedule_once(self.set_color, 1.3)
    
    def set_color(self, *args):
        self.background = self.get_color(self.background_color, 0)
        self.background_line = self.get_color(self.color_line, 0)
        self.color = self.get_color(self.color_text, 0)
    
    def get_color(self, object, index):
        if isinstance(object, (list, tuple)):
            if len(object) == 2 and index > -1 and index < 3:
                return object[index]
        return object


    def set_pressed(self, *args):
        if self.down_color_text[-1] != 0:
            self.color = self.down_color_text
        if self.down_color_line[-1] != 0:
            self.background_line = self.down_color_line

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        elif self in touch.ud:
            return False
        elif not self.collide_point(*self.to_widget(*touch.pos)):
            return False

        Animation.cancel_all(self, 'color', 'background_line')
        self.set_pressed()
        
        touch.grab(self)
        self.ripple_show(touch)
        self._pressed = True
        return super(ButtonEffect, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.ripple_fade()
        
        if not self.collide_point(*self.to_widget(*touch.pos)):
            return False
        
        anim = Animation(
            color=self.get_color(self.color_text, 1),
            background_line=self.get_color(self.color_line, 1),
            t=self.transition_out,
            duration=self.duration_out)
        anim.bind(on_complete=self.on_touch_anim_end)
        anim.start(self)
        
        return super().on_touch_up(touch)


    def on_touch_anim_end(self, *args):
        self._pressed = False

    def on_mouse_pos(self, window, mouse_pos):
        if self.collide_point(*self.to_widget(*mouse_pos)):
            if not self._pressed:
                self.background_line = self.get_color(self.color_line, 1)
                self.color = self.get_color(self.color_text, 1)
            anim = Animation(
                background=self.get_color(self.background_color, 1),
                d=self.duration_back, t='out_quad')
            anim.start(self)
            return None
        
        anim = Animation(
            background=self.get_color(self.background_color, 0),
            d=self.duration_back, t='out_quad')
        anim.start(self)
        if not self._pressed:
            self.color = self.get_color(self.color_text, 0)
            self.background_line = self.get_color(self.color_line, 0)
