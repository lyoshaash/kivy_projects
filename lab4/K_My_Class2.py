from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

KV = '''
MyBox:                   # контейнер (пользовательский класс)
    Button:              # кнопка (класс Button)
        text: 'Кнопка 2' # свойство кнопки (надпись на кнопке)
'''


# пользовательский класс MyBox
# на основе базового класса BoxLayout
class MyBox(BoxLayout):
    pass


class MainApp(App):
    def build(self):
        return Builder.load_string(KV)


MainApp().run()