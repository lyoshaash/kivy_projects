from kivy.app import App
from kivy.lang import Builder

KV = '''
BoxLayout:
    orientation: 'vertical'
    Button:
        text: 'Кнопка 1'
        on_press: app.press_button(self.text)
    Label:
        text: app.name
'''


class MainApp(App):
    def build(self):
        return Builder.load_string(KV)

    def press_button(self, instance):
        print('Вы нажали на кнопку!')
        print(instance)


MainApp().run()