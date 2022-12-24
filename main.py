import sys
import os
import pygame as pg
import random
from constants import *

pg.init()


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
tanks_group = pg.sprite.Group()  # ClassicTank
enemies_group = pg.sprite.Group()  # ClassicEnemy
player_group = pg.sprite.Group()  # ClassicPlayer
wall_group = pg.sprite.Group()  # BrickWall
bullet_group = pg.sprite.Group()  # ClassicBullet
borders_group = pg.sprite.Group()  # Border
booster_group = pg.sprite.Group()  # Booster

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

BLACK = pg.Color("black")
WHITE = pg.Color("white")
SOFT_GOLD = pg.Color("#CCAF5B")
ORANGE = pg.Color("orange")
RED = pg.Color("red")


class ClassicTank(pg.sprite.Sprite):
    shoot_sound = pg.mixer.Sound("data/sounds/classic_tank_shoot.mp3")
    shoot_sound.set_volume(0.3)
    kill_sound = pg.mixer.Sound("data/sounds/tank_boom.mp3")
    kill_sound.set_volume(0.3)

    def __init__(self, pos_x, pos_y, group, enemy_group: pg.sprite.Group):
        super().__init__(all_sprites, group)

        self.font = pg.font.Font(None, 30)
        self.enemy_group = enemy_group

        self.speed = 3
        self.dmg = 5
        self.hp = 100
        self.direction = DIRECTION_UP

        self.reload = 0.3
        self.reload *= FPS
        self.reload_timer = 0
        self.is_reloaded = True
        self.distance = 500

        self.image = images["classic_tank" + self.direction]
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def shoot(self):
        # TODO: particles
        if self.is_reloaded:
            ClassicTank.shoot_sound.play()
            self.is_reloaded = False
            ClassicBullet(self)

    def update(self, *args):
        if self.hp > 60:
            hp_text = self.font.render(str(self.hp), True, SOFT_GOLD)
        elif self.hp >= 30:
            hp_text = self.font.render(str(self.hp), True, ORANGE)
        else:
            hp_text = self.font.render(str(self.hp), True, RED)
        hp_rect = self.rect.copy()
        hp_rect.y -= 20
        hp_rect.x -= 30
        screen.blit(hp_text, hp_rect)

        if self.hp <= 0:
            self.kill_tank()
        if not self.is_reloaded:
            if self.reload_timer < self.reload:
                self.reload_timer += 1
            else:
                self.reload_timer = 0
                self.is_reloaded = True

    def kill_tank(self):
        particle_count = 5
        velocities_x = range(-5, 6)
        velocities_y = range(-20, -5)
        for _ in range(particle_count):
            ParticleKilledTank((self.rect.centerx, self.rect.centery),
                               random.choice(velocities_x), random.choice(velocities_y))

        ClassicTank.kill_sound.play()
        self.kill()


class ClassicPlayer(ClassicTank):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, player_group, enemies_group)

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


class ClassicBot(ClassicTank):
    def __init__(self, pos_x, pos_y, group, group_to_kill, speed=3):
        super().__init__(pos_x, pos_y, group, group_to_kill)
        self.speed = speed
        self.enemies = []
        self.target = None
        self.coords_to_move = None
        self.group_to_kill = group_to_kill

    def enemy_locator(self):
        self.enemies = []
        for enemy in self.group_to_kill.sprites():
            self.enemies.append(enemy)
        # сортировка всех противников начиная с ближнего
        self.enemies = sorted(self.enemies, key=lambda sprite: (sprite.rect.x ** 2 + sprite.rect.y ** 2) ** 0.5)

    def update(self):
        super().update()
        self.enemy_locator()
        if self.enemies:
            # идем к самому ближайшему
            self.target = self.enemies[0]
            self.target: ClassicTank
            target_x, target_y = self.target.rect.centerx, self.target.rect.centery
            if abs(target_x - self.rect.centerx) < abs(target_y - self.rect.centery):
                if self.rect.centerx != target_x:
                    if target_x - self.rect.centerx > self.speed:
                        self.direction = DIRECTION_RIGHT
                        if not pg.sprite.spritecollideany(self, self.group_to_kill):
                            self.rect = self.rect.move(self.speed, 0)
                    elif target_x - self.rect.centerx < -self.speed:
                        self.direction = DIRECTION_LEFT
                        if not pg.sprite.spritecollideany(self, self.group_to_kill):
                            self.rect = self.rect.move(-self.speed, 0)
                    else:
                        if target_y - self.rect.centery > self.distance:
                            self.direction = DIRECTION_DOWN
                            if not pg.sprite.spritecollideany(self, self.group_to_kill):
                                self.rect = self.rect.move(0, self.speed)
                        elif target_y - self.rect.centery < -self.distance:
                            self.direction = DIRECTION_UP
                            if not pg.sprite.spritecollideany(self, self.group_to_kill):
                                self.rect = self.rect.move(0, -self.speed)
                        else:
                            if target_y < self.rect.centery:
                                self.direction = DIRECTION_UP
                            else:
                                self.direction = DIRECTION_DOWN
                            self.shoot()
            else:
                if self.rect.centery != target_y:
                    if target_y - self.rect.centery > self.speed:
                        self.direction = DIRECTION_DOWN
                        if not pg.sprite.spritecollideany(self, self.group_to_kill):
                            self.rect = self.rect.move(0, self.speed)
                    elif target_y - self.rect.centery < -self.speed:
                        self.direction = DIRECTION_UP
                        if not pg.sprite.spritecollideany(self, self.group_to_kill):
                            self.rect = self.rect.move(0, -self.speed)
                    else:
                        if target_x - self.rect.centerx > self.distance:
                            self.direction = DIRECTION_RIGHT
                            if not pg.sprite.spritecollideany(self, self.group_to_kill):
                                self.rect = self.rect.move(self.speed, 0)
                        elif target_x - self.rect.centerx < -self.distance:
                            self.direction = DIRECTION_LEFT
                            if not pg.sprite.spritecollideany(self, self.group_to_kill):
                                self.rect = self.rect.move(-self.speed, 0)
                        else:
                            if target_x < self.rect.centerx:
                                self.direction = DIRECTION_LEFT
                            else:
                                self.direction = DIRECTION_RIGHT
                            self.shoot()

        self.image = images["classic_tank" + self.direction]
        self.image.get_rect().center = self.rect.center


