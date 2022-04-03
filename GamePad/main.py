
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from gamepad import GamePad
from login import Login

Builder.load_string("""

#:import hex kivy.utils.get_color_from_hex

# PALLET 1
#:set super_gray hex('#0D0D0D')
#:set black_gray hex('#1A1A1A')
#:set mid_gray hex('#262626')
#:set gray hex('#333333')
#:set light_gray hex('#404040')

# PALLET 2
#:set black hex('#000000')
#:set green hex('#6FEE5D')
#:set clear_white hex('#F6F6F6')
#:set white hex('#FFFFFF')
#:set blue hex('#0064CE')

<GameScreens>:
    Login:
        id:login
        name:'login'
        gamepad:gamepad
    GamePad:
        id:gamepad
        name:'gamepad'
""")

class GameScreens(ScreenManager):
    pass

class Program(App):
    def build(self):
        return GameScreens()
    
    def on_stop(self):
        gamepad = self.root.ids.gamepad
        if gamepad.username:
            gamepad.exit_game()
        return super().on_stop()

if __name__ == '__main__':
    Program().run()
