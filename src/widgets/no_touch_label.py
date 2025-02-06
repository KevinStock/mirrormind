from kivy.uix.label import Label

class NonTouchLabel(Label):
    def on_touch_down(self, touch):
        return False

    def on_touch_up(self, touch):
        return False