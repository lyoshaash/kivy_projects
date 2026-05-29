# модуль First_App_Kivy.py
import kivy.app  # импорт приложения фреймворка Kivy
import kivy.uix.label  # импорт визуального элемента Label (метка)


class MainApp(kivy.app.App):  # формирование базового класса приложения
    def build(self):  # формирование интерфейса приложения
        return kivy.uix.label.Label(text='Привет от Kivy!')


app = MainApp(title='Первое приложение на Kivy')  # задание имени приложения
app.run()  # запуск приложения
