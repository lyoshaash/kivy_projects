from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

KV = '''
box:
    #корневой виджет
    id: root_widget
    orientation: 'vertical'

    #поле для ввода исходных данных
    TextInput:
        id: entry
        font_size: 32
        multiline: False

    #кнопка для выполнения расчета
    Button:
        text: ' = '
        font_size: 64
        #on_press: root.result(entry.text)
        on_press: root_widget.result(entry.text)

    #поле для показа результатов расчета
    Label:
        id: itog
        text: 'Итого' 
        font_size: 64   
'''


# класс, задающий корневой виджет
class box(BoxLayout):
    # Функция подсчета результата
    def result(self, entry_text):
        if entry_text:
            try:
                # Формула для расчета результатов
                result = str(eval(entry_text))
                self.ids["itog"].text = result
            except Exception:
                # если введено не число
                self.ids["itog"].text = "Ошибка"


# базовый класс приложения
class MainApp(App):
    def build(self):
        return Builder.load_string(KV)


MainApp().run()