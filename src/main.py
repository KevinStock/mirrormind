from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen

class DashboardScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class MirrorMindApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

if __name__ == '__main__':
    MirrorMindApp().run()