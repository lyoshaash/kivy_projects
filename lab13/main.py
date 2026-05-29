import math
import os
import random
import struct
import tempfile
import wave

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.widget import Widget

Window.size = (520, 720)
Window.clearcolor = (0.04, 0.05, 0.09, 1)

COLS = 10
ROWS = 20

PIECES = {
    "I": [(0, 1), (1, 1), (2, 1), (3, 1)],
    "O": [(1, 0), (2, 0), (1, 1), (2, 1)],
    "T": [(1, 0), (0, 1), (1, 1), (2, 1)],
    "S": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
    "J": [(0, 0), (0, 1), (1, 1), (2, 1)],
    "L": [(2, 0), (0, 1), (1, 1), (2, 1)],
}

COLORS = {
    "I": (0.00, 0.85, 1.00, 1),
    "O": (1.00, 0.88, 0.10, 1),
    "T": (0.70, 0.20, 0.95, 1),
    "S": (0.10, 0.85, 0.25, 1),
    "Z": (0.95, 0.10, 0.15, 1),
    "J": (0.15, 0.35, 0.95, 1),
    "L": (1.00, 0.55, 0.05, 1),
}

SCORE_FOR_LINES = {1: 100, 2: 300, 3: 500, 4: 800}


class TetrisGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keyboard = Window.request_keyboard(self._keyboard_closed, self)
        if self.keyboard:
            self.keyboard.bind(on_key_down=self._on_key_down)

        self.music = None
        self.music_muted = False
        self.generated_music_path = None
        self.start_music()

        self.board = []
        self.current = None
        self.next_piece = None
        self.score = 0
        self.high_score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.fall_timer = 0
        self.new_game()

        Clock.schedule_interval(self.update, 1 / 60)

    def start_music(self):
        path = self.find_music_file()
        if path is None:
            path = self.make_generated_music()
        if path:
            self.music = SoundLoader.load(path)
            if self.music:
                self.music.loop = True
                self.music.volume = 0.35
                self.music.play()

    def find_music_file(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for name in ("music.mp3", "music.ogg", "music.wav"):
            path = os.path.join(base_dir, name)
            if os.path.exists(path):
                return path
        return None

    def make_generated_music(self):
        try:
            sample_rate = 22050
            duration = 28
            path = os.path.join(tempfile.gettempdir(), "kivy_tetris_background.wav")
            if os.path.exists(path):
                return path

            melody = [
                (659, 0.20), (494, 0.10), (523, 0.10), (587, 0.20),
                (523, 0.10), (494, 0.10), (440, 0.20), (440, 0.10),
                (523, 0.10), (659, 0.20), (587, 0.10), (523, 0.10),
                (494, 0.30), (523, 0.10), (587, 0.20), (659, 0.20),
                (523, 0.20), (440, 0.20), (440, 0.20), (0, 0.15),
            ]

            frames = []
            elapsed = 0.0
            index = 0
            while elapsed < duration:
                freq, note_len = melody[index % len(melody)]
                total = int(sample_rate * note_len)
                for i in range(total):
                    t = i / sample_rate
                    if freq == 0:
                        value = 0
                    else:
                        main = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
                        bass_freq = freq / 2
                        bass = 1.0 if math.sin(2 * math.pi * bass_freq * t) >= 0 else -1.0
                        envelope = min(1.0, i / max(1, int(sample_rate * 0.02)))
                        release_start = int(total * 0.82)
                        if i > release_start:
                            envelope *= max(0.0, 1 - (i - release_start) / max(1, total - release_start))
                        value = int((main * 0.22 + bass * 0.08) * envelope * 32767)
                    frames.append(struct.pack("<h", value))
                elapsed += note_len
                index += 1

            with wave.open(path, "wb") as file:
                file.setnchannels(1)
                file.setsampwidth(2)
                file.setframerate(sample_rate)
                file.writeframes(b"".join(frames))
            self.generated_music_path = path
            return path
        except Exception:
            return None

    def new_game(self):
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.fall_timer = 0
        self.next_piece = self.random_piece_name()
        self.spawn_piece()
        self.redraw()

    def random_piece_name(self):
        return random.choice(list(PIECES.keys()))

    def spawn_piece(self):
        name = self.next_piece or self.random_piece_name()
        self.next_piece = self.random_piece_name()
        self.current = {
            "name": name,
            "blocks": list(PIECES[name]),
            "x": 3,
            "y": ROWS - 2,
            "color": COLORS[name],
        }
        if self.collides(self.current["blocks"], self.current["x"], self.current["y"]):
            self.game_over = True
            self.high_score = max(self.high_score, self.score)

    def fall_interval(self):
        return max(0.08, 0.55 - (self.level - 1) * 0.045)

    def update(self, dt):
        if self.game_over or self.paused:
            return
        self.fall_timer += dt
        if self.fall_timer >= self.fall_interval():
            self.fall_timer = 0
            self.soft_drop(count_score=False)
        self.redraw()

    def collides(self, blocks, x, y):
        for bx, by in blocks:
            px = x + bx
            py = y + by
            if px < 0 or px >= COLS or py < 0 or py >= ROWS:
                return True
            if self.board[py][px] is not None:
                return True
        return False

    def move(self, dx, dy):
        if self.game_over or self.paused:
            return False
        nx = self.current["x"] + dx
        ny = self.current["y"] + dy
        if not self.collides(self.current["blocks"], nx, ny):
            self.current["x"] = nx
            self.current["y"] = ny
            self.redraw()
            return True
        return False

    def soft_drop(self, count_score=True):
        if self.move(0, -1):
            if count_score:
                self.score += 1
            return True
        self.lock_piece()
        return False

    def hard_drop(self):
        if self.game_over or self.paused:
            return
        dropped = 0
        while self.move(0, -1):
            dropped += 1
        self.score += dropped * 2
        self.lock_piece()
        self.redraw()

    def rotate_piece(self):
        if self.game_over or self.paused:
            return
        if self.current["name"] == "O":
            return
        blocks = self.current["blocks"]
        rotated = [(y, -x) for x, y in blocks]
        min_x = min(x for x, _ in rotated)
        min_y = min(y for _, y in rotated)
        rotated = [(x - min_x, y - min_y) for x, y in rotated]

        for shift in (0, -1, 1, -2, 2):
            if not self.collides(rotated, self.current["x"] + shift, self.current["y"]):
                self.current["blocks"] = rotated
                self.current["x"] += shift
                self.redraw()
                return

    def lock_piece(self):
        if self.game_over:
            return
        for bx, by in self.current["blocks"]:
            px = self.current["x"] + bx
            py = self.current["y"] + by
            if 0 <= px < COLS and 0 <= py < ROWS:
                self.board[py][px] = self.current["color"]
        cleared = self.clear_lines()
        if cleared:
            self.lines += cleared
            self.score += SCORE_FOR_LINES.get(cleared, cleared * 200) * self.level
            self.level = self.lines // 10 + 1
        self.high_score = max(self.high_score, self.score)
        self.spawn_piece()

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell is None for cell in row)]
        cleared = ROWS - len(new_board)
        for _ in range(cleared):
            new_board.append([None for _ in range(COLS)])
        self.board = new_board
        return cleared

    def toggle_pause(self):
        if not self.game_over:
            self.paused = not self.paused
            self.redraw()

    def toggle_music(self):
        self.music_muted = not self.music_muted
        if self.music:
            self.music.volume = 0 if self.music_muted else 0.35
        self.redraw()

    def _keyboard_closed(self):
        if self.keyboard:
            self.keyboard.unbind(on_key_down=self._on_key_down)
            self.keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        if key in ("left", "a"):
            self.move(-1, 0)
        elif key in ("right", "d"):
            self.move(1, 0)
        elif key in ("down", "s"):
            self.soft_drop()
        elif key in ("up", "w"):
            self.rotate_piece()
        elif key == "spacebar":
            if self.game_over:
                self.new_game()
            else:
                self.hard_drop()
        elif key == "p":
            self.toggle_pause()
        elif key == "m":
            self.toggle_music()
        elif key == "r":
            self.new_game()
        return True

    def on_touch_down(self, touch):
        if self.game_over:
            self.new_game()
            return True
        if touch.x < self.width * 0.33:
            self.move(-1, 0)
        elif touch.x > self.width * 0.66:
            self.move(1, 0)
        else:
            self.rotate_piece()
        return True

    def on_touch_move(self, touch):
        if touch.dy < -12:
            self.soft_drop()
        return True

    def on_size(self, *args):
        self.redraw()

    def draw_text(self, text, x, y, size=22, color=(1, 1, 1, 1), anchor="left"):
        label = CoreLabel(text=text, font_size=size, color=color)
        label.refresh()
        texture = label.texture
        if anchor == "center":
            pos = (x - texture.size[0] / 2, y - texture.size[1] / 2)
        else:
            pos = (x, y)
        Rectangle(texture=texture, pos=pos, size=texture.size)

    def board_geometry(self):
        side = 150 if self.width >= 430 else 105
        cell = min((self.width - side - 35) / COLS, (self.height - 40) / ROWS)
        cell = max(14, cell)
        board_w = cell * COLS
        board_h = cell * ROWS
        board_x = 20
        board_y = (self.height - board_h) / 2
        return board_x, board_y, cell, side

    def draw_block(self, x, y, cell, color, board_x, board_y, alpha=1):
        px = board_x + x * cell
        py = board_y + y * cell
        r, g, b, a = color
        Color(r, g, b, min(a, alpha))
        Rectangle(pos=(px + 1, py + 1), size=(cell - 2, cell - 2))
        Color(1, 1, 1, 0.18 * alpha)
        Line(rectangle=(px + 2, py + 2, cell - 4, cell - 4), width=1)

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.04, 0.05, 0.09, 1)
            Rectangle(pos=self.pos, size=self.size)

            board_x, board_y, cell, side = self.board_geometry()
            board_w = cell * COLS
            board_h = cell * ROWS
            panel_x = board_x + board_w + 18

            Color(0.08, 0.09, 0.15, 1)
            Rectangle(pos=(board_x - 4, board_y - 4), size=(board_w + 8, board_h + 8))
            Color(0.12, 0.13, 0.21, 1)
            Rectangle(pos=(board_x, board_y), size=(board_w, board_h))

            Color(0.25, 0.27, 0.38, 0.55)
            for x in range(COLS + 1):
                Line(points=[board_x + x * cell, board_y, board_x + x * cell, board_y + board_h], width=1)
            for y in range(ROWS + 1):
                Line(points=[board_x, board_y + y * cell, board_x + board_w, board_y + y * cell], width=1)

            for y in range(ROWS):
                for x in range(COLS):
                    color = self.board[y][x]
                    if color:
                        self.draw_block(x, y, cell, color, board_x, board_y)

            if self.current and not self.game_over:
                ghost_y = self.current["y"]
                while not self.collides(self.current["blocks"], self.current["x"], ghost_y - 1):
                    ghost_y -= 1
                for bx, by in self.current["blocks"]:
                    self.draw_block(
                        self.current["x"] + bx,
                        ghost_y + by,
                        cell,
                        (0.85, 0.85, 0.95, 1),
                        board_x,
                        board_y,
                        alpha=0.18,
                    )
                for bx, by in self.current["blocks"]:
                    self.draw_block(
                        self.current["x"] + bx,
                        self.current["y"] + by,
                        cell,
                        self.current["color"],
                        board_x,
                        board_y,
                    )

            self.draw_text("ТЕТРИС", panel_x, self.height - 58, size=30, color=(0.9, 0.95, 1, 1))
            self.draw_text(f"Счёт: {self.score}", panel_x, self.height - 105, size=22)
            self.draw_text(f"Рекорд: {self.high_score}", panel_x, self.height - 135, size=22)
            self.draw_text(f"Линии: {self.lines}", panel_x, self.height - 165, size=22)
            self.draw_text(f"Уровень: {self.level}", panel_x, self.height - 195, size=22)
            self.draw_text("Следующая:", panel_x, self.height - 245, size=20, color=(0.85, 0.9, 1, 1))

            if self.next_piece:
                mini_cell = min(24, cell * 0.75)
                nx = panel_x + 10
                ny = self.height - 330
                for bx, by in PIECES[self.next_piece]:
                    Color(*COLORS[self.next_piece])
                    Rectangle(pos=(nx + bx * mini_cell, ny + by * mini_cell), size=(mini_cell - 2, mini_cell - 2))

            help_text = "←/→ движение\n↑ поворот\n↓ быстрее\nSpace сбросить\nP пауза\nM музыка\nR заново"
            for i, line in enumerate(help_text.split("\n")):
                self.draw_text(line, panel_x, 205 - i * 26, size=17, color=(0.78, 0.82, 0.92, 1))

            music_status = "музыка выкл" if self.music_muted else "музыка вкл"
            self.draw_text(music_status, panel_x, 20, size=16, color=(0.65, 0.75, 1, 1))

            if self.paused:
                Color(0, 0, 0, 0.55)
                Rectangle(pos=(board_x, board_y), size=(board_w, board_h))
                self.draw_text("ПАУЗА", board_x + board_w / 2, board_y + board_h / 2, size=42, anchor="center")

            if self.game_over:
                Color(0, 0, 0, 0.72)
                Rectangle(pos=(board_x, board_y), size=(board_w, board_h))
                self.draw_text("ИГРА ОКОНЧЕНА", board_x + board_w / 2, board_y + board_h / 2 + 55, size=32, anchor="center")
                self.draw_text(f"Финальный счёт: {self.score}", board_x + board_w / 2, board_y + board_h / 2 + 5, size=24, anchor="center")
                self.draw_text(f"Рекорд: {self.high_score}", board_x + board_w / 2, board_y + board_h / 2 - 35, size=24, anchor="center")
                self.draw_text("Space или клик — заново", board_x + board_w / 2, board_y + board_h / 2 - 85, size=20, anchor="center")


class TetrisApp(App):
    def build(self):
        self.title = "Тетрис на Kivy"
        return TetrisGame()


if __name__ == "__main__":
    TetrisApp().run()
