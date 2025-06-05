import sys
import pygame
import os
from pygame.math import Vector2
import math
import random

os.environ['SDL_VIDEO_CENTERED'] = '1'  # hack to start the window in the center of the screen.
WINDOW_HEIGHT = 720
WINDOW_WIDTH = 1280
WINDOW_TITLE = 'T. rex Runner'
BACKGROUND_IMAGE = './Assets/bg.jpg'
GRAVITY = 4.8
OBSTACLE_SPEED = 12
MIN_OBSTACLE_GAP = 300


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, posx, posy, path_to_image):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(path_to_image), (80, 80))
        self.rect = self.image.get_rect()
        self.rect.center = (posx, posy)

    def get_hitbox(self):
        margin_x = self.rect.width * 0.3
        margin_y = self.rect.height * 0.2
        return pygame.Rect(
            self.rect.x + margin_x,
            self.rect.y + margin_y,
            self.rect.width - 2 * margin_x,
            self.rect.height - 2 * margin_y
        )


class Dino(pygame.sprite.Sprite):
    def __init__(self, posx, posy, image_folder):
        super().__init__()
        self.frames = [
            pygame.transform.scale(
                pygame.image.load(os.path.join(image_folder, f'1 ({i}).png')),
                (180, 180)
            ) for i in range(1, 13)
        ]
        self.idle_frames = [
            pygame.transform.scale(
                pygame.image.load(os.path.join('./Assets/trex/idle sequence/', f'1 ({i}).png')), (180, 180)
            ) for i in range(1, 13)
        ]
        self.jump_frames = [
            pygame.transform.scale(
                pygame.image.load(os.path.join('./Assets/trex/jump sequence/', f'1 ({i}).png')), (185, 185)
            ) for i in range(1, 13)
        ]

        self.state = 'walk'
        self.current_frame = 0
        self.animation_speed = 0.25
        self.frame_counter = 0

        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (posx, posy)

    def update(self):
        self.frame_counter += self.animation_speed
        if self.state == 'walk':
            frames = self.frames
        elif self.state == 'jump':
            frames = self.jump_frames
        else:
            frames = self.idle_frames

        if self.frame_counter >= len(frames):
            self.frame_counter = 0
        print(self.frame_counter)
        self.current_frame = int(self.frame_counter)
        print(self.current_frame)
        self.image = frames[self.current_frame]

    def get_hitbox(self):
        margin_x = self.rect.width * 0.2
        margin_y = self.rect.height * 0.3
        return pygame.Rect(
            self.rect.x + margin_x,
            self.rect.y + margin_y,
            self.rect.width - 2 * margin_x,
            self.rect.height - 2 * margin_y
        )


class GameState:
    def __init__(self):
        self.score = 0
        self.high_score = self.get_high_score()
        self.dino_pos = Vector2(180, 590)
        self.obstacle_y_pos = 620
        self.obstacle_x_pos = [800, 1250, 1560, 1980]
        self.get_high_score()
        self.last_score_checkpoint = 0

    def update(self, move_dino_command):
        self.dino_pos += move_dino_command

        if self.dino_pos.y > 590:
            self.dino_pos.y = 590
        elif self.dino_pos.y <= 180:
            self.dino_pos.y = 180

        # For future update if I decide to add x axis movement while jumping.
        # if self.dino_pos.x > WINDOW_WIDTH-50:
        #     self.dino_pos.x = WINDOW_WIDTH - 50
        # elif self.dino_pos.x <= 180:
        #     self.dino_pos.x = 180

    def get_high_score(self):
        try:
            with open(f'highscore.txt', 'r') as file:
                return int(file.readline().strip())
        except FileNotFoundError:
            with open(f'highscore.txt', 'w') as file:
                file.write(str(self.high_score))


