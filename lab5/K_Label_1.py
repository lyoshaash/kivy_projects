from kivy.app import App
from kivy.uix.label import Label


class MainApp(App):
    def build(self):
        L = Label(text = "Это текст", font_size = 50)
        return L


MainApp().run()