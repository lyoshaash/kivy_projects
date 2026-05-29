from kivy.app import App  # импорт класса - приложения
from kivy.lang import Builder  # импорт метода Builder

# загрузка кода из KV файла
kv_file = Builder.load_file('./basic_class.kv')


class Basic_Class(App):  # определение базового класса
    def build(self):
        return kv_file


My_App = Basic_Class()  # приложение на основе базового класса
My_App.run()  # запуск приложения
