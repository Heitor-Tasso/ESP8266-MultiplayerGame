
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

Builder.load_string("""

#:import GamePad gamepad.GamePad
#:import Login login.Login

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

