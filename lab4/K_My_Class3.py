from kivy.app import App
from kivy.lang import Builder

KV = '''
# пользовательский класс MyBox
# на основе базового класса BoxLayout
<MyBox@BoxLayout>:

MyBox:                   # контейнер (пользовательский класс) 
    Button:              # кнопка (класс Button)
        text: 'Кнопка 3' # свойство кнопки (надпись на кнопке)
'''


class MainApp(App):
    def build(self):
        return Builder.load_string(KV)


MainApp().run()