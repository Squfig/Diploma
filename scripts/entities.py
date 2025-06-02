import pygame


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        frame_movement = [movement[0] + self.velocity[0], movement[1] + self.velocity[1]]

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                elif frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                elif frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

    def render(self, surf):
        surf.blit(self.game.assets[self.type], self.pos)


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.size = size
        self.jumps = 0

    def update(self, tilemap, movement=(0, 0)):
        dx = movement[0]
        future_rect = self.rect().move(dx, 0)

        for box in self.game.boxes:
            if future_rect.colliderect(box.rect()):
                if not box.try_push(dx):
                    dx = 0
                    break

        for door in self.game.doors:
            if not door.open and future_rect.colliderect(door.rect()):
                dx = 0
                break

        super().update(tilemap, movement=(dx, 0))

        entity_rect = self.rect()
        for box in self.game.boxes:
            if entity_rect.colliderect(box.rect()):
                if self.velocity[1] > 0:
                    entity_rect.bottom = box.rect().top
                    self.collisions['down'] = True
                elif self.velocity[1] < 0:
                    entity_rect.top = box.rect().bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        for door in self.game.doors:
            if not door.open and entity_rect.colliderect(door.rect()):
                if self.velocity[1] > 0:
                    entity_rect.bottom = door.rect().top
                    self.collisions['down'] = True
                elif self.velocity[1] < 0:
                    entity_rect.top = door.rect().bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        if self.collisions['down']:
            self.jumps = 1

        player_rect = self.rect()
        for tile in tilemap.tiles_around(self.pos):
            tile_rect = pygame.Rect(
                tile['pos'][0] * tilemap.tile_size,
                tile['pos'][1] * tilemap.tile_size,
                tilemap.tile_size,
                tilemap.tile_size * 2 if tile['type'] == 'exit' else tilemap.tile_size
            )
            if player_rect.colliderect(tile_rect):
                if tile['type'] == 'spikes':
                    self.game.restart_level()
                    break
                elif tile['type'] == 'exit':
                    self.game.next_level()

        for enemy in self.game.enemies:
            if self.rect().colliderect(enemy.rect()):
                self.game.restart_level()

    def jump(self):
        if self.jumps:
            self.velocity[1] = -3.04
            self.jumps = 0


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)
        self.direction = 1

    def update(self, tilemap, movement=(0, 0)):
        future_rect = self.rect().move(self.direction, 0)
        for box in self.game.boxes:
            if future_rect.colliderect(box.rect()):
                if not box.try_push(self.direction):
                    self.direction *= -1
                    return

        for enemy in self.game.enemies:
            if enemy is not self and future_rect.colliderect(enemy.rect()):
                self.direction *= -1
                return

        for door in self.game.doors:
            if not door.open and future_rect.colliderect(door.rect()):
                self.direction *= -1
                return

        super().update(tilemap, (self.direction, 0))

        entity_rect = self.rect()
        for other in self.game.boxes + self.game.enemies:
            if other is not self and entity_rect.colliderect(other.rect()):
                if self.velocity[1] > 0:
                    entity_rect.bottom = other.rect().top
                    self.collisions['down'] = True
                elif self.velocity[1] < 0:
                    entity_rect.top = other.rect().bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        for door in self.game.doors:
            if not door.open and entity_rect.colliderect(door.rect()):
                if self.velocity[1] > 0:
                    entity_rect.bottom = door.rect().top
                    self.collisions['down'] = True
                elif self.velocity[1] < 0:
                    entity_rect.top = door.rect().bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        if self.collisions['left'] or self.collisions['right']:
            self.direction *= -1


class Box(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'box', pos, size)

    def try_push(self, dx):
        future_rect = self.rect().move(dx, 0)

        for entity in self.game.boxes + self.game.enemies + [self.game.player]:
            if entity is not self and future_rect.colliderect(entity.rect()):
                return False

        for door in self.game.doors:
            if not door.open and future_rect.colliderect(door.rect()):
                return False

        for rect in self.game.tilemap.physics_rects_around((future_rect.x, future_rect.y)):
            if future_rect.colliderect(rect):
                return False

        self.pos[0] += dx
        return True

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=(0, 0))

        entity_rect = self.rect()
        for other in self.game.boxes + [self.game.player] + self.game.enemies:
            if other is not self and entity_rect.colliderect(other.rect()):
                if self.velocity[1] > 0:
                    entity_rect.bottom = other.rect().top
                    self.collisions['down'] = True
                elif self.velocity[1] < 0:
                    entity_rect.top = other.rect().bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        for door in self.game.doors:
            if not door.open and entity_rect.colliderect(door.rect()):
                if self.velocity[1] > 0:
                    entity_rect.bottom = door.rect().top
                    self.collisions['down'] = True
                elif self.velocity[1] < 0:
                    entity_rect.top = door.rect().bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0


class Button:
    def __init__(self, game, pos, size, color='red'):
        self.game = game
        self.color = color
        self.pos = list(pos)
        self.size = size
        self.pressed = False

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1] + self.size[1] // 2, self.size[0], self.size[1] // 2)

    def update(self):
        self.pressed = any(
            self.rect().colliderect(entity.rect())
            for entity in [self.game.player] + self.game.boxes + self.game.enemies
        )

    def render(self, surf):
        sprite = f'button_{self.color}_pressed' if self.pressed else f'button_{self.color}'
        surf.blit(self.game.assets[sprite], self.pos)


class Door:
    def __init__(self, game, pos, size, color='red'):
        self.game = game
        self.color = color
        self.pos = list(pos)
        self.size = size
        self.open = False

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self):
        self.open = any(button.color == self.color and button.pressed for button in self.game.buttons)

    def render(self, surf):
        sprite = f'door_{self.color}_open' if self.open else f'door_{self.color}'
        surf.blit(self.game.assets[sprite], self.pos)
