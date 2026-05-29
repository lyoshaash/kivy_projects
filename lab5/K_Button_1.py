from kivy.app import App
from kivy.uix.button import Button


class MainApp(App):
    def build(self):
        btn = Button(text = "Это кнопка", font_size = 50)
        return btn


MainApp().run()