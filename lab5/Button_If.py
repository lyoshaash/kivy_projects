from kivy.app import App
from kivy.lang import Builder

KV = '''
BoxLayout:
    orientation: 'vertical'
    Button:
        id: bt1
        text: 'Кнопка 1'
    Label:
        text: 'Кнопка отпущена' if bt1.state == 'normal' else 'Кнопка нажата'
'''


class MainApp(App):
    def build(self):
        return Builder.load_string(KV)


MainApp().run()