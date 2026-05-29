from kivy.app import App
from kivy.lang import Builder

KV = '''
<MyButton@Button>:
    font_size: '25sp'
    pos_hint: {'center_x': .5, 'center_y': .6}
    markup: True
    
BoxLayout:
    orientation: "vertical"
    MyButton:
        text: " Кнопка 1"
    MyButton:
        text: " Кнопка 2"
    MyButton:
        text: " Кнопка 3"
'''


class MainApp(App):
    def build(self):
        return Builder.load_string(KV)


MainApp().run()