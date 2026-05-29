from kivy.app import App
from kivy.lang import Builder

KV = '''
CheckBox:
'''


class MainApp(App):
    def build(self):
        return Builder.load_string(KV)


MainApp().run()