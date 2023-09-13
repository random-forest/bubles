import pyxel

from src.Circle import Circle
from src.utils import Vec2, init_audio, text_label, get_str_width
from constants import *


class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title=SCREEN_TITLE)
        pyxel.mouse(True)

        self.stage = 1
        self.time = 0
        self.bg_color = self.stage % 16
        self.is_game_started = False
        self.is_game_over = False

        self.bubbles = self.generate_bubbles()

        self.last_frame_count = pyxel.frame_count
        self.last_action_time = 0

        self.stage_time_limit = (len(self.bubbles) * 2) + NUM_BONUS_SECONDS

        init_audio()

        pyxel.run(self.update, self.draw)

    def update(self):
        try:
            if pyxel.btnp(pyxel.KEY_Q):
                pyxel.quit()

            if self.is_game_started and not self.is_game_over:
                # Update timer
                self.update_timer()

            num_bubbles = len(list(filter(lambda b: b.text != " ", self.bubbles)))
            if self.time >= self.stage_time_limit + (self.stage_time_limit // 2) and num_bubbles != 0:
                self.is_game_over = True

            for bubble in self.bubbles:
                if bubble.text == " ":
                    # Remove bubbles outside the screen
                    if (
                        bubble.pos.x + bubble.r < 0 or bubble.pos.x - bubble.r > SCREEN_WIDTH or
                        bubble.pos.y + bubble.r < 0 or bubble.pos.y - bubble.r > SCREEN_HEIGHT
                    ):
                        self.bubbles.remove(bubble)
                    bubble.update()
                else:
                    dx = bubble.pos.x - pyxel.mouse_x
                    dy = bubble.pos.y - pyxel.mouse_y
                    # Detect if mouse on circle
                    if dx * dx + dy * dy < bubble.r * bubble.r:
                        bubble.hover_anim()
                    else:
                        bubble.r = 16

            # If bubbles is empty, go to next stage
            if num_bubbles == 0 and not self.is_game_over:
                self.init_next_stage()

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                if self.is_game_over:
                    self.restart_game()

                for i in range(num_bubbles):
                    bubble = self.bubbles[i]

                    dx = bubble.pos.x - pyxel.mouse_x
                    dy = bubble.pos.y - pyxel.mouse_y

                    # If click on circle
                    if dx * dx + dy * dy < bubble.r * bubble.r:
                        self.is_game_started = True
                        # Got correct bubble
                        if bubble.text == self.bubbles[0].text:
                            # Decrase timer
                            self.time -= 1
                            if self.time < 0.1:
                                self.time = abs(self.time)
                            # play sound
                            pyxel.play(2, [2], loop=False)
                            # Animation of explode
                            self.bubbles = [*self.bubbles, *bubble.explode_particles()]
                            self.bubbles.remove(bubble)
                            break
                        else:
                            self.time += 1
                            pyxel.play(3, [3], loop=False)
                    else:
                        # Incrase time if you click outside bubble
                        self.time += 0.1
                        if self.time < 0.1:
                            self.time = abs(self.time)
        except Exception as err:
            print(err)
            pass

    def draw(self):
        # Show game over screen
        if self.is_game_over:
            pyxel.cls(0)
            stage_message = f"STAGE {self.stage}"
            total_message = f"{round(self.time, 1)} of {self.stage_time_limit} seconds"
            text_label(pyxel.width // 2 - get_str_width(stage_message) // 2, pyxel.height // 2, stage_message, col=9)
            text_label(pyxel.width // 2 - get_str_width(total_message) // 2, pyxel.height // 2 + pyxel.FONT_HEIGHT + 10,
                       total_message, col=9)
            text_label(pyxel.width // 2 - get_str_width(GAMEOVER_MESSAGE) // 2, pyxel.height // 2 + pyxel.FONT_HEIGHT +
                       20, GAMEOVER_MESSAGE, col=9)
            # Draw blinked restart message
            if pyxel.frame_count % 20 < 10:
                pyxel.text(
                    pyxel.width // 2 - get_str_width(RESTART_MESSSAGE) // 2, (pyxel.height // 2) + 50,
                    RESTART_MESSSAGE,
                    9
                )
        else:
            if self.time > self.stage_time_limit:
                pyxel.cls(pyxel.COLOR_RED)
                pyxel.text(116, pyxel.height // 2, ATTENTION_MESSAGE, (pyxel.frame_count % 15) + 1)
            else:
                pyxel.cls(self.bg_color)

            for bubble in self.bubbles:
                # Draw bubble
                if bubble.color == self.bg_color:
                    pyxel.circb(bubble.pos.x, bubble.pos.y, bubble.r + 1, 0)
                if bubble.text == " ":
                    pyxel.circb(bubble.pos.x, bubble.pos.y, bubble.r, (pyxel.frame_count % 15) + 1)
                else:
                    pyxel.circ(bubble.pos.x, bubble.pos.y, bubble.r, bubble.color)

                # Calculate center of bubble and draw number
                number_text = str(bubble.text)
                text_x = bubble.pos.x - (pyxel.FONT_WIDTH * len(number_text)) // 2
                text_y = bubble.pos.y - pyxel.FONT_HEIGHT // 2

                if bubble.color == 7:
                    pyxel.text(text_x + 1, text_y + 1, bubble.text, pyxel.rndi(1, 6))
                else:
                    pyxel.text(text_x + 1, text_y + 1, bubble.text, 7)

            pyxel.text(10, 10, f'{GUI_STAGE_TEXT} {self.stage}', 7)
            # Draw time of a round
            timer_text = f"{round(self.time, 1)} / {self.stage_time_limit} sec"
            top_right = pyxel.width - get_str_width(timer_text) - 10
            pyxel.text(top_right, 10, timer_text, 7)

            # Draw init message
            if not self.is_game_started and pyxel.frame_count % 20 < 10:
                pyxel.text(pyxel.width // 2 - get_str_width(INIT_MESSAGE) // 2, pyxel.height // 2, INIT_MESSAGE,
                           (pyxel.frame_count % 15) + 1)

    def update_timer(self):
        current_frame_count = pyxel.frame_count
        elapsed_frames = current_frame_count - self.last_frame_count
        # Assuming 60 frames per second (16.67 milliseconds per frame)
        elapsed_time_ms = elapsed_frames * 16.67
        # Increment the timer by the elapsed time
        self.last_action_time += elapsed_time_ms
        if self.last_action_time >= 1000:
            self.time += 0.1

    def init_next_stage(self):
        self.time = 0
        self.stage += 1
        self.bg_color = self.stage % 16
        self.bubbles = self.generate_bubbles()
        self.stage_time_limit = (len(self.bubbles) * 2) + NUM_BONUS_SECONDS

    def restart_game(self):
        self.time = 0
        self.stage = 1
        self.bg_color = self.stage % 16
        self.bubbles = self.generate_bubbles()
        self.stage_time_limit = (len(self.bubbles) * 2) + NUM_BONUS_SECONDS
        self.is_game_over = False

    def generate_bubbles(self):
        circles = []
        num_circles = self.stage + 1

        while len(circles) < num_circles:
            text = str(len(circles) + 1)  # Example text for the circle
            position = Vec2(
                pyxel.rndf(16, SCREEN_WIDTH - 16),
                pyxel.rndf(16, SCREEN_HEIGHT - 16)
            )
            velocity = Vec2(
                pyxel.rndf(-MAX_BUBBLE_SPEED, MAX_BUBBLE_SPEED),
                pyxel.rndf(-MAX_BUBBLE_SPEED, MAX_BUBBLE_SPEED)
            )
            new_circle = Circle(text, pos=position, vel=velocity)
            collision = False

            for circle in circles:
                if new_circle.check_collision(circle):
                    collision = True
                    break
            if not collision:
                circles.append(new_circle)

        return circles
