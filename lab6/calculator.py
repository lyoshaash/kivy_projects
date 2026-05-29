from __future__ import annotations

import ast
import operator

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


class SafeCalculator:
    """Небольшой безопасный вычислитель для выражений калькулятора."""

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @classmethod
    def calculate(cls, expression: str) -> float | int:
        tree = ast.parse(expression, mode="eval")
        return cls._eval_node(tree.body)

    @classmethod
    def _eval_node(cls, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in cls.OPERATORS:
            left = cls._eval_node(node.left)
            right = cls._eval_node(node.right)
            return cls.OPERATORS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in cls.OPERATORS:
            value = cls._eval_node(node.operand)
            return cls.OPERATORS[type(node.op)](value)

        raise ValueError("Недопустимое выражение")


class CalculatorApp(App):
    def build(self):
        self.title = "Calculator"
        self.history = []
        self.history_visible = True

        root = BoxLayout(orientation="horizontal", padding=10, spacing=10)

        self.calc_layout = BoxLayout(orientation="vertical", spacing=10, size_hint=(0.7, 1))

        self.input = TextInput(
            multiline=False,
            readonly=True,
            halign="right",
            font_size=40,
            size_hint=(1, 0.2),
        )
        self.calc_layout.add_widget(self.input)

        control_layout = GridLayout(cols=4, spacing=10, size_hint=(1, 0.15))
        for label in ["Del", "C", "M", "="]:
            control_layout.add_widget(
                Button(text=label, font_size=24, on_press=self.on_control_press)
            )
        self.calc_layout.add_widget(control_layout)

        buttons = [
            ["7", "8", "9", "*"],
            ["4", "5", "6", "/"],
            ["1", "2", "3", "+"],
            [".", "0", "00", "-"],
        ]

        button_layout = GridLayout(cols=4, spacing=10, size_hint=(1, 0.65))
        for row in buttons:
            for label in row:
                button_layout.add_widget(
                    Button(text=label, font_size=30, on_press=self.on_button_press)
                )
        self.calc_layout.add_widget(button_layout)

        root.add_widget(self.calc_layout)

        self.history_layout = BoxLayout(orientation="vertical", size_hint=(0.3, 1))
        self.history_scroll = ScrollView()
        self.history_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.history_grid.bind(minimum_height=self.history_grid.setter("height"))
        self.history_scroll.add_widget(self.history_grid)
        self.history_layout.add_widget(self.history_scroll)
        root.add_widget(self.history_layout)

        Window.bind(on_key_down=self.on_key_down)
        return root

    def on_button_press(self, instance):
        self.add_char(instance.text)

    def on_control_press(self, instance):
        if instance.text == "Del":
            self.input.text = self.input.text[:-1]
        elif instance.text == "C":
            self.input.text = ""
        elif instance.text == "M":
            self.toggle_history()
        elif instance.text == "=":
            self.calculate()

    def add_char(self, char):
        if char in "+-*/":
            if not self.input.text:
                if char == "-":
                    self.input.text = char
                return
            if self.input.text[-1] in "+-*/.":
                self.input.text = self.input.text[:-1] + char
            else:
                self.input.text += char
        elif char == ".":
            parts = self._split_by_operations(self.input.text)
            current_number = parts[-1] if parts else ""
            if "." not in current_number:
                self.input.text += char
        else:
            self.input.text += char

    def calculate(self):
        expression = self.input.text
        if not expression:
            return

        try:
            result = SafeCalculator.calculate(expression)
            if isinstance(result, float) and result.is_integer():
                result_text = str(int(result))
            else:
                result_text = str(round(result, 8)).rstrip("0").rstrip(".")

            self.history.append(f"{expression} = {result_text}")
            self.input.text = result_text
            self.update_history()
        except Exception:
            self.input.text = "Ошибка"

    def toggle_history(self):
        if self.history_visible:
            self.history_layout.size_hint_x = 0
            self.history_visible = False
        else:
            self.history_layout.size_hint_x = 0.3
            self.history_visible = True

    def update_history(self):
        self.history_grid.clear_widgets()
        for item in reversed(self.history):
            button = Button(text=item, size_hint_y=None, height=45)
            button.bind(on_press=self.load_history)
            self.history_grid.add_widget(button)

    def load_history(self, instance):
        expression = instance.text.split("=")[0].strip()
        self.input.text = expression

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if codepoint in "0123456789.+-*/":
            self.add_char(codepoint)
        elif key == 8:  # Backspace
            self.input.text = self.input.text[:-1]
        elif key == 13:  # Enter
            self.calculate()
        elif codepoint and codepoint.lower() == "m":
            self.toggle_history()
        elif codepoint and codepoint.lower() == "c":
            self.input.text = ""

        numpad_digits = {
            256: "0", 257: "1", 258: "2", 259: "3", 260: "4",
            261: "5", 262: "6", 263: "7", 264: "8", 265: "9",
        }
        numpad_operations = {
            266: ".", 267: "/", 268: "*", 269: "-", 270: "+",
        }

        if key in numpad_digits:
            self.add_char(numpad_digits[key])
        elif key in numpad_operations:
            self.add_char(numpad_operations[key])

    @staticmethod
    def _split_by_operations(text):
        for operation in "+-*/":
            text = text.replace(operation, " ")
        return text.split()


if __name__ == "__main__":
    CalculatorApp().run()
