import sys
import pygame
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'  # hack to start the window in the center of the screen.


class GameState:
    def __init__(self):
        self.x = 120
        self.y = 600

    def update(self, move_command_x, move_command_y):
        self.x += move_command_x
        self.y += move_command_y


class UI:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((1200, 800))
        self.clock = pygame.time.Clock()
        self.FPS = 60
        pygame.display.set_caption('T. rex Runner')
        pygame.display.set_icon(pygame.image.load('icon.png'))
        self.running = True
        self.gamestate = GameState()
        self.move_command_x = 0
        self.move_command_y = 0

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.gamestate.y -= 10

                elif event.key == pygame.K_DOWN:
                    self.gamestate.y += 10

    def update(self):
        self.gamestate.update(self.move_command_x, self.move_command_y)

    def render(self):
        self.window.fill((0, 0, 0))
        pygame.draw.rect(self.window, (255, 255, 255), (self.gamestate.x, self.gamestate.y, 100, 100))
        pygame.display.update()

    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(self.FPS)


game_ui = UI()
game_ui.run()
pygame.quit()