class UI:
    def __init__(self):
        pygame.init()
        self.running = True
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.gamestate = GameState()
        self.moveDinoCommand = Vector2(0, 0)
        self.background = pygame.image.load(BACKGROUND_IMAGE).convert()
        self.dino = Dino(self.gamestate.dino_pos.x, self.gamestate.dino_pos.y, './Assets/trex/walk sequence/')

        # Set FPS
        self.fps = 60

        self.obs1 = Obstacle(self.gamestate.obstacle_x_pos[0], self.gamestate.obstacle_y_pos,
                             './Assets/trex/obstacle.png')
        self.obs2 = Obstacle(self.gamestate.obstacle_x_pos[1], self.gamestate.obstacle_y_pos,
                             './Assets/trex/obstacle.png')
        self.obs3 = Obstacle(self.gamestate.obstacle_x_pos[2], self.gamestate.obstacle_y_pos,
                             './Assets/trex/obstacle.png')
        self.obs4 = Obstacle(self.gamestate.obstacle_x_pos[3], self.gamestate.obstacle_y_pos,
                             './Assets/trex/obstacle.png')

        self.background_tiles = math.ceil(WINDOW_WIDTH / self.background.get_width()) + 1
        self.scroll = 0
        self.y_change = 0

        self.active = True

        # font setup

        self.font = pygame.font.Font('freesansbold.ttf', 24)
        self.gameOverfont = pygame.font.Font('freesansbold.ttf', 44)

        pygame.display.set_caption(WINDOW_TITLE)
        pygame.display.set_icon(pygame.image.load('icon.png'))
        pygame.mouse.set_visible(False)

        # BG music setup

        pygame.mixer.music.load('./Assets/sfx/bg.mp3')
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)

        # Jump sound setup

        self.jump_sound = pygame.mixer.Sound('./Assets/sfx/jump.wav')
        self.jump_sound.set_volume(0.3)

        # Game over sound setup

        self.game_over_sound = pygame.mixer.Sound('./Assets/sfx/gaameover.mp3')
        self.game_over_sound.set_volume(0.1)

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if not self.active and (
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_r) or
                    (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
            ):
                self.game_over_sound.stop()
                self.active = True
                self.dino.state = 'walk'
                self.gamestate.score = 0
                self.gamestate.obstacle_x_pos = [800, 1250, 1560, 1980]
                pygame.mixer.music.play(-1)
                self.obs1.rect.center = (self.gamestate.obstacle_x_pos[0], self.gamestate.obstacle_y_pos)
                self.obs2.rect.center = (self.gamestate.obstacle_x_pos[1], self.gamestate.obstacle_y_pos)
                self.obs3.rect.center = (self.gamestate.obstacle_x_pos[2], self.gamestate.obstacle_y_pos)
                self.obs4.rect.center = (self.gamestate.obstacle_x_pos[3], self.gamestate.obstacle_y_pos)

            if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_SPACE and self.y_change == 0:
                    self.y_change = 60
                    self.dino.state = 'jump'
                    self.jump_sound.play()

        for i in range(len(self.gamestate.obstacle_x_pos)):
            if self.active:
                self.gamestate.obstacle_x_pos[i] -= OBSTACLE_SPEED
                if self.gamestate.obstacle_x_pos[i] < self.gamestate.dino_pos.x - 180:
                    self.gamestate.score += 1

                    while True:
                        random_x = random.randint(1290, 2000)
                        if all(abs(random_x - other_x) > MIN_OBSTACLE_GAP for other_x in self.gamestate.obstacle_x_pos):
                            self.gamestate.obstacle_x_pos[i] = random_x
                            break

                if (self.dino.get_hitbox().colliderect(self.obs1.get_hitbox()) or
                        self.dino.get_hitbox().colliderect(self.obs2.get_hitbox()) or
                        self.dino.get_hitbox().colliderect(self.obs3.get_hitbox()) or
                        self.dino.get_hitbox().colliderect(self.obs4.get_hitbox())):
                    self.active = False
                    self.dino.state = 'idle'
                    break

        if self.y_change > 0 or self.gamestate.dino_pos.y < 590:
            self.gamestate.dino_pos.y -= self.y_change
            self.y_change -= GRAVITY

        if self.gamestate.dino_pos.y > 590:
            self.gamestate.dino_pos.y = 590

        if self.gamestate.dino_pos.y == 590 and self.y_change < 0:
            self.y_change = 0
            if not self.active:
                self.dino.state = 'idle'
            else:
                self.dino.state = 'walk'

    def update(self):
        # Increases 1 FPS every 100 points achieved
        if self.gamestate.score - self.gamestate.last_score_checkpoint >= 100:
            self.fps += 1
            self.gamestate.last_score_checkpoint = self.gamestate.score

        self.gamestate.update(self.moveDinoCommand)

    def render(self):
        # Background
        for i in range(0, self.background_tiles):
            self.window.blit(self.background, (i * self.background.get_width() + self.scroll, 0))

        if self.active:
            self.scroll -= 5

        if abs(self.scroll) > self.background.get_width():
            self.scroll = 0

        # Dino Sprite
        self.dino.update()
        self.dino.rect.center = (self.gamestate.dino_pos.x, self.gamestate.dino_pos.y)
        self.window.blit(self.dino.image, self.dino.rect)

        # Obstacle 1 Sprite
        self.obs1.rect.center = (self.gamestate.obstacle_x_pos[0], self.gamestate.obstacle_y_pos)
        self.window.blit(self.obs1.image, self.obs1.rect)

        # Obstacle 2 Sprite
        self.obs2.rect.center = (self.gamestate.obstacle_x_pos[1], self.gamestate.obstacle_y_pos)
        self.window.blit(self.obs2.image, self.obs2.rect)

        # Obstacle 3 Sprite
        self.obs3.rect.center = (self.gamestate.obstacle_x_pos[2], self.gamestate.obstacle_y_pos)
        self.window.blit(self.obs3.image, self.obs3.rect)

        # Obstacle 4 Sprite
        self.obs4.rect.center = (self.gamestate.obstacle_x_pos[3], self.gamestate.obstacle_y_pos)
        self.window.blit(self.obs4.image, self.obs4.rect)

        # Draw Obstacle and Dino hitboxes jusst for checking
        # pygame.draw.rect(self.window, (0, 255, 0), self.dino.get_hitbox(), 2)
        # pygame.draw.rect(self.window, (0, 255, 255), self.obs1.get_hitbox(), 2)
        # pygame.draw.rect(self.window, (0, 255, 255), self.obs2.get_hitbox(), 2)
        # pygame.draw.rect(self.window, (0, 255, 255), self.obs3.get_hitbox(), 2)
        # pygame.draw.rect(self.window, (0, 255, 255), self.obs4.get_hitbox(), 2)

        # Score Text
        if self.active:
            if self.gamestate.score < 100:
                score_obj = self.font.render(f'Score: {self.gamestate.score}', True, (255, 255, 255))
                self.window.blit(score_obj, (WINDOW_WIDTH - 120, 30))
            else:
                score_obj = self.font.render(f'Score: {self.gamestate.score}', True, (255, 255, 255))
                self.window.blit(score_obj, (WINDOW_WIDTH - 135, 30))

        # Game over display

        if not self.active:
            pygame.mixer.music.stop()
            self.game_over_sound.play(-1)
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.window.blit(overlay, (0, 0))

            game_over_text = self.gameOverfont.render("GAME OVER", True, (255, 50, 50))
            self.window.blit(game_over_text, (WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 - 50))

            score_obj = self.font.render(f'Your Last Score was: {self.gamestate.score}', True, (0, 255, 255))
            self.window.blit(score_obj, (WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 + 200))

            if self.gamestate.score > self.gamestate.high_score:
                self.gamestate.high_score = self.gamestate.score
                with open(f'highscore.txt', 'w') as file:
                    file.write(str(self.gamestate.high_score))

            highscore_obj = self.font.render(f'High Score: {self.gamestate.high_score}', True, (255, 255, 0))
            self.window.blit(highscore_obj, (WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 + 230))

            instruction_text = self.font.render("Press 'R' to Restart and 'Space' to jump", True, (255, 255, 255))
            self.window.blit(instruction_text, (WINDOW_WIDTH // 2 - 210, WINDOW_HEIGHT // 2 + 10))

        pygame.display.update()

    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(self.fps)


game_ui = UI()
game_ui.run()
pygame.quit()
