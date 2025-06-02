import sys
import pygame
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'  # hack to start the window in the center of the screen.


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((1200, 800))
        self.clock = pygame.time.Clock()
        self.FPS = 60
        pygame.display.set_caption('T. rex Runner')
        pygame.display.set_icon(pygame.image.load('icon.png'))
        self.running = True
        self.characterX = 120
        self.characterY = 600

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.characterY -= 10

                elif event.key == pygame.K_DOWN:
                    self.characterY += 10

    def update(self):
        pass

    def render(self):
        self.window.fill((0, 0, 0))
        pygame.draw.rect(self.window, (255, 255, 255), (self.characterX, self.characterY, 100, 100))
        pygame.display.update()

    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(self.FPS)


game = Game()
game.run()
pygame.quit()