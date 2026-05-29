from random import choice, randint

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.label import Label

Window.size = (520, 760)
Window.clearcolor = (0.03, 0.06, 0.16, 1)

COLS = 10
ROWS = 20
CELL = 30
BOARD_X = 70
BOARD_Y = 80
DOOR_Y = 8

SHAPES = [
    # I
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    # O
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    # T
    [(0, 0), (1, 0), (2, 0), (1, 1)],
    # L
    [(0, 0), (0, 1), (0, 2), (1, 0)],
    # J
    [(1, 0), (1, 1), (1, 2), (0, 0)],
    # S
    [(1, 0), (2, 0), (0, 1), (1, 1)],
    # Z
    [(0, 0), (1, 0), (1, 1), (2, 1)],
]

COLORS = [
    (0.65, 0.65, 0.65, 1),
    (0.75, 0.45, 0.25, 1),
    (0.45, 0.45, 0.50, 1),
    (0.55, 0.35, 0.18, 1),
    (0.40, 0.40, 0.42, 1),
]


class TetrillerGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        self.highscore = 0
        self.lives = 3
        self.level = 1
        self.message = "Проведи человечка к зеленой двери"
        self.paused = False
        self.game_over = False
        self.hero_timer = 0
        self.fall_timer = 0
        self.info = Label(
            text="",
            font_size=18,
            color=(1, 1, 1, 1),
            pos=(20, 690),
            size=(480, 40),
        )
        self.help = Label(
            text="←/→ - двигать фигуру   ↑ - поворот   ↓ - быстрее   Space - сброс   P - пауза   R - заново",
            font_size=13,
            color=(0.90, 0.90, 0.95, 1),
            pos=(20, 20),
            size=(480, 30),
        )
        self.add_widget(self.info)
        self.add_widget(self.help)
        Window.bind(on_key_down=self.on_key_down)
        self.reset_game()
        Clock.schedule_interval(self.update, 1 / 60)

    def reset_game(self):
        self.board = {}
        self.hero_x = COLS // 2
        self.hero_dir = 1
        self.hero_h = 2
        self.game_over = False
        self.paused = False
        self.message = "Построй лестницу к двери на 9-й клетке"
        self.spawn_piece()
        self.update_hero_position()
        self.draw()

    def new_round(self):
        self.board = {}
        self.hero_x = COLS // 2
        self.hero_dir = choice([-1, 1])
        self.hero_h = 2
        self.level += 1
        self.score += 1000
        self.highscore = max(self.highscore, self.score)
        self.message = "Побег! Стакан очищен. Новый раунд"
        self.spawn_piece()
        self.update_hero_position()

    def lose_life(self, text="Человечка раздавило"):
        self.lives -= 1
        self.highscore = max(self.highscore, self.score)
        if self.lives <= 0:
            self.game_over = True
            self.message = f"Игра окончена. Счет: {self.score}. Рекорд: {self.highscore}. R - заново"
            return
        self.message = f"{text}. Осталось жизней: {self.lives}"
        self.board = {}
        self.hero_x = COLS // 2
        self.hero_dir = choice([-1, 1])
        self.hero_h = 2
        self.spawn_piece()
        self.update_hero_position()

    def spawn_piece(self):
        shape = choice(SHAPES)
        self.piece = {
            "cells": shape[:],
            "x": COLS // 2 - 2,
            "y": ROWS - 2,
            "color": choice(COLORS),
        }
        if self.piece_hits(self.piece["x"], self.piece["y"], self.piece["cells"]):
            self.lose_life("Стакан заполнен")

    def rotate_piece(self):
        if self.game_over or self.paused:
            return
        old = self.piece["cells"]
        rotated = [(y, -x) for x, y in old]
        min_x = min(x for x, y in rotated)
        min_y = min(y for x, y in rotated)
        rotated = [(x - min_x, y - min_y) for x, y in rotated]
        if not self.piece_hits(self.piece["x"], self.piece["y"], rotated):
            self.piece["cells"] = rotated

    def move_piece(self, dx, dy):
        if self.game_over or self.paused:
            return False
        nx = self.piece["x"] + dx
        ny = self.piece["y"] + dy
        if not self.piece_hits(nx, ny, self.piece["cells"]):
            self.piece["x"] = nx
            self.piece["y"] = ny
            return True
        if dy < 0:
            self.lock_piece()
        return False

    def drop_piece(self):
        if self.game_over or self.paused:
            return
        while self.move_piece(0, -1):
            pass

    def piece_hits(self, x0, y0, cells):
        for x, y in cells:
            x += x0
            y += y0
            if x < 0 or x >= COLS or y < 0:
                return True
            if y >= ROWS:
                continue
            if (x, y) in self.board:
                return True
        return False

    def lock_piece(self):
        for x, y in self.piece["cells"]:
            bx = self.piece["x"] + x
            by = self.piece["y"] + y
            if 0 <= bx < COLS and 0 <= by < ROWS:
                self.board[(bx, by)] = self.piece["color"]
        self.clear_lines()
        self.update_hero_position()
        if self.check_hero_crushed():
            self.lose_life()
        else:
            self.spawn_piece()

    def clear_lines(self):
        full = [y for y in range(ROWS) if all((x, y) in self.board for x in range(COLS))]
        if not full:
            return
        for y in full:
            for x in range(COLS):
                self.board.pop((x, y), None)
        shift = 0
        new_board = {}
        for y in range(ROWS):
            if y in full:
                shift += 1
            else:
                for x in range(COLS):
                    if (x, y) in self.board:
                        new_board[(x, y - shift)] = self.board[(x, y)]
        self.board = new_board
        self.score += len(full) * 150
        self.highscore = max(self.highscore, self.score)
        self.message = f"Очищено линий: {len(full)}"

    def column_floor(self, x):
        ys = [y for (bx, y) in self.board if bx == x]
        if not ys:
            return 0
        return max(ys) + 1

    def first_block_above(self, x, bottom):
        ys = [y for (bx, y) in self.board if bx == x and y >= bottom]
        return min(ys) if ys else ROWS + 10

    def update_hero_position(self):
        self.hero_y = self.column_floor(self.hero_x)
        block = self.first_block_above(self.hero_x, self.hero_y)
        clearance = block - self.hero_y
        if clearance <= 0:
            self.hero_h = 0
        elif clearance == 1:
            self.hero_h = 1
        else:
            self.hero_h = 2

    def check_hero_crushed(self):
        self.update_hero_position()
        return self.hero_h <= 0 or self.hero_y >= ROWS - 1

    def move_hero(self):
        if self.game_over or self.paused:
            return
        self.update_hero_position()
        if self.check_hero_crushed():
            self.lose_life()
            return
        nx = self.hero_x + self.hero_dir
        if nx < 0 or nx >= COLS:
            if self.hero_y in (DOOR_Y, DOOR_Y + 1):
                self.new_round()
                return
            self.hero_dir *= -1
            return
        next_y = self.column_floor(nx)
        if abs(next_y - self.hero_y) <= 1:
            block = self.first_block_above(nx, next_y)
            if block - next_y >= 1:
                self.hero_x = nx
                self.hero_y = next_y
                self.update_hero_position()
            else:
                self.hero_dir *= -1
        else:
            self.hero_dir *= -1

    def update(self, dt):
        if not self.game_over and not self.paused:
            self.fall_timer += dt
            self.hero_timer += dt
            fall_speed = max(0.18, 0.62 - self.level * 0.04)
            if self.fall_timer >= fall_speed:
                self.fall_timer = 0
                self.move_piece(0, -1)
            if self.hero_timer >= 0.45:
                self.hero_timer = 0
                self.move_hero()
        self.draw()

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if codepoint in ("r", "R"):
            self.score = 0
            self.lives = 3
            self.level = 1
            self.reset_game()
            return True
        if self.game_over:
            return True
        if codepoint in ("p", "P"):
            self.paused = not self.paused
            self.message = "Пауза" if self.paused else "Игра продолжается"
            return True
        if key == 276:
            self.move_piece(-1, 0)
        elif key == 275:
            self.move_piece(1, 0)
        elif key == 273:
            self.rotate_piece()
        elif key == 274:
            self.move_piece(0, -1)
        elif key == 32:
            self.drop_piece()
        return True

    def cell_rect(self, x, y):
        return BOARD_X + x * CELL, BOARD_Y + y * CELL, CELL, CELL

    def draw_cell(self, x, y, color):
        px, py, w, h = self.cell_rect(x, y)
        Color(*color)
        Rectangle(pos=(px + 1, py + 1), size=(w - 2, h - 2))
        Color(0.08, 0.08, 0.09, 1)
        Line(rectangle=(px + 1, py + 1, w - 2, h - 2), width=1)

    def draw_cloud(self, x, y, s):
        Color(0.80, 0.86, 0.95, 0.55)
        Ellipse(pos=(x, y), size=(s, s * 0.55))
        Ellipse(pos=(x + s * 0.35, y + s * 0.12), size=(s * 0.8, s * 0.50))
        Ellipse(pos=(x + s * 0.75, y), size=(s, s * 0.55))

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.03, 0.06, 0.16, 1)
            Rectangle(pos=(0, 0), size=self.size)

            self.draw_cloud(25, 610, 75)
            self.draw_cloud(360, 640, 65)
            self.draw_cloud(260, 580, 50)

            Color(0.04, 0.04, 0.06, 1)
            Rectangle(pos=(BOARD_X, BOARD_Y), size=(COLS * CELL, ROWS * CELL))

            # doors at the ninth cell from the bottom
            Color(0.1, 0.9, 0.35, 1)
            Rectangle(pos=(BOARD_X - 18, BOARD_Y + DOOR_Y * CELL), size=(16, CELL * 2))
            Rectangle(pos=(BOARD_X + COLS * CELL + 2, BOARD_Y + DOOR_Y * CELL), size=(16, CELL * 2))

            Color(0.16, 0.18, 0.26, 1)
            for x in range(COLS + 1):
                Line(points=[BOARD_X + x * CELL, BOARD_Y, BOARD_X + x * CELL, BOARD_Y + ROWS * CELL], width=1)
            for y in range(ROWS + 1):
                Line(points=[BOARD_X, BOARD_Y + y * CELL, BOARD_X + COLS * CELL, BOARD_Y + y * CELL], width=1)

            for (x, y), color in self.board.items():
                self.draw_cell(x, y, color)

            if not self.game_over:
                for x, y in self.piece["cells"]:
                    px = self.piece["x"] + x
                    py = self.piece["y"] + y
                    if 0 <= py < ROWS:
                        self.draw_cell(px, py, self.piece["color"])

            # hero: very simple graphics, one or two cells high
            hx, hy, _, _ = self.cell_rect(self.hero_x, self.hero_y)
            Color(1.0, 0.82, 0.20, 1)
            Rectangle(pos=(hx + 7, hy + 2), size=(CELL - 14, CELL * self.hero_h - 4))
            Color(0.05, 0.05, 0.05, 1)
            Ellipse(pos=(hx + 10, hy + CELL * self.hero_h - 13), size=(10, 10))

            Color(0.7, 0.9, 1, 1)
            Line(rectangle=(BOARD_X, BOARD_Y, COLS * CELL, ROWS * CELL), width=2)

        status = f"Tetriller   Счет: {self.score}   Рекорд: {self.highscore}   Жизни: {self.lives}   Уровень: {self.level}\n{self.message}"
        self.info.text = status


class TetrillerApp(App):
    def build(self):
        self.title = "Tetriller"
        return TetrillerGame()


if __name__ == "__main__":
    TetrillerApp().run()
