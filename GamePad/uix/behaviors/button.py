
__all__ = ['ButtonBehavior', 'ToggleButtonBehavior', 'FloatBehavior']

from kivy.clock import Clock
from kivy.config import Config
from weakref import ref
from time import time
from kivy.app import App
from kivy.uix.image import Image
from utils import image, icon
from kivy.metrics import dp

from kivy.properties import (
    OptionProperty, ObjectProperty,
    BooleanProperty, NumericProperty,
    ListProperty,
)

from kivy.graphics import Color, Line, Rectangle

class FloatBehavior(object):
    hint_x = NumericProperty(0.5)
    hint_y = NumericProperty(0.5)
    name = ''
    move_layout = False
    selected = False
    resized = False
    root = ObjectProperty(None)
    pad_widget = ObjectProperty(None)
    last_touch_pos = ListProperty([0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.binds)
    
    def binds(self, *args):
        self.bind(hint_x=self.update_pos)
        self.bind(hint_y=self.update_pos)
        self.root = App.get_running_app().root.ids.gamepad
        self.pad_widget = self.root.ids.content_pad
        self.pad_widget.bind(pos=self.update_pos)
        self.pad_widget.bind(size=self.update_pos)
        Clock.schedule_once(self.update_pos)
    
    def update_pos(self, *args):
        if not self.get_root_window():
            return None
        self.x = self.pad_widget.x+(self.pad_widget.width*self.hint_x)
        self.y = self.pad_widget.y+(self.pad_widget.height*self.hint_y)
        if (self.selected or self.resized) and not self.move_layout:
            self.find_equals()
            Clock.schedule_once(self.remove_equals, 2)

    def on_touch_down(self, touch):
        self.last_touch_pos = touch.pos
        if self.collide_point(*touch.pos):
            if self.root.move_layout:
                self.move_layout = True
                if touch.is_double_tap:
                    self.resized = True
                    self.selected = False
                    self.clear_background_selected()
                    self.draw_background_resized()
                else:
                    if self.resized:
                        tx, ty = touch.pos
                        if not (self.precision(tx, self.x+self.width) or self.precision(tx, self.x)) \
                            and not self.precision(ty, self.y+self.height):
                            self.resized = False
                        elif not (self.precision(tx, self.x+self.width) or self.precision(tx, self.x)) \
                            and not self.precision(ty, self.y):
                            self.resized = False
                    
                    if not self.resized:
                        self.selected = True
                        self.clear_background_resized()
                        self.draw_background_selected()
                    
                return False
        else:
            self.selected = False
            self.resized = False
            self.move_layout = False
            self.clear_background_selected()
            self.clear_background_resized()
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.move_layout:
            self.move_layout = False

            json_pos = self.root.get_json(name='position')
            json_pos[self.name]['hint_x'] = self.hint_x
            json_pos[self.name]['hint_y'] = self.hint_y
            json_pos[self.name]['width'] = self.width
            json_pos[self.name]['height'] = self.height
            self.root.update_json(json_pos, name='position')
            Clock.schedule_once(self.root.clear_middle_line, 2)
            Clock.schedule_once(self.remove_equals, 2)

        return super().on_touch_up(touch)

    def on_touch_move(self, touch):
        if self.root.move_layout and self.move_layout:
            tx, ty = touch.pos
            if self.selected:
                self.clear_background_selected()
                s_center = self.x+(self.width/2)
                p_center = self.pad_widget.x+(self.pad_widget.width/2)

                if self.precision(s_center, p_center):
                    if self.precision(tx, p_center, (self.width/2)):
                        tx = (p_center-(self.width/2))
                        self.root.add_middle_line()
                        Clock.unschedule(self.root.clear_middle_line)
                    else:
                        Clock.schedule_once(self.root.clear_middle_line, 1)

                self.hint_x = round(tx/self.pad_widget.width, 2)
                self.hint_y = round(ty/self.pad_widget.height, 2)
                self.find_equals()
                self.draw_background_selected()
                self.last_touch_pos = touch.pos
                return False
            elif self.resized:
                lx, ly = self.last_touch_pos
                vl = ((tx-lx) + (ty-ly)) / 2
                self.size = (round(self.width+vl, 2), round(self.height+vl, 2))
                self.draw_background_resized()
                self.last_touch_pos = touch.pos
                self.find_equals()
                return False
        self.last_touch_pos = touch.pos
        return super().on_touch_move(touch)
    
    def get_floats_config(self, *args):
        json_pos = self.root.get_json(name='position')
        del json_pos[self.name]
        px, py = self.pad_widget.pos
        pw, ph = self.pad_widget.size

        for name, values in json_pos.items():
            x = px+(pw*values['hint_x'])
            y = py+(ph*values['hint_y'])
            w, h = values['width'], values['height']
            center_x, center_y = (x+(w*0.5)), (y+(h*0.5))
            yield (name, x, y, w, h, center_x, center_y)

    def precision(self, n1, n2, marg=dp(5)):
        return (n1 > (n2-marg) and n1 < (n2+marg))

    def find_equals(self, *args):
        sw, sh = self.size
        sx, sy = self.pos
        cx, cy = self.center_x, self.center_y
        for name, x, y, w, h, center_x, center_y in self.get_floats_config():
            
            self.root.remove_line(f'{name}_x')
            if self.precision(x, sx) or self.precision(x, (sx+sw)):
                self.root.add_line(x, f'{name}_x')
            if self.precision(center_x, cx):
                self.root.add_line(center_x, f'{name}_x')
            if self.precision((x+w), sx) or self.precision((x+w), (sx+sw)):
                self.root.add_line((x+w), f'{name}_x')

            self.root.remove_line(f'{name}_y')
            if self.precision(y, sy) or self.precision(y, (sy+sh)):
                self.root.add_line(y, f'{name}_y')
            if self.precision(center_y, cy):
                self.root.add_line(center_y, f'{name}_y')
            if self.precision((y+h), (sy+sh)) or self.precision((y+h), sy):
                self.root.add_line((y+h), f'{name}_y')
    
    def remove_equals(self, *args):
        for name, x, y, w, h, center_x, center_y in self.get_floats_config():
            toph = (self.y+self.height)
            leftw = (self.x+self.width)
            
            if self.precision(x, self.x) or self.precision(center_x, self.center_x):
                self.root.remove_line(f'{name}_x')
            elif self.precision((x+w), leftw) or self.precision((x+w), self.x):
                self.root.remove_line(f'{name}_x')
            
            if self.precision(y, self.y) or self.precision(center_y, self.center_y):
                self.root.remove_line(f'{name}_y')
            elif self.precision((y+h), toph) or self.precision((y+h), self.y):
                self.root.remove_line(f'{name}_y')

    def update_background_selected(self, *args):
        self.clear_background_selected(unbind=False)
        self.draw_background_selected(bind=False)

    def draw_background_selected(self, bind=True, *args):
        add = self.canvas.before.add

        img = Image(size_hint=(None, None), size=(dp(35), dp(35)), source=image('move'))
        add(Color(rgba=[1, 1, 1, 1], group='selected'))
        add(Rectangle(
            pos=(self.x-(img.width*0.5), self.y-(img.height*0.5)),
            size=img.size, texture=img.texture, group='selected'))
        
        add(Color(rgba=[0, 1, 0, 1], group='selected'))
        add(Line(rectangle=[*self.pos, *self.size], group='selected'))
    
        if bind:
            self.bind(size=self.update_background_selected)
            self.bind(pos=self.update_background_selected)

    def clear_background_selected(self, unbind=True, *args):
        self.canvas.before.remove_group('selected')
        if unbind:
            self.unbind(size=self.update_background_selected)
            self.unbind(pos=self.update_background_selected)
    

    def update_background_resized(self, *args):
        self.clear_background_resized(unbind=False)
        self.draw_background_resized(bind=False)

    def draw_background_resized(self, bind=True, *args):
        add = self.canvas.before.add

        img = Image(size_hint=(None, None), size=(dp(20), dp(20)), source=icon('resize'))
        add(Color(rgba=[1, 1, 1, 1], group='resized'))
        add(Rectangle(
            pos=(self.x, self.y),
            size=img.size, texture=img.texture, group='resized'))
        add(Rectangle(
            pos=(self.x, self.y+self.height-img.height),
            size=img.size, texture=img.texture, group='resized'))
        add(Rectangle(
            pos=(self.x+self.width-img.width, self.y+self.height-img.height),
            size=img.size, texture=img.texture, group='resized'))
        add(Rectangle(
            pos=(self.x+self.width-img.width, self.y),
            size=img.size, texture=img.texture, group='resized'))
        
        add(Color(rgba=[1, 0, 0, 1], group='resized'))
        add(Line(rectangle=[*self.pos, *self.size], group='resized'))
    
        if bind:
            self.bind(size=self.update_background_resized)
            self.bind(pos=self.update_background_resized)

    def clear_background_resized(self, unbind=True, *args):
        self.canvas.before.remove_group('resized')
        if unbind:
            self.unbind(size=self.update_background_resized)
            self.unbind(pos=self.update_background_resized)

class ButtonBehavior(object):
    '''
    This `mixin <https://en.wikipedia.org/wiki/Mixin>`_ class provides
    :class:`~kivy.uix.button.Button` behavior. Please see the
    :mod:`button behaviors module <kivy.uix.behaviors.button>` documentation
    for more information.

    :Events:
        `on_press`
            Fired when the button is pressed.
        `on_release`
            Fired when the button is released (i.e. the touch/click that
            pressed the button goes away).

    '''

    state = OptionProperty('normal', options=('normal', 'down'))
    '''The state of the button, must be one of 'normal' or 'down'.
    The state is 'down' only when the button is currently touched/clicked,
    otherwise its 'normal'.

    :attr:`state` is an :class:`~kivy.properties.OptionProperty` and defaults
    to 'normal'.
    '''

    last_touch = ObjectProperty(None)
    '''Contains the last relevant touch received by the Button. This can
    be used in `on_press` or `on_release` in order to know which touch
    dispatched the event.

    .. versionadded:: 1.8.0

    :attr:`last_touch` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to `None`.
    '''

    min_state_time = NumericProperty(0)
    '''The minimum period of time which the widget must remain in the
    `'down'` state.

    .. versionadded:: 1.9.1

    :attr:`min_state_time` is a float and defaults to 0.035. This value is
    taken from :class:`~kivy.config.Config`.
    '''

    always_release = BooleanProperty(False)
    '''This determines whether or not the widget fires an `on_release` event if
    the touch_up is outside the widget.

    .. versionadded:: 1.9.0

    .. versionchanged:: 1.10.0
        The default value is now False.

    :attr:`always_release` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to `False`.
    '''

    def __init__(self, **kwargs):
        self.register_event_type('on_press')
        self.register_event_type('on_release')
        if 'min_state_time' not in kwargs:
            self.min_state_time = float(Config.get('graphics',
                                                   'min_state_time'))
        super(ButtonBehavior, self).__init__(**kwargs)
        self.__state_event = None
        self.__touch_time = None
        self.fbind('state', self.cancel_event)

    def _do_press(self):
        self.state = 'down'

    def _do_release(self, *args):
        self.state = 'normal'

    def cancel_event(self, *args):
        if self.__state_event:
            self.__state_event.cancel()
            self.__state_event = None

    def on_touch_down(self, touch):
        if super(ButtonBehavior, self).on_touch_down(touch):
            return True
        if touch.is_mouse_scrolling:
            return False
        if not self.collide_point(touch.x, touch.y):
            return False
        if self in touch.ud:
            return False
        touch.grab(self)
        touch.ud[self] = True
        self.last_touch = touch
        self.__touch_time = time()
        self._do_press()
        if App._running_app:
            self.dispatch('on_press')
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            return True
        if super(ButtonBehavior, self).on_touch_move(touch):
            return True
        return self in touch.ud

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return super(ButtonBehavior, self).on_touch_up(touch)
        assert(self in touch.ud)
        touch.ungrab(self)
        self.last_touch = touch

        if (not self.always_release and
                not self.collide_point(*touch.pos)):
            self._do_release()
            return

        touchtime = time() - self.__touch_time
        if touchtime < self.min_state_time:
            self.__state_event = Clock.schedule_once(
                self._do_release, self.min_state_time - touchtime)
        else:
            self._do_release()
        if App._running_app:
            self.dispatch('on_release')
        return True

    def on_press(self):
        pass

    def on_release(self):
        pass

    def trigger_action(self, duration=0.1):
        '''Trigger whatever action(s) have been bound to the button by calling
        both the on_press and on_release callbacks.

        This is similar to a quick button press without using any touch events,
        but note that like most kivy code, this is not guaranteed to be safe to
        call from external threads. If needed use
        :class:`Clock <kivy.clock.Clock>` to safely schedule this function and
        the resulting callbacks to be called from the main thread.

        Duration is the length of the press in seconds. Pass 0 if you want
        the action to happen instantly.

        .. versionadded:: 1.8.0
        '''
        self._do_press()
        self.dispatch('on_press')

        def trigger_release(dt):
            self._do_release()
            self.dispatch('on_release')
        if not duration:
            trigger_release(0)
        else:
            Clock.schedule_once(trigger_release, duration)

class ToggleButtonBehavior(ButtonBehavior):
    '''This `mixin <https://en.wikipedia.org/wiki/Mixin>`_ class provides
    :mod:`~kivy.uix.togglebutton` behavior. Please see the
    :mod:`togglebutton behaviors module <kivy.uix.behaviors.togglebutton>`
    documentation for more information.
    .. versionadded:: 1.8.0
    '''

    __groups = {}

    group = ObjectProperty(None, allownone=True)
    '''Group of the button. If `None`, no group will be used (the button will be
    independent). If specified, :attr:`group` must be a hashable object, like
    a string. Only one button in a group can be in a 'down' state.
    :attr:`group` is a :class:`~kivy.properties.ObjectProperty` and defaults to
    `None`.
    '''

    allow_no_selection = BooleanProperty(True)
    '''This specifies whether the widgets in a group allow no selection i.e.
    everything to be deselected.
    .. versionadded:: 1.9.0
    :attr:`allow_no_selection` is a :class:`BooleanProperty` and defaults to
    `True`
    '''

    def __init__(self, **kwargs):
        self._previous_group = None
        super(ToggleButtonBehavior, self).__init__(**kwargs)

    def on_group(self, *largs):
        groups = ToggleButtonBehavior.__groups
        if self._previous_group:
            group = groups[self._previous_group]
            for item in group[:]:
                if item() is self:
                    group.remove(item)
                    break
        group = self._previous_group = self.group
        if group not in groups:
            groups[group] = []
        r = ref(self, ToggleButtonBehavior._clear_groups)
        groups[group].append(r)

    def _release_group(self, current):
        if self.group is None:
            return
        group = self.__groups[self.group]
        for item in group[:]:
            widget = item()
            if widget is None:
                group.remove(item)
            if widget is current:
                continue
            widget.state = 'normal'

    def _do_press(self):
        if (not self.allow_no_selection and
                self.group and self.state == 'down'):
            return

        self._release_group(self)
        self.state = 'normal' if self.state == 'down' else 'down'

    def _do_release(self, *args):
        pass

    @staticmethod
    def _clear_groups(wk):
        # auto flush the element when the weak reference have been deleted
        groups = ToggleButtonBehavior.__groups
        for group in list(groups.values()):
            if wk in group:
                group.remove(wk)
                break

    @staticmethod
    def get_widgets(groupname):
        '''Return a list of the widgets contained in a specific group. If the
        group doesn't exist, an empty list will be returned.
        .. note::
            Always release the result of this method! Holding a reference to
            any of these widgets can prevent them from being garbage collected.
            If in doubt, do::
                l = ToggleButtonBehavior.get_widgets('mygroup')
                # do your job
                del l
        .. warning::
            It's possible that some widgets that you have previously
            deleted are still in the list. The garbage collector might need
            to release other objects before flushing them.
        '''
        groups = ToggleButtonBehavior.__groups
        if groupname not in groups:
            return []
        return [x() for x in groups[groupname] if x()][:]
