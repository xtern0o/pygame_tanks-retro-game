import sys
import os
import pygame as pg
import random
from constants import *


pg.init()
size = w, h = 800, 600
FPS = 60


def load_image(name):
    fullname = os.path.join('data/images', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    return image


def terminate():
    pg.quit()
    sys.exit()


all_sprites = pg.sprite.Group()
tanks_group = pg.sprite.Group()     # ClassicTank
enemies_group = pg.sprite.Group()   # ClassicEnemy
player_group = pg.sprite.Group()    # ClassicPlayer
wall_group = pg.sprite.Group()      # Wall
bullet_group = pg.sprite.Group()    # ClassicBullet

images = {
    "classic_tank_up": load_image("classic_tank.png"),
    "classic_tank_down": pg.transform.flip(load_image("classic_tank.png"), False, True),
    "classic_tank_right": pg.transform.rotate(load_image("classic_tank.png"), -90),
    "classic_tank_left": pg.transform.flip(pg.transform.rotate(load_image("classic_tank.png"), -90), True, False),

    "bullet_right": load_image("classic_bullet.png"),
    "bullet_left": pg.transform.flip(load_image("classic_bullet.png"), True, False),
    "bullet_up": pg.transform.rotate(load_image("classic_bullet.png"), 90),
    "bullet_down": pg.transform.flip(pg.transform.rotate(load_image("classic_bullet.png"), 90), False, True)
}
tank_width = tank_height = 50

BLACK = pg.Color("black")
WHITE = pg.Color("white")


class ClassicTank(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y, group):
        super().__init__(all_sprites, group)

        self.speed = 3
        self.dmg = 20
        self.hp = 100
        self.direction = DIRECTION_UP

        self.shoot_sound = pg.mixer.Sound("data/sounds/classic_tank_shoot.mp3")

        self.reload = 2
        self.reload *= FPS
        self.reload_timer = 0
        self.is_reloaded = True

        self.image = images["classic_tank" + self.direction]
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def shoot(self):
        # TODO: particles
        if self.is_reloaded:
            bullet = ClassicBullet(self)
            self.shoot_sound.play()
            self.is_reloaded = False

    def update(self, *args):
        if self.hp <= 0:
            self.kill_tank()
        if not self.is_reloaded:
            if self.reload_timer < self.reload:
                self.reload_timer += 1
            else:
                self.reload_timer = 0
                self.is_reloaded = True

    def kill_tank(self):
        # TODO: particles
        self.kill()


class ClassicPlayer(ClassicTank):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, player_group)

    def update(self, *args):
        super().update(*args)
        if args:
            if args[0][pg.K_SPACE]:
                self.shoot()

            if args[0][pg.K_UP] or args[0][pg.K_w]:
                self.rect = self.rect.move(0, -self.speed)
                self.direction = DIRECTION_UP
                if pg.sprite.spritecollideany(self, wall_group) or pg.sprite.spritecollideany(self, enemies_group):
                    self.rect = self.rect.move(0, self.speed)
            elif args[0][pg.K_DOWN] or args[0][pg.K_s]:
                self.rect = self.rect.move(0, self.speed)
                self.direction = DIRECTION_DOWN
                if pg.sprite.spritecollideany(self, wall_group) or pg.sprite.spritecollideany(self, enemies_group):
                    self.rect = self.rect.move(0, -self.speed)
            elif args[0][pg.K_LEFT] or args[0][pg.K_a]:
                self.rect = self.rect.move(-self.speed, 0)
                self.direction = DIRECTION_LEFT
                if pg.sprite.spritecollideany(self, wall_group) or pg.sprite.spritecollideany(self, enemies_group):
                    self.rect = self.rect.move(self.speed, 0)
            elif args[0][pg.K_RIGHT] or args[0][pg.K_d]:
                self.rect = self.rect.move(self.speed, 0)
                self.direction = DIRECTION_RIGHT
                if pg.sprite.spritecollideany(self, wall_group) or pg.sprite.spritecollideany(self, enemies_group):
                    self.rect = self.rect.move(-self.speed, 0)
            self.image = images["classic_tank" + self.direction]
            self.image.get_rect().center = self.rect.center


class ClassicBullet(pg.sprite.Sprite):
    def __init__(self, owner: ClassicTank):
        super().__init__(all_sprites, bullet_group)
        self.owner = owner

        self.speed = 10
        self.distance = 500
        self.damage = self.owner.dmg
        self.direction = self.owner.direction
        self.image = images["bullet" + self.direction]
        self.rect = self.image.get_rect()
        if self.direction == DIRECTION_UP:
            self.rect.midbottom = self.owner.rect.midtop
        elif self.direction == DIRECTION_RIGHT:
            self.rect.midleft = self.owner.rect.midright
        elif self.direction == DIRECTION_LEFT:
            self.rect.midright = self.owner.rect.midleft
        elif self.direction == DIRECTION_DOWN:
            self.rect.midtop = self.owner.rect.midbottom

    def update(self):
        if self.distance > 0:
            if self.direction == DIRECTION_UP:
                self.rect = self.rect.move(0, -self.speed)
            elif self.direction == DIRECTION_DOWN:
                self.rect = self.rect.move(0, self.speed)
            elif self.direction == DIRECTION_RIGHT:
                self.rect = self.rect.move(self.speed, 0)
            elif self.direction == DIRECTION_LEFT:
                self.rect = self.rect.move(-self.speed, 0)

            hits = pg.sprite.groupcollide(enemies_group, bullet_group, False, True)
            for tank in hits:
                tank.hp -= self.damage
                # TODO: minus hp effect
        else:
            self.kill()
        self.distance -= self.speed


class MapBoard:
    def __init__(self, width, height, left=0, top=0, cell_size=40, color=pg.Color("#1F2310")):
        self.width = width
        self.height = height
        self.board = [[random.randint(0, 1) for _ in range(width)] for __ in range(height)]
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.border_color = color

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                lt = (self.left + x * self.cell_size, self.top + y * self.cell_size)
                pg.draw.rect(screen, self.border_color, (lt, (self.cell_size, self.cell_size)), 1)


screen = pg.display.set_mode(size)
screen.fill(BLACK)
pg.display.set_caption("Tanks Retro Game")

map = MapBoard(20, 15)

player = ClassicPlayer(30, 30)
enemy1 = ClassicTank(100, 100, enemies_group)
enemy2 = ClassicTank(500, 500, player_group)

clock = pg.time.Clock()

while True:
    screen.fill(BLACK)
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            terminate()

    keys_pressed = pg.key.get_pressed()
    if keys_pressed[pg.K_ESCAPE]:
        terminate()
    player.update(keys_pressed)

    map.render(screen)

    all_sprites.draw(screen)
    all_sprites.update()
    pg.display.flip()
