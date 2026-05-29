import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.label import Label
from kivy.uix.widget import Widget


class SnakeGame(Widget):
    grid_size = 24
    speed = 0.13

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snake = []
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.fruit = (0, 0)
        self.score = 0
        self.game_over = False
        self.cell_size = 20
        self.field_x = 0
        self.field_y = 0

        self.score_label = Label(font_size=24, bold=True)
        self.message_label = Label(font_size=32, bold=True, halign='center')
        self.add_widget(self.score_label)
        self.add_widget(self.message_label)

        self.bind(size=self.redraw, pos=self.redraw)
        Window.bind(on_key_down=self.on_key_down)
        self.start_game()

    def start_game(self):
        center = self.grid_size // 2
        self.snake = [(center, center), (center - 1, center), (center - 2, center)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.place_fruit()
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, self.speed)
        self.redraw()

    def place_fruit(self):
        free_cells = [
            (x, y)
            for x in range(self.grid_size)
            for y in range(self.grid_size)
            if (x, y) not in self.snake
        ]
        self.fruit = random.choice(free_cells)

    def update_layout_data(self):
        side = min(self.width, self.height)
        self.cell_size = int(side // self.grid_size)
        field_side = self.cell_size * self.grid_size
        self.field_x = self.x + (self.width - field_side) / 2
        self.field_y = self.y + (self.height - field_side) / 2

    def update(self, _dt):
        if self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        step_x, step_y = self.direction
        new_head = (head_x + step_x, head_y + step_y)

        out_of_field = (
            new_head[0] < 0
            or new_head[0] >= self.grid_size
            or new_head[1] < 0
            or new_head[1] >= self.grid_size
        )
        if out_of_field:
            self.finish_game()
            return

        eating = new_head == self.fruit
        body_for_check = self.snake if eating else self.snake[:-1]
        if new_head in body_for_check:
            self.finish_game()
            return

        self.snake.insert(0, new_head)
        if eating:
            self.score += 1
            self.place_fruit()
        else:
            self.snake.pop()

        self.redraw()

    def finish_game(self):
        self.game_over = True
        Clock.unschedule(self.update)
        self.redraw()

    def change_direction(self, new_direction):
        opposite_direction = (-self.direction[0], -self.direction[1])
        if new_direction != opposite_direction:
            self.next_direction = new_direction

    def on_key_down(self, _window, key, _scancode, codepoint, _modifiers):
        key_by_code = {
            273: (0, 1),
            274: (0, -1),
            275: (1, 0),
            276: (-1, 0),
        }
        key_by_letter = {
            'w': (0, 1),
            'ц': (0, 1),
            's': (0, -1),
            'ы': (0, -1),
            'd': (1, 0),
            'в': (1, 0),
            'a': (-1, 0),
            'ф': (-1, 0),
        }

        if self.game_over and (key == 32 or codepoint in (' ', '\r')):
            self.start_game()
            return True

        if key in key_by_code:
            self.change_direction(key_by_code[key])
            return True

        symbol = (codepoint or '').lower()
        if symbol in key_by_letter:
            self.change_direction(key_by_letter[symbol])
            return True

        return False

    def on_touch_down(self, touch):
        if self.game_over:
            self.start_game()
            return True

        if not self.collide_point(touch.x, touch.y):
            return False

        rel_x = (touch.x - self.x) / max(self.width, 1)
        rel_y = (touch.y - self.y) / max(self.height, 1)
        inv_x = 1 - rel_x

        if rel_x > rel_y and inv_x > rel_y:
            self.change_direction((0, -1))
        elif rel_x > rel_y >= inv_x:
            self.change_direction((1, 0))
        elif rel_x <= rel_y < inv_x:
            self.change_direction((-1, 0))
        else:
            self.change_direction((0, 1))

        return True

    def draw_cell(self, cell, rgba):
        x, y = cell
        margin = 2
        Color(*rgba)
        Rectangle(
            pos=(self.field_x + x * self.cell_size + margin,
                 self.field_y + y * self.cell_size + margin),
            size=(self.cell_size - margin * 2, self.cell_size - margin * 2),
        )

    def redraw(self, *_args):
        self.update_layout_data()
        field_side = self.cell_size * self.grid_size

        self.canvas.clear()
        with self.canvas:
            Color(0.08, 0.08, 0.08, 1)
            Rectangle(pos=self.pos, size=self.size)

            Color(0.18, 0.18, 0.18, 1)
            Rectangle(pos=(self.field_x, self.field_y), size=(field_side, field_side))

            Color(0.28, 0.28, 0.28, 1)
            for i in range(self.grid_size + 1):
                x = self.field_x + i * self.cell_size
                y = self.field_y + i * self.cell_size
                Line(points=[x, self.field_y, x, self.field_y + field_side], width=1)
                Line(points=[self.field_x, y, self.field_x + field_side, y], width=1)

            self.draw_cell(self.fruit, (1, 0.25, 0.25, 1))
            for index, cell in enumerate(self.snake):
                if index == 0:
                    self.draw_cell(cell, (0.25, 1, 0.35, 1))
                else:
                    self.draw_cell(cell, (0.1, 0.65, 0.2, 1))

        self.score_label.text = f'Счет: {self.score}'
        self.score_label.size = (220, 40)
        self.score_label.pos = (self.x + 10, self.top - 45)

        if self.game_over:
            self.message_label.text = 'Игра окончена\nНажмите Space или кликните мышью'
        else:
            self.message_label.text = ''
        self.message_label.size = self.size
        self.message_label.pos = self.pos


class SnakeApp(App):
    def build(self):
        self.title = 'Змейка на Kivy'
        return SnakeGame()


if __name__ == '__main__':
    SnakeApp().run()
