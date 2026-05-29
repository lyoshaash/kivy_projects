from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.uix.widget import Widget

Window.size = (760, 620)
Window.minimum_width = 520
Window.minimum_height = 420


LEVELS = [
    [
        "  #####  ",
        "  #   #  ",
        "  #$  #  ",
        "###  $## ",
        "#  $ $ # ",
        "# # ## # ",
        "# # ## ###",
        "#        #",
        "#######@ #",
        "      ####",
        "   ...    ",
    ],
    [
        "########",
        "#  .   #",
        "#  $   #",
        "#  #   #",
        "#  @   #",
        "########",
    ],
    [
        "  #######",
        "###     #",
        "#   #$  #",
        "#   $   #",
        "# ..# @ #",
        "#########",
    ],
]


class SokobanGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level_index = 0
        self.history = []
        self.redo_history = []
        self.moves = 0
        self.pushes = 0
        self.cell = 32
        self.board_x = 0
        self.board_y = 0
        self.load_level(self.level_index)

        self.bind(size=lambda *_: self.draw())
        self.keyboard = Window.request_keyboard(None, self)
        if self.keyboard:
            self.keyboard.bind(on_key_down=self.on_key_down)

    def load_level(self, index):
        self.level_index = index % len(LEVELS)
        rows = LEVELS[self.level_index]
        self.rows = len(rows)
        self.cols = max(len(row) for row in rows)
        self.walls = set()
        self.targets = set()
        self.boxes = set()
        self.player = (0, 0)

        for r, row in enumerate(rows):
            row = row.ljust(self.cols)
            for c, ch in enumerate(row):
                pos = (c, r)
                if ch == "#":
                    self.walls.add(pos)
                elif ch == ".":
                    self.targets.add(pos)
                elif ch == "$":
                    self.boxes.add(pos)
                elif ch == "*":
                    self.targets.add(pos)
                    self.boxes.add(pos)
                elif ch == "@":
                    self.player = pos
                elif ch == "+":
                    self.targets.add(pos)
                    self.player = pos

        self.history = []
        self.redo_history = []
        self.moves = 0
        self.pushes = 0
        self.draw()

    def get_state(self):
        return self.player, set(self.boxes), self.moves, self.pushes

    def set_state(self, state):
        self.player, boxes, self.moves, self.pushes = state
        self.boxes = set(boxes)
        self.draw()

    def is_completed(self):
        return bool(self.targets) and self.targets.issubset(self.boxes)

    def on_key_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        directions = {
            "up": (0, -1),
            "w": (0, -1),
            "down": (0, 1),
            "s": (0, 1),
            "left": (-1, 0),
            "a": (-1, 0),
            "right": (1, 0),
            "d": (1, 0),
        }

        if key in directions and not self.is_completed():
            self.move(*directions[key])
        elif key == "backspace":
            self.undo()
        elif key == "spacebar":
            self.redo()
        elif key == "r":
            self.load_level(self.level_index)
        elif key == "n":
            self.load_level(self.level_index + 1)
        elif key == "p":
            self.load_level(self.level_index - 1)
        return True

    def on_touch_down(self, touch):
        col = int((touch.x - self.board_x) // self.cell)
        row = int(self.rows - 1 - ((touch.y - self.board_y) // self.cell))
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return super().on_touch_down(touch)

        pc, pr = self.player
        dc = col - pc
        dr = row - pr
        if abs(dc) + abs(dr) == 1 and not self.is_completed():
            self.move(dc, dr)
        return True

    def move(self, dc, dr):
        pc, pr = self.player
        next_pos = (pc + dc, pr + dr)
        box_next_pos = (pc + 2 * dc, pr + 2 * dr)

        if next_pos in self.walls:
            return

        if next_pos in self.boxes:
            if box_next_pos in self.walls or box_next_pos in self.boxes:
                return
            self.history.append(self.get_state())
            self.redo_history.clear()
            self.boxes.remove(next_pos)
            self.boxes.add(box_next_pos)
            self.player = next_pos
            self.moves += 1
            self.pushes += 1
        else:
            self.history.append(self.get_state())
            self.redo_history.clear()
            self.player = next_pos
            self.moves += 1

        self.draw()

    def undo(self):
        if not self.history:
            return
        self.redo_history.append(self.get_state())
        self.set_state(self.history.pop())

    def redo(self):
        if not self.redo_history:
            return
        self.history.append(self.get_state())
        self.set_state(self.redo_history.pop())

    def draw_text(self, text, x, y, size=18, color=(1, 1, 1, 1)):
        label = CoreLabel(text=text, font_size=size)
        label.refresh()
        Color(*color)
        Rectangle(texture=label.texture, pos=(x, y), size=label.texture.size)

    def draw_cell(self, color, col, row):
        x = self.board_x + col * self.cell
        y = self.board_y + (self.rows - 1 - row) * self.cell
        Color(*color)
        Rectangle(pos=(x, y), size=(self.cell, self.cell))
        Color(0.10, 0.10, 0.10, 1)
        Line(rectangle=(x, y, self.cell, self.cell), width=1)

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.05, 0.06, 0.07, 1)
            Rectangle(pos=self.pos, size=self.size)

            top_panel = 80
            bottom_panel = 54
            available_w = max(1, self.width - 40)
            available_h = max(1, self.height - top_panel - bottom_panel)
            self.cell = min(available_w / self.cols, available_h / self.rows)
            self.board_x = (self.width - self.cell * self.cols) / 2
            self.board_y = bottom_panel + (available_h - self.cell * self.rows) / 2

            self.draw_text(
                f"Кладовщик / Sokoban   Уровень: {self.level_index + 1}/{len(LEVELS)}   Ходы: {self.moves}   Толчки: {self.pushes}",
                20,
                self.height - 42,
                20,
                (0.95, 0.95, 0.95, 1),
            )
            self.draw_text(
                "Управление: стрелки или WASD, Backspace — отмена, Space — повтор, R — сначала, N/P — уровень",
                20,
                16,
                15,
                (0.78, 0.82, 0.86, 1),
            )

            for row in range(self.rows):
                for col in range(self.cols):
                    pos = (col, row)
                    if pos in self.walls:
                        self.draw_cell((0.24, 0.27, 0.31, 1), col, row)
                    else:
                        self.draw_cell((0.12, 0.14, 0.16, 1), col, row)

                    if pos in self.targets:
                        x = self.board_x + col * self.cell + self.cell * 0.28
                        y = self.board_y + (self.rows - 1 - row) * self.cell + self.cell * 0.28
                        Color(0.30, 0.75, 0.35, 1)
                        Ellipse(pos=(x, y), size=(self.cell * 0.44, self.cell * 0.44))

            for col, row in self.boxes:
                x = self.board_x + col * self.cell + self.cell * 0.12
                y = self.board_y + (self.rows - 1 - row) * self.cell + self.cell * 0.12
                if (col, row) in self.targets:
                    Color(0.95, 0.75, 0.20, 1)
                else:
                    Color(0.68, 0.38, 0.16, 1)
                Rectangle(pos=(x, y), size=(self.cell * 0.76, self.cell * 0.76))
                Color(0.18, 0.10, 0.06, 1)
                Line(rectangle=(x, y, self.cell * 0.76, self.cell * 0.76), width=2)

            pc, pr = self.player
            x = self.board_x + pc * self.cell + self.cell * 0.14
            y = self.board_y + (self.rows - 1 - pr) * self.cell + self.cell * 0.14
            Color(0.25, 0.55, 1.0, 1)
            Ellipse(pos=(x, y), size=(self.cell * 0.72, self.cell * 0.72))
            Color(0.02, 0.08, 0.16, 1)
            Line(ellipse=(x, y, self.cell * 0.72, self.cell * 0.72), width=2)

            if self.is_completed():
                Color(0, 0, 0, 0.72)
                Rectangle(pos=(0, 0), size=self.size)
                self.draw_text("Уровень пройден! Нажми N для следующего уровня", 90, self.height / 2, 28)


class SokobanApp(App):
    title = "Кладовщик"

    def build(self):
        return SokobanGame()


if __name__ == "__main__":
    SokobanApp().run()
