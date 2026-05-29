from random import choice

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, ObjectProperty, ReferenceListProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector


class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-vx, vy)
            vel = bounced * 1.08
            ball.velocity = vel.x, vel.y + offset * 2


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    left_direction = NumericProperty(0)
    right_direction = NumericProperty(0)
    paddle_speed = NumericProperty(7)

    def serve_ball(self, direction=None):
        if direction is None:
            direction = choice((-1, 1))
        self.ball.center = self.center
        self.ball.velocity = Vector(4 * direction, choice((-2, -1, 1, 2)))

    def update(self, dt):
        self.move_paddles()
        self.ball.move()

        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        if self.ball.y <= self.y:
            self.ball.y = self.y
            self.ball.velocity_y *= -1
        if self.ball.top >= self.top:
            self.ball.top = self.top
            self.ball.velocity_y *= -1

        if self.ball.right < self.x:
            self.player2.score += 1
            self.serve_ball(direction=1)
        if self.ball.x > self.right:
            self.player1.score += 1
            self.serve_ball(direction=-1)

    def move_paddles(self):
        self.player1.center_y += self.left_direction * self.paddle_speed
        self.player2.center_y += self.right_direction * self.paddle_speed
        self.keep_paddle_inside(self.player1)
        self.keep_paddle_inside(self.player2)

    def keep_paddle_inside(self, paddle):
        if paddle.y < self.y:
            paddle.y = self.y
        if paddle.top > self.top:
            paddle.top = self.top

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
            self.keep_paddle_inside(self.player1)
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y
            self.keep_paddle_inside(self.player2)

    def reset_game(self):
        self.player1.score = 0
        self.player2.score = 0
        self.serve_ball()

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key == 119:      # W
            self.left_direction = 1
        elif key == 115:    # S
            self.left_direction = -1
        elif key == 273:    # Arrow Up
            self.right_direction = 1
        elif key == 274:    # Arrow Down
            self.right_direction = -1
        elif key == 32:     # Space
            self.reset_game()
        return True

    def on_key_up(self, window, key, scancode):
        if key in (119, 115):
            self.left_direction = 0
        elif key in (273, 274):
            self.right_direction = 0
        return True


class PongApp(App):
    title = 'Пинг-понг'

    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        Window.bind(on_key_down=game.on_key_down)
        Window.bind(on_key_up=game.on_key_up)
        return game


if __name__ == '__main__':
    PongApp().run()
