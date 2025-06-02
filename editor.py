import pygame
import sys


from scripts.utils import load_image
from scripts.tilemap import Tilemap


RENDER_SCALE = 2.0
MAP_LOAD = 19
MAP_SAVE = 19


class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Editor')
        self.screen = pygame.display.set_mode((960, 640))
        self.display = pygame.Surface((480, 320))
        self.clock = pygame.time.Clock()
        self.assets = {
            'exit': load_image('exit.png'),
            'stone': load_image('stone.png'),
            'spikes': load_image('spikes.png'),
            'player': load_image('player.png'),
            'enemy': load_image('enemy.png'),
            'box': load_image('box.png'),
            'button_red': load_image('button_red.png'),
            'door_red': load_image('door_red.png'),
            'button_green': load_image('button_green.png'),
            'door_green': load_image('door_green.png'),
            'button_blue': load_image('button_blue.png'),
            'door_blue': load_image('door_blue.png'),
            'rip': load_image('rip.png'),
            'torch': load_image('torch.png'),
        }
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tilemap = Tilemap(self, tile_size=16)

        try:
            self.tilemap.load('data/maps/' + str(MAP_LOAD) + '.json')
        except FileNotFoundError:
            pass

        self.clicking = False
        self.right_clicking = False
        self.ongrid = True

    def run(self):
        while True:
            self.display.fill((0, 0, 0))
            self.tilemap.render(self.display)

            current_tile_img = self.assets[self.tile_list[self.tile_group]].copy()
            current_tile_img.set_alpha(40)

            m_pos = pygame.mouse.get_pos()
            m_pos = (m_pos[0] / RENDER_SCALE, m_pos[1] / RENDER_SCALE)
            tile_pos = (int(m_pos[0] // self.tilemap.tile_size), int(m_pos[1] // self.tilemap.tile_size))

            if self.ongrid:
                self.display.blit(current_tile_img,
                                  (tile_pos[0] * self.tilemap.tile_size, tile_pos[1] * self.tilemap.tile_size))
            else:
                self.display.blit(current_tile_img, m_pos)

            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {
                    'type': self.tile_list[self.tile_group], 'pos': tile_pos}
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']]
                    tile_r = pygame.Rect(tile['pos'][0], tile['pos'][1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(m_pos):
                        self.tilemap.offgrid_tiles.remove(tile)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'pos': m_pos})
                    if event.button == 3:
                        self.right_clicking = True
                    if event.button == 4:
                        self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                    if event.button == 5:
                        self.tile_group = (self.tile_group + 1) % len(self.tile_list)

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_o:
                        self.tilemap.save('data/maps/' + str(MAP_SAVE) + '.json')

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


Editor().run()
