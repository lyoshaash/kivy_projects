import random
from copy import deepcopy

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


SIDE = 9
BOX = 3


class SudokuGenerator:
    """Генератор судоку: создает готовое поле и удаляет часть чисел."""

    @staticmethod
    def pattern(row, col):
        return (BOX * (row % BOX) + row // BOX + col) % SIDE

    @staticmethod
    def shuffled(seq):
        seq = list(seq)
        random.shuffle(seq)
        return seq

    def make_solution(self):
        row_groups = self.shuffled(range(BOX))
        rows = [group * BOX + row for group in row_groups for row in self.shuffled(range(BOX))]

        col_groups = self.shuffled(range(BOX))
        cols = [group * BOX + col for group in col_groups for col in self.shuffled(range(BOX))]

        nums = self.shuffled(range(1, SIDE + 1))
        return [[nums[self.pattern(r, c)] for c in cols] for r in rows]

    def make_puzzle(self, difficulty="Средний"):
        solution = self.make_solution()
        puzzle = deepcopy(solution)

        # Количество открытых клеток: чем меньше подсказок, тем сложнее игра.
        clues_by_level = {
            "Легкий": 42,
            "Средний": 34,
            "Сложный": 28,
        }
        clues = clues_by_level.get(difficulty, 34)
        cells_to_remove = SIDE * SIDE - clues

        cells = [(r, c) for r in range(SIDE) for c in range(SIDE)]
        random.shuffle(cells)

        removed = 0
        for row, col in cells:
            if removed >= cells_to_remove:
                break
            backup = puzzle[row][col]
            puzzle[row][col] = 0
            removed += 1

        return puzzle, solution


class SudokuGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=10, spacing=8, **kwargs)
        Window.clearcolor = (0.08, 0.09, 0.12, 1)
        Window.bind(on_key_down=self.on_key_down)

        self.generator = SudokuGenerator()
        self.difficulties = ["Легкий", "Средний", "Сложный"]
        self.difficulty_index = 1
        self.difficulty = self.difficulties[self.difficulty_index]

        self.puzzle = []
        self.solution = []
        self.current = []
        self.fixed = []
        self.cells = []
        self.selected = None
        self.mistakes = 0

        self.title = Label(
            text="Судоку",
            font_size=32,
            size_hint=(1, 0.09),
            color=(1, 1, 1, 1),
            bold=True,
        )
        self.add_widget(self.title)

        self.status = Label(
            text="Выбери клетку и введи число 1-9",
            font_size=18,
            size_hint=(1, 0.07),
            color=(0.88, 0.9, 1, 1),
        )
        self.add_widget(self.status)

        self.grid = GridLayout(cols=9, rows=9, spacing=1, size_hint=(1, 0.66))
        self.add_widget(self.grid)

        self.number_panel = GridLayout(cols=9, rows=1, spacing=4, size_hint=(1, 0.09))
        for number in range(1, 10):
            btn = Button(
                text=str(number),
                font_size=24,
                bold=True,
                background_normal="",
                background_color=(0.18, 0.32, 0.52, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(on_release=lambda instance, n=number: self.enter_number(n))
            self.number_panel.add_widget(btn)
        self.add_widget(self.number_panel)

        self.control_panel = GridLayout(cols=5, rows=1, spacing=4, size_hint=(1, 0.09))
        controls = [
            ("Очистить", self.clear_cell),
            ("Подсказка", self.give_hint),
            ("Новая", self.new_game),
            ("Сложность", self.change_difficulty),
            ("Проверить", self.check_board),
        ]
        for text, action in controls:
            btn = Button(
                text=text,
                font_size=17,
                background_normal="",
                background_color=(0.28, 0.28, 0.36, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(on_release=lambda instance, fn=action: fn())
            self.control_panel.add_widget(btn)
        self.add_widget(self.control_panel)

        self.new_game()

    def new_game(self, *args):
        self.puzzle, self.solution = self.generator.make_puzzle(self.difficulty)
        self.current = deepcopy(self.puzzle)
        self.fixed = [[self.puzzle[r][c] != 0 for c in range(SIDE)] for r in range(SIDE)]
        self.cells = []
        self.selected = None
        self.mistakes = 0
        self.build_grid()
        self.update_status(f"Новая игра. Сложность: {self.difficulty}")

    def build_grid(self):
        self.grid.clear_widgets()
        self.cells = [[None for _ in range(SIDE)] for _ in range(SIDE)]

        for row in range(SIDE):
            for col in range(SIDE):
                value = self.current[row][col]
                btn = Button(
                    text=str(value) if value else "",
                    font_size=24,
                    bold=self.fixed[row][col],
                    background_normal="",
                    color=(1, 1, 1, 1) if self.fixed[row][col] else (0.07, 0.08, 0.1, 1),
                )
                btn.row = row
                btn.col = col
                btn.bind(on_release=self.select_cell)
                self.cells[row][col] = btn
                self.grid.add_widget(btn)

        self.refresh_colors()

    def select_cell(self, button):
        self.selected = (button.row, button.col)
        if self.fixed[button.row][button.col]:
            self.update_status("Это исходная клетка, её менять нельзя")
        else:
            self.update_status("Введите число 1-9, Backspace — очистить")
        self.refresh_colors()

    def refresh_colors(self):
        for row in range(SIDE):
            for col in range(SIDE):
                btn = self.cells[row][col]
                in_same_area = False
                if self.selected is not None:
                    sr, sc = self.selected
                    in_same_area = (
                        row == sr
                        or col == sc
                        or (row // BOX == sr // BOX and col // BOX == sc // BOX)
                    )

                if self.fixed[row][col]:
                    color = (0.18, 0.22, 0.33, 1)
                elif self.current[row][col] == 0:
                    color = (0.94, 0.94, 0.96, 1)
                elif self.current[row][col] == self.solution[row][col]:
                    color = (0.78, 0.92, 0.78, 1)
                else:
                    color = (0.95, 0.58, 0.58, 1)

                if in_same_area and not self.fixed[row][col]:
                    color = self.lighten(color)

                if self.selected == (row, col):
                    color = (0.98, 0.86, 0.35, 1)

                if row % 3 == 2 and row != 8:
                    # Небольшой визуальный акцент на границах блоков через цвет соседних клеток.
                    pass

                btn.background_color = color

    @staticmethod
    def lighten(color):
        r, g, b, a = color
        return (min(r + 0.08, 1), min(g + 0.08, 1), min(b + 0.08, 1), a)

    def enter_number(self, number):
        if self.selected is None:
            self.update_status("Сначала выбери пустую клетку")
            return

        row, col = self.selected
        if self.fixed[row][col]:
            self.update_status("Исходные числа менять нельзя")
            return

        self.current[row][col] = number
        self.cells[row][col].text = str(number)

        if number == self.solution[row][col]:
            self.update_status("Верно")
        else:
            self.mistakes += 1
            self.update_status(f"Ошибка. Ошибок: {self.mistakes}")

        self.refresh_colors()
        if self.is_completed():
            self.update_status(f"Победа! Судоку решено. Ошибок: {self.mistakes}")

    def clear_cell(self, *args):
        if self.selected is None:
            self.update_status("Сначала выбери клетку")
            return

        row, col = self.selected
        if self.fixed[row][col]:
            self.update_status("Исходные числа очистить нельзя")
            return

        self.current[row][col] = 0
        self.cells[row][col].text = ""
        self.update_status("Клетка очищена")
        self.refresh_colors()

    def give_hint(self, *args):
        if self.selected is None:
            self.update_status("Выбери пустую клетку для подсказки")
            return

        row, col = self.selected
        if self.fixed[row][col]:
            self.update_status("Это уже исходная подсказка")
            return

        value = self.solution[row][col]
        self.current[row][col] = value
        self.cells[row][col].text = str(value)
        self.update_status(f"Подсказка: в этой клетке число {value}")
        self.refresh_colors()
        if self.is_completed():
            self.update_status(f"Победа! Судоку решено. Ошибок: {self.mistakes}")

    def check_board(self, *args):
        wrong = 0
        empty = 0
        for row in range(SIDE):
            for col in range(SIDE):
                if self.current[row][col] == 0:
                    empty += 1
                elif self.current[row][col] != self.solution[row][col]:
                    wrong += 1

        if wrong == 0 and empty == 0:
            self.update_status(f"Победа! Судоку решено. Ошибок: {self.mistakes}")
        elif wrong == 0:
            self.update_status(f"Пока всё правильно. Пустых клеток: {empty}")
        else:
            self.update_status(f"Есть ошибки: {wrong}. Пустых клеток: {empty}")
        self.refresh_colors()

    def change_difficulty(self, *args):
        self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulties)
        self.difficulty = self.difficulties[self.difficulty_index]
        self.new_game()

    def is_completed(self):
        return self.current == self.solution

    def update_status(self, text):
        self.status.text = text
        self.title.text = f"Судоку — {self.difficulty}"

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if codepoint and codepoint in "123456789":
            self.enter_number(int(codepoint))
            return True

        if key in (8, 127):  # Backspace / Delete
            self.clear_cell()
            return True

        if codepoint and codepoint.lower() == "r":
            self.new_game()
            return True

        if codepoint and codepoint.lower() == "h":
            self.give_hint()
            return True

        if codepoint and codepoint.lower() == "c":
            self.check_board()
            return True

        if key in (273, 274, 275, 276):  # arrows: up, down, right, left
            self.move_selection(key)
            return True

        return False

    def move_selection(self, key):
        if self.selected is None:
            self.selected = (0, 0)
        row, col = self.selected
        if key == 273:
            row = (row - 1) % SIDE
        elif key == 274:
            row = (row + 1) % SIDE
        elif key == 275:
            col = (col + 1) % SIDE
        elif key == 276:
            col = (col - 1) % SIDE
        self.selected = (row, col)
        self.refresh_colors()


class SudokuApp(App):
    def build(self):
        self.title = "Судоку"
        Window.size = (620, 760)
        return SudokuGame()


if __name__ == "__main__":
    SudokuApp().run()
