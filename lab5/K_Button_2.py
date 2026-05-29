from kivy.app import App
from kivy.lang import Builder

KV = '''
Button:
    text: "Это кнопка"
    font_size: 50  
'''


class MainApp(App):
    def build(self):
        return Builder.load_string(KV)


MainApp().run()