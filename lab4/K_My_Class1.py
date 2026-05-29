from kivy.app import App
from kivy.lang import Builder

KV = '''
BoxLayout:               # контейнер (класс BoxLayout)
    Button:              # кнопка (класс Button)
        text: 'Кнопка 1' # свойство кнопки (надпись)
'''


class MainApp(App):
    def build(self):
        return Builder.load_string(KV)


MainApp().run()