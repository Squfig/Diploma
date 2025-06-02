import pygame


def load_image(path):
    img = pygame.image.load('data/images/' + path).convert()
    img.set_colorkey((0, 0, 0))
    return img
