from random import randint

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.label import Label
from kivy.uix.widget import Widget


class FlappyBirdGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.gravity = -950
        self.jump_power = 380
        self.pipe_speed = 230
        self.pipe_interval = 1.45

        self.bird_size = 36
        self.bird_x = 120
        self.bird_y = 300
        self.bird_velocity = 0

        self.ground_height = 70
        self.pipe_width = 70
        self.gap_height = 180
        self.pipe_timer = 0
        self.pipes = []

        self.score = 0
        self.best_score = 0
        self.game_state = 'ready'

        self.score_label = Label(
            text='Счет: 0   Highscore: 0',
            font_size='28sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(460, 60),
        )
        self.help_label = Label(
            text='Flappy Bird\nПробел / клик — взлететь',
            font_size='22sp',
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(520, 170),
        )
        self.add_widget(self.score_label)
        self.add_widget(self.help_label)

        Window.bind(on_key_down=self.on_key_down)
        self.bind(size=self.reset_game)
        Clock.schedule_interval(self.update, 1 / 60)

    def reset_game(self, *args):
        self.ground_height = max(55, self.height * 0.12)
        self.pipe_width = max(55, self.width * 0.09)
        self.gap_height = max(150, self.height * 0.28)
        self.bird_size = max(30, min(self.width, self.height) * 0.055)
        self.bird_x = self.width * 0.25
        self.bird_y = self.height * 0.55
        self.bird_velocity = 0
        self.pipe_timer = 0
        self.pipes = []
        self.score = 0
        self.game_state = 'ready'
        self.update_labels()
        self.draw_game()

    def start_game(self):
        if self.game_state in ('ready', 'game_over'):
            if self.game_state == 'game_over':
                self.reset_game()
            self.game_state = 'playing'
            self.help_label.opacity = 0
        self.jump()

    def jump(self):
        self.bird_velocity = self.jump_power

    def on_touch_down(self, touch):
        self.start_game()
        return True

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        char = codepoint.lower() if codepoint else ''
        if key in (32, 273) or char in ('w', 'ц'):
            self.start_game()
        elif char in ('r', 'к'):
            self.reset_game()
        return True

    def create_pipe(self):
        min_gap_y = self.ground_height + 80
        max_gap_y = max(min_gap_y + 1, self.height - self.gap_height - 80)
        gap_y = randint(int(min_gap_y), int(max_gap_y))
        self.pipes.append({
            'x': self.width + self.pipe_width,
            'gap_y': gap_y,
            'passed': False,
        })

    def update(self, dt):
        if self.width <= 0 or self.height <= 0:
            return

        if self.game_state == 'playing':
            self.bird_velocity += self.gravity * dt
            self.bird_y += self.bird_velocity * dt

            self.pipe_timer += dt
            if self.pipe_timer >= self.pipe_interval:
                self.pipe_timer = 0
                self.create_pipe()

            for pipe in self.pipes:
                pipe['x'] -= self.pipe_speed * dt

                # Счет обновляется сразу после того, как птичка полностью пролетела трубу.
                if not pipe['passed'] and pipe['x'] + self.pipe_width < self.bird_x - self.bird_size / 2:
                    pipe['passed'] = True
                    self.score += 1
                    self.best_score = max(self.best_score, self.score)
                    self.update_labels()

            self.pipes = [pipe for pipe in self.pipes if pipe['x'] + self.pipe_width > -10]

            if self.has_collision():
                self.game_over()

        self.update_labels()
        self.draw_game()

    def has_collision(self):
        bird_left = self.bird_x - self.bird_size / 2
        bird_right = self.bird_x + self.bird_size / 2
        bird_bottom = self.bird_y - self.bird_size / 2
        bird_top = self.bird_y + self.bird_size / 2

        if bird_bottom <= self.ground_height or bird_top >= self.height:
            return True

        for pipe in self.pipes:
            pipe_left = pipe['x']
            pipe_right = pipe['x'] + self.pipe_width
            gap_bottom = pipe['gap_y']
            gap_top = pipe['gap_y'] + self.gap_height

            horizontal_hit = bird_right > pipe_left and bird_left < pipe_right
            vertical_hit = bird_bottom < gap_bottom or bird_top > gap_top
            if horizontal_hit and vertical_hit:
                return True

        return False

    def game_over(self):
        self.game_state = 'game_over'
        self.best_score = max(self.best_score, self.score)
        self.help_label.opacity = 1
        self.help_label.text = (
            f'Игра окончена\nФинальный счет: {self.score}\nHighscore: {self.best_score}\n'
            'Пробел / клик — заново\nR — сброс'
        )
        self.update_labels()

    def update_labels(self):
        self.score_label.text = f'Счет: {self.score}   Highscore: {self.best_score}'
        self.score_label.center_x = self.width / 2
        self.score_label.top = self.height - 10

        self.help_label.center_x = self.width / 2
        self.help_label.center_y = self.height / 2
        self.help_label.text_size = self.help_label.size

        if self.game_state == 'ready':
            self.help_label.opacity = 1
            self.help_label.text = 'Flappy Bird\nПробел / клик — взлететь'

    def draw_cloud(self, x, y, scale=1):
        Color(1, 1, 1, 0.85)
        Ellipse(pos=(x, y), size=(70 * scale, 35 * scale))
        Ellipse(pos=(x + 25 * scale, y + 15 * scale), size=(55 * scale, 45 * scale))
        Ellipse(pos=(x + 65 * scale, y + 5 * scale), size=(70 * scale, 38 * scale))
        Rectangle(pos=(x + 25 * scale, y), size=(75 * scale, 30 * scale))

    def draw_game(self):
        self.canvas.clear()

        with self.canvas:
            # Темно-синий фон.
            Color(0.03, 0.08, 0.22, 1)
            Rectangle(pos=(0, 0), size=self.size)

            # Облака на фоне.
            self.draw_cloud(self.width * 0.08, self.height * 0.78, 0.85)
            self.draw_cloud(self.width * 0.58, self.height * 0.68, 1.05)
            self.draw_cloud(self.width * 0.30, self.height * 0.50, 0.65)

            Color(0.07, 0.20, 0.12, 1)
            Rectangle(pos=(0, 0), size=(self.width, self.ground_height))

            Color(0.14, 0.45, 0.20, 1)
            Rectangle(pos=(0, self.ground_height), size=(self.width, 12))

            for pipe in self.pipes:
                x = pipe['x']
                gap_y = pipe['gap_y']

                Color(0.10, 0.70, 0.25, 1)
                Rectangle(pos=(x, self.ground_height), size=(self.pipe_width, gap_y - self.ground_height))
                Rectangle(
                    pos=(x, gap_y + self.gap_height),
                    size=(self.pipe_width, self.height - gap_y - self.gap_height),
                )

                Color(0.08, 0.55, 0.18, 1)
                Rectangle(pos=(x - 5, gap_y - 18), size=(self.pipe_width + 10, 18))
                Rectangle(pos=(x - 5, gap_y + self.gap_height), size=(self.pipe_width + 10, 18))

            # Птичка: простой оранжевый круг без лишних деталей.
            Color(1.0, 0.45, 0.02, 1)
            Ellipse(
                pos=(self.bird_x - self.bird_size / 2, self.bird_y - self.bird_size / 2),
                size=(self.bird_size, self.bird_size),
            )


class FlappyBirdApp(App):
    title = 'Flappy Bird Kivy'

    def build(self):
        Window.size = (480, 720)
        return FlappyBirdGame()


if __name__ == '__main__':
    FlappyBirdApp().run()
