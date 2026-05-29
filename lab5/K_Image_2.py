# модуль K_Image_2.py
from kivy.app import App
from kivy.lang import Builder

KV = '''
Image:
    source: "./Images/fon.jpg"
'''


class MainApp(App):
    def build(self):
        return Builder.load_string(KV)


MainApp().run()