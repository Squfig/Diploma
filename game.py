import pygame


from sys import exit
from scripts.utils import load_image
from scripts.entities import Player, Box, Enemy, Button, Door
from scripts.tilemap import Tilemap


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Diploma')
        self.screen = pygame.display.set_mode((960, 640))
        self.display = pygame.Surface((480, 320))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.assets = {
            'box': load_image('box.png'),
            'exit': load_image('exit.png'),
            'stone': load_image('stone.png'),
            'enemy': load_image('enemy.png'),
            'player': load_image('player.png'),
            'spikes': load_image('spikes.png'),
            'button_red': load_image('button_red.png'),
            'button_red_pressed': load_image('button_red_pressed.png'),
            'door_red': load_image('door_red.png'),
            'door_red_open': load_image('door_red_open.png'),
            'button_green': load_image('button_green.png'),
            'button_green_pressed': load_image('button_green_pressed.png'),
            'door_green': load_image('door_green.png'),
            'door_green_open': load_image('door_green_open.png'),
            'button_blue': load_image('button_blue.png'),
            'button_blue_pressed': load_image('button_blue_pressed.png'),
            'door_blue': load_image('door_blue.png'),
            'door_blue_open': load_image('door_blue_open.png'),
            'background': load_image('background.png'),
            'tutorial': load_image('tutorial.png'),
            'rip': load_image('rip.png'),
            'torch': load_image('torch.png'),
        }
        self.tilemap = Tilemap(self, tile_size=16)
        self.level = 0
        self.boxes = []
        self.enemies = []
        self.buttons = []
        self.doors = []
        self.player = Player(self, (0, 0), (16, 16))

        pygame.mixer.music.load("data/music/background_music.mp3")
        pygame.mixer.music.set_volume(0.05)
        pygame.mixer.music.play(-1)
        self.music_on = True

        self.load_level(self.level)

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        self.boxes = []
        self.enemies = []
        self.buttons = []
        self.doors = []
        for tile_pos in list(self.tilemap.tilemap):
            tile = self.tilemap.tilemap[tile_pos]
            pos = (tile['pos'][0] * self.tilemap.tile_size, tile['pos'][1] * self.tilemap.tile_size)
            size = (self.tilemap.tile_size,) * 2

            if tile['type'] == 'player':
                self.player = Player(self, pos, size)
                self.tilemap.tilemap.pop(tile_pos)
            elif tile['type'] == 'box':
                self.boxes.append(Box(self, pos, size))
                self.tilemap.tilemap.pop(tile_pos)
            elif tile['type'] == 'enemy':
                self.enemies.append(Enemy(self, pos, size))
                self.tilemap.tilemap.pop(tile_pos)
            if tile['type'].startswith('button_'):
                color = tile['type'].split('_')[1]
                self.buttons.append(Button(self, pos, size, color))
                self.tilemap.tilemap.pop(tile_pos)
            elif tile['type'].startswith('door_'):
                color = tile['type'].split('_')[1]
                self.doors.append(Door(self, pos, size, color))
                self.tilemap.tilemap.pop(tile_pos)

    def fade(self, direction='in'):
        fade = pygame.Surface(self.display.get_size())
        fade.fill((0, 0, 0))

        if direction == 'in':
            alpha_range = range(0, 255, 10)
        elif direction == 'out':
            alpha_range = range(255, 0, -10)
        else:
            return

        for alpha in alpha_range:
            self.display.blit(self.assets['background'], (0, 0))
            self.tilemap.render(self.display)
            for button in self.buttons:
                button.render(self.display)
            for door in self.doors:
                door.render(self.display)
            for enemy in self.enemies:
                enemy.render(self.display)
            self.player.render(self.display)
            for box in self.boxes:
                box.render(self.display)
            fade.set_alpha(alpha)
            self.display.blit(fade, (0, 0))
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

    def restart_level(self):
        self.fade('in')
        self.load_level(self.level)
        self.fade('out')

    def next_level(self):
        self.fade('in')
        self.level += 1
        if self.level >= 20:
            pygame.quit()
            exit()
        self.load_level(self.level)
        self.fade('out')

    def run(self):
        while True:
            self.display.blit((self.assets['background']), (0, 0))
            self.tilemap.render(self.display)

            for button in self.buttons:
                button.update()
                button.render(self.display)
            for door in self.doors:
                door.update()
                door.render(self.display)
            for enemy in self.enemies:
                enemy.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                enemy.render(self.display)
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display)
            for box in self.boxes:
                box.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                box.render(self.display)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        self.player.jump()
                    if event.key == pygame.K_r:
                        self.restart_level()
                    if event.key == pygame.K_m:
                        if self.music_on:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                        self.music_on = not self.music_on
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            self.screen.blit(pygame.font.SysFont(None, 64).render(f'{self.level + 1}', True, (70, 130, 180)),
                             (900, 10))
            pygame.display.update()
            self.clock.tick(60)


Game().run()