class ClassicBullet(pg.sprite.Sprite):
    tank_hit_sound = pg.mixer.Sound("data/sounds/hit_sound.mp3")
    tank_hit_sound.set_volume(0.7)

    def __init__(self, owner: ClassicTank):
        super().__init__(all_sprites, bullet_group)
        self.owner = owner

        self.speed = 10
        self.distance = owner.distance
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

            hits = pg.sprite.groupcollide(self.owner.enemy_group, bullet_group, False, True)
            for tank in hits:
                tank: ClassicTank
                tank.hp -= self.damage

                ClassicBullet.tank_hit_sound.play()
                ParticleHitTank(self.rect.center, self.damage)

            hits = pg.sprite.groupcollide(wall_group, bullet_group, False, True)
            for wall in hits:
                wall: BrickWall
                wall.hp -= self.damage

                ParticleHitBrick(self.rect.center, random.choice(range(-5, 6)), random.choice(range(-20, -10)))
        else:
            self.kill()
        self.distance -= self.speed


class GravityParticle(pg.sprite.Sprite):
    def __init__(self, pos, dx, dy, accel, image: pg.Surface):
        super().__init__(all_sprites)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.velocity = [dx, dy]
        self.accel = accel

    def update(self):
        self.velocity[1] += self.accel
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]


class FlyingParticle(pg.sprite.Sprite):
    def __init__(self, pos, image: pg.Surface, time: float, velocity: tuple = (1, -1)):
        super().__init__(all_sprites)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.time = time * FPS
        self.current_time = self.time
        self.velocity = velocity

    def update(self):
        if self.current_time >= 0:
            self.rect = self.rect.move(*self.velocity)
            self.current_time -= 1
        else:
            self.kill()


class ParticleKilledTank(GravityParticle):
    def __init__(self, pos, dx, dy):
        super().__init__(pos, dx, dy, 1, pg.transform.scale(load_image("star.png"), (30, 30)))


class ParticleHitTank(FlyingParticle):
    def __init__(self, pos, damage):
        self.font = pg.font.Font(None, 40)
        hp_text = self.font.render("-" + str(damage), True, SOFT_GOLD)
        super().__init__(pos, hp_text, 1, (random.randint(-2, 3), random.randint(-2, 3)))


class ParticleHitBrick(GravityParticle):
    def __init__(self, pos, dx, dy):
        super().__init__(pos, dx, dy, 1, load_image("brick_particle.png"))


class BrickWall(pg.sprite.Sprite):
    images = [load_image(f"brickwall_{i}.png") for i in range(4)]
    brick_hit_sound = pg.mixer.Sound("data/sounds/brick_hit_sound.mp3")
    brick_hit_sound.set_volume(0.4)

    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, wall_group)
        self.image = BrickWall.images[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery = pos_y

        self.hp = 80

    def update(self):
        if 40 < self.hp <= 60:
            self.image = BrickWall.images[1]
        elif 20 < self.hp <= 40:
            self.image = BrickWall.images[2]
        elif 0 < self.hp <= 20:
            self.image = BrickWall.images[3]
        elif self.hp <= 0:
            BrickWall.brick_hit_sound.play()
            self.break_wall()

    def break_wall(self):
        self.kill()


class MapBoard:
    def __init__(self, width, height, left=0, top=0, cell_size=50, color=pg.Color("#1F2310")):
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


screen = pg.display.set_mode(SIZE)
screen.fill(BLACK)
pg.display.set_caption("Tanks Retro Game")

map_board = MapBoard(16, 12)
player = ClassicPlayer(30, 30)
enemy1 = ClassicTank(100, 100, enemies_group, player_group)
enemybot = ClassicBot(500, 500, enemies_group, player_group, speed=2)
teammatebot = ClassicBot(200, 50, player_group, enemies_group)
wall1 = BrickWall(300, 100)

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
    map_board.render(screen)

    all_sprites.draw(screen)
    all_sprites.update()

    pg.display.flip()
