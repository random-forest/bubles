import pyxel

from src.utils import Vec2
from constants import *


class Circle:
    def __init__(self, text: str, pos=None, vel=None):
        self.text = text
        self.r = 16

        if not pos:
            self.pos = Vec2(
                pyxel.rndf(self.r, SCREEN_WIDTH - self.r),
                pyxel.rndf(self.r, SCREEN_HEIGHT - self.r),
            )
        else:
            self.pos = pos

        if not vel:
            self.vel = Vec2(
                pyxel.rndf(-MAX_BUBBLE_SPEED, MAX_BUBBLE_SPEED),
                pyxel.rndf(-MAX_BUBBLE_SPEED, MAX_BUBBLE_SPEED),
            )
        else:
            self.vel = vel

        self.color = pyxel.rndi(1, 15)

    def update(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

        self.r += pyxel.rndi(1, MAX_BUBBLE_SPEED // 2)

        # if self.vel.x < 0 and self.pos.x < self.r:
        #     self.vel.x *= -1
        #
        # if self.vel.x > 0 and self.pos.x > SCREEN_WIDTH - self.r:
        #     self.vel.x *= -1
        #
        # if self.vel.y < 0 and self.pos.y < self.r:
        #     self.vel.y *= -1
        #
        # if self.vel.y > 0 and self.pos.y > SCREEN_HEIGHT - self.r:
        #     self.vel.y *= -1

    def hover_anim(self):
        if pyxel.frame_count % 20 < 10:
            self.r = self.r + 0.5
        else:
            self.r = self.r - 0.5

    def explode_particles(self):
        result = []

        new_radius = pyxel.sqrt(self.r * self.r / NUM_EXPLODE_BUBBLES) * 2

        for j in range(NUM_EXPLODE_BUBBLES):
            angle = 360 * j / NUM_EXPLODE_BUBBLES

            part = Circle(" ")
            part.r = new_radius
            part.pos.x = self.pos.x + (self.r + new_radius) * pyxel.cos(angle)
            part.pos.y = self.pos.y + (self.r + new_radius) * pyxel.sin(angle)
            part.vel.x = pyxel.cos(angle) * MAX_BUBBLE_SPEED
            part.vel.y = pyxel.sin(angle) * MAX_BUBBLE_SPEED

            result.append(part)

        return result

    def check_collision(self, circle2):
        distance = (self.pos.x - circle2.pos.x) ** 2 + (self.pos.y - circle2.pos.y) ** 2
        return distance <= (self.r + circle2.r) ** 2
