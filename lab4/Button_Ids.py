from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

KV = '''
box:
    Button:
        text: ' Кнопка '
        on_press: root.result('Нажата кнопка')
    Label:
        id: itog
'''


class box(BoxLayout):
    def result(self, entry_text):
        self.ids["itog"].text = entry_text


class MainApp(App):
    def build(self):
        return Builder.load_string(KV)


MainApp().run()