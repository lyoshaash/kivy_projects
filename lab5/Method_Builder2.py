from kivy.app import App  # импорт класса - приложения
from kivy.lang import Builder  # импорт метода Builder

# создание текстовой строки
my_str = '''
Label:
    text:('Загрузка метки из текстовой строки')
    font_size: '16pt'
'''

# загрузка кода из текстовой строки
kv_str = Builder.load_string(my_str)


class Basic_Class(App):  # определение базового класса
    def build(self):
        return kv_str


My_App = Basic_Class()  # приложение на основе базового класса
My_App.run()  # запуск приложения
