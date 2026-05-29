# модуль First_App_Kivy2.py
from kivy.app import App  # импорт приложения фреймворка Kivy
from kivy.uix.label import Label  # импорт элемента Label (метка)


class MainApp(App):  # формирование базового класса приложения
    def build(self):  # формирование интерфейса приложения
        self.title = 'Приложение на Kivy'  # имя приложения
        self.icon = './pyt.ico'  # иконка приложения
        label = Label(text='Привет от Kivy и Python!')  # значение метки
        return label  # возврат виджета приложению


if __name__ == '__main__':  # условие вызова приложения
    app = MainApp()  # создание приложения
    app.run()  # запуск приложения
