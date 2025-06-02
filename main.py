import sys
import pygame
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
window = pygame.display.set_mode((1200, 800))
clock = pygame.time.Clock()
FPS = 60
pygame.display.set_caption('Trex Game')

running = True

characterX = 120
characterY = 600

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                characterY -= 10

            elif event.key == pygame.K_DOWN:
                characterY += 10

    clock.tick(FPS)
    window.fill((0, 0, 0))
    pygame.draw.rect(window, (255, 255, 255), (characterX, characterY, 100, 100))
    pygame.display.update()

pygame.quit()
