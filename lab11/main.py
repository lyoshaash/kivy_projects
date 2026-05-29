from collections import Counter
from random import choice

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.metrics import dp
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget


COLORS = [
    (0.92, 0.18, 0.22, 1),   # red
    (0.15, 0.47, 0.95, 1),   # blue
    (0.17, 0.70, 0.34, 1),   # green
    (0.96, 0.74, 0.16, 1),   # yellow
    (0.58, 0.25, 0.82, 1),   # purple
    (1.00, 0.49, 0.15, 1),   # orange
]
COLOR_NAMES = ["красный", "синий", "зелёный", "жёлтый", "фиолетовый", "оранжевый"]
EMPTY_COLOR = (0.20, 0.22, 0.27, 1)
BG_COLOR = (0.08, 0.09, 0.12, 1)
PANEL_COLOR = (0.13, 0.15, 0.20, 1)
TEXT_COLOR = (0.94, 0.95, 0.98, 1)
MAX_ATTEMPTS = 10
CODE_LENGTH = 4


class Dot(Widget):
    dot_color = ListProperty(EMPTY_COLOR)
    border_color = ListProperty((0.62, 0.66, 0.76, 1))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw, dot_color=self.draw, border_color=self.draw)
        self.draw()

    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            size = min(self.width, self.height) * 0.72
            x = self.center_x - size / 2
            y = self.center_y - size / 2
            Color(*self.dot_color)
            Ellipse(pos=(x, y), size=(size, size))
            Color(*self.border_color)
            Line(ellipse=(x, y, size, size), width=dp(1.2))


class FeedbackDot(Dot):
    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            size = min(self.width, self.height) * 0.55
            x = self.center_x - size / 2
            y = self.center_y - size / 2
            Color(*self.dot_color)
            Ellipse(pos=(x, y), size=(size, size))
            Color(*self.border_color)
            Line(ellipse=(x, y, size, size), width=dp(1))


class MastermindGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(12), spacing=dp(10), **kwargs)
        Window.clearcolor = BG_COLOR
        Window.bind(on_key_down=self.on_key_down)

        self.secret = []
        self.current_guess = []
        self.attempt = 0
        self.game_over = False
        self.guess_dots = []
        self.feedback_dots = []
        self.current_dots = []
        self.secret_dots = []

        self.build_interface()
        self.new_game()

    def build_interface(self):
        with self.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_background, size=self.update_background)

        title = Label(
            text="Mastermind",
            font_size=dp(30),
            bold=True,
            color=TEXT_COLOR,
            size_hint_y=None,
            height=dp(42),
        )
        self.add_widget(title)

        self.status = Label(
            text="Угадай секретный код из 4 цветов",
            font_size=dp(17),
            color=TEXT_COLOR,
            size_hint_y=None,
            height=dp(34),
        )
        self.add_widget(self.status)

        secret_box = BoxLayout(size_hint_y=None, height=dp(52), padding=(dp(6), 0), spacing=dp(8))
        secret_box.add_widget(Label(text="Код:", color=TEXT_COLOR, font_size=dp(16), size_hint_x=None, width=dp(70)))
        for _ in range(CODE_LENGTH):
            dot = Dot(dot_color=EMPTY_COLOR)
            self.secret_dots.append(dot)
            secret_box.add_widget(dot)
        self.add_widget(secret_box)

        header = BoxLayout(size_hint_y=None, height=dp(24), spacing=dp(8))
        header.add_widget(Label(text="Ход", color=TEXT_COLOR, size_hint_x=None, width=dp(45)))
        header.add_widget(Label(text="Попытка", color=TEXT_COLOR))
        header.add_widget(Label(text="Подсказки", color=TEXT_COLOR, size_hint_x=None, width=dp(120)))
        self.add_widget(header)

        board = GridLayout(cols=1, spacing=dp(4), size_hint_y=1)
        self.add_widget(board)

        for row_index in range(MAX_ATTEMPTS):
            row = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(38))
            row.add_widget(Label(text=str(row_index + 1), color=TEXT_COLOR, size_hint_x=None, width=dp(45)))

            guess_grid = GridLayout(cols=CODE_LENGTH, spacing=dp(4))
            row_guess_dots = []
            for _ in range(CODE_LENGTH):
                dot = Dot(dot_color=EMPTY_COLOR)
                row_guess_dots.append(dot)
                guess_grid.add_widget(dot)
            self.guess_dots.append(row_guess_dots)
            row.add_widget(guess_grid)

            feedback_grid = GridLayout(cols=CODE_LENGTH, spacing=dp(2), size_hint_x=None, width=dp(120))
            row_feedback_dots = []
            for _ in range(CODE_LENGTH):
                dot = FeedbackDot(dot_color=EMPTY_COLOR)
                row_feedback_dots.append(dot)
                feedback_grid.add_widget(dot)
            self.feedback_dots.append(row_feedback_dots)
            row.add_widget(feedback_grid)
            board.add_widget(row)

        current_box = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8), padding=(dp(6), 0))
        current_box.add_widget(Label(text="Ввод:", color=TEXT_COLOR, font_size=dp(16), size_hint_x=None, width=dp(70)))
        for _ in range(CODE_LENGTH):
            dot = Dot(dot_color=EMPTY_COLOR)
            self.current_dots.append(dot)
            current_box.add_widget(dot)
        self.add_widget(current_box)

        palette = GridLayout(cols=6, spacing=dp(6), size_hint_y=None, height=dp(54))
        for i, color in enumerate(COLORS):
            btn = Button(
                text=str(i + 1),
                font_size=dp(20),
                bold=True,
                background_normal="",
                background_down="",
                background_color=color,
                color=(1, 1, 1, 1),
            )
            btn.bind(on_release=lambda instance, index=i: self.add_color(index))
            palette.add_widget(btn)
        self.add_widget(palette)

        controls = GridLayout(cols=4, spacing=dp(6), size_hint_y=None, height=dp(48))
        controls.add_widget(self.make_button("Проверить", self.submit_guess))
        controls.add_widget(self.make_button("Удалить", self.remove_color))
        controls.add_widget(self.make_button("Очистить", self.clear_current))
        controls.add_widget(self.make_button("Новая", self.new_game))
        self.add_widget(controls)

        help_text = "1–6 — цвета   Enter — проверить   Backspace — удалить   R — новая игра"
        self.help_label = Label(text=help_text, color=(0.72, 0.76, 0.84, 1), font_size=dp(13), size_hint_y=None, height=dp(24))
        self.add_widget(self.help_label)

    def update_background(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def make_button(self, text, callback):
        btn = Button(
            text=text,
            font_size=dp(15),
            background_normal="",
            background_down="",
            background_color=PANEL_COLOR,
            color=TEXT_COLOR,
        )
        btn.bind(on_release=lambda instance: callback())
        return btn

    def new_game(self, *args):
        self.secret = [choice(range(len(COLORS))) for _ in range(CODE_LENGTH)]
        self.current_guess = []
        self.attempt = 0
        self.game_over = False
        self.status.text = "Угадай секретный код из 4 цветов"

        for row in self.guess_dots:
            for dot in row:
                dot.dot_color = EMPTY_COLOR
        for row in self.feedback_dots:
            for dot in row:
                dot.dot_color = EMPTY_COLOR
                dot.border_color = (0.62, 0.66, 0.76, 1)
        for dot in self.secret_dots:
            dot.dot_color = EMPTY_COLOR
        self.update_current_dots()

    def add_color(self, index):
        if self.game_over:
            return
        if len(self.current_guess) < CODE_LENGTH:
            self.current_guess.append(index)
            self.update_current_dots()
        if len(self.current_guess) == CODE_LENGTH:
            self.status.text = "Нажми «Проверить» или Enter"

    def remove_color(self, *args):
        if self.game_over:
            return
        if self.current_guess:
            self.current_guess.pop()
            self.update_current_dots()
            self.status.text = "Цвет удалён"

    def clear_current(self, *args):
        if self.game_over:
            return
        self.current_guess = []
        self.update_current_dots()
        self.status.text = "Текущая попытка очищена"

    def update_current_dots(self):
        for i, dot in enumerate(self.current_dots):
            if i < len(self.current_guess):
                dot.dot_color = COLORS[self.current_guess[i]]
            else:
                dot.dot_color = EMPTY_COLOR

    def submit_guess(self, *args):
        if self.game_over:
            return
        if len(self.current_guess) != CODE_LENGTH:
            self.status.text = "Выбери 4 цвета перед проверкой"
            return

        row = self.attempt
        for i, color_index in enumerate(self.current_guess):
            self.guess_dots[row][i].dot_color = COLORS[color_index]

        black, white = self.get_feedback(self.current_guess, self.secret)
        feedback_colors = [(0.02, 0.02, 0.03, 1)] * black + [(0.96, 0.96, 0.92, 1)] * white
        while len(feedback_colors) < CODE_LENGTH:
            feedback_colors.append(EMPTY_COLOR)

        for dot, color in zip(self.feedback_dots[row], feedback_colors):
            dot.dot_color = color
            dot.border_color = (0.92, 0.92, 0.92, 1) if color != EMPTY_COLOR else (0.62, 0.66, 0.76, 1)

        self.attempt += 1
        guess_text = ", ".join(COLOR_NAMES[i] for i in self.current_guess)

        if black == CODE_LENGTH:
            self.game_over = True
            self.reveal_secret()
            self.status.text = f"Победа! Код угадан за {self.attempt} ход(ов): {guess_text}"
        elif self.attempt >= MAX_ATTEMPTS:
            self.game_over = True
            self.reveal_secret()
            self.status.text = "Ходы закончились. Нажми «Новая», чтобы сыграть ещё раз"
        else:
            self.status.text = f"Чёрные: {black}, белые: {white}. Осталось ходов: {MAX_ATTEMPTS - self.attempt}"

        self.current_guess = []
        self.update_current_dots()

    @staticmethod
    def get_feedback(guess, secret):
        black = sum(1 for g, s in zip(guess, secret) if g == s)
        guess_counter = Counter(guess)
        secret_counter = Counter(secret)
        total_color_matches = sum(min(guess_counter[color], secret_counter[color]) for color in guess_counter)
        white = total_color_matches - black
        return black, white

    def reveal_secret(self):
        for i, color_index in enumerate(self.secret):
            self.secret_dots[i].dot_color = COLORS[color_index]

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if codepoint in {"1", "2", "3", "4", "5", "6"}:
            self.add_color(int(codepoint) - 1)
            return True
        if key == 13:  # Enter
            self.submit_guess()
            return True
        if key == 8:  # Backspace
            self.remove_color()
            return True
        if codepoint and codepoint.lower() == "r":
            self.new_game()
            return True
        return False


class MastermindApp(App):
    def build(self):
        self.title = "Mastermind"
        return MastermindGame()


if __name__ == "__main__":
    MastermindApp().run()
