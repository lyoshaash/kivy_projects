from kivy.app import App
from kivy.lang import Builder

KV = '''
Slider:
    orientation: 'horizontal'
    value_track: True
    value_track_color: 1, 0, 0, 1
'''


class MainApp(App):
    def build(self):
        return Builder.load_string(KV)


MainApp().run()