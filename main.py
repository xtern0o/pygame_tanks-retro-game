import sys
import os
import pygame as pg
import random

from constants import *
from config import *

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
tanks_group = pg.sprite.Group()     # ClassicTank
enemies_group = pg.sprite.Group()   # ClassicTankEnemy
player_group = pg.sprite.Group()    # ClassicTankPlayer
wall_group = pg.sprite.Group()      # BrickWall
bullet_group = pg.sprite.Group()    # ClassicBullet
booster_group = pg.sprite.Group()   # Booster
mine_group = pg.sprite.Group()      # Mine
border_group = pg.sprite.Group()    # Border

images = {
    "classic_tank_up": load_image("classic_tank.png"),
    "classic_tank_down": pg.transform.flip(load_image("classic_tank.png"), False, True),
    "classic_tank_right": pg.transform.rotate(load_image("classic_tank.png"), -90),
    "classic_tank_left": pg.transform.flip(pg.transform.rotate(load_image("classic_tank.png"), -90), True, False),

    "bullet_right": load_image("classic_bullet.png"),
    "bullet_left": pg.transform.flip(load_image("classic_bullet.png"), True, False),
    "bullet_up": pg.transform.rotate(load_image("classic_bullet.png"), 90),
    "bullet_down": pg.transform.flip(pg.transform.rotate(load_image("classic_bullet.png"), 90), False, True),

    "bul_part_right": load_image("classic_bullet_particle.png"),
    "bul_part_left": load_image("classic_bullet_particle.png"),
    "bul_part_up": pg.transform.rotate(load_image("classic_bullet_particle.png"), 90),
    "bul_part_down": pg.transform.rotate(load_image("classic_bullet_particle.png"), 90),

    "fire_part_right": load_image("fire_particle.png"),
    "fire_part_left": load_image("fire_particle.png"),
    "fire_part_up": pg.transform.rotate(load_image("fire_particle.png"), 90),
    "fire_part_down": pg.transform.rotate(load_image("fire_particle.png"), 90)

}

BLACK = pg.Color("black")
WHITE = pg.Color("white")
SOFT_GOLD = pg.Color("#CCAF5B")
ORANGE = pg.Color("orange")
RED = pg.Color("red")
DARKGREEN = pg.Color("darkgreen")
GREEN = pg.Color("green")
YELLOW = pg.Color("yellow")
DARKRED = pg.Color("darkred")
BROWN = pg.Color("brown")
GRAY = pg.Color("gray")


class ClassicTank(pg.sprite.Sprite):
    shoot_sound = pg.mixer.Sound("data/sounds/classic_tank_shoot.mp3")
    shoot_sound.set_volume(0.1)
    kill_sound = pg.mixer.Sound("data/sounds/tank_boom.mp3")
    kill_sound.set_volume(0.1)
    font = pg.font.Font(None, 30)

    def __init__(self, pos_x, pos_y, group, enemy_group: pg.sprite.Group):
        super().__init__(all_sprites, group, tanks_group)

        self.objectname = "ClassicTank"
        self.killed = False

        self.enemy_group = enemy_group
        self.group = group

        self.speed = CLASSIC_TANK_CFG["speed"]
        self.dmg = CLASSIC_TANK_CFG["damage"]
        self.hp = CLASSIC_TANK_CFG["hp"]
        self.direction = DIRECTION_UP

        self.reload = CLASSIC_TANK_CFG["reload"]
        self.reload *= FPS
        self.reload_timer = 0
        self.is_reloaded = True
        self.fire_distance = CLASSIC_TANK_CFG["fire_distance"]

        self.image = images["classic_tank" + self.direction]
        self.rect = self.image.get_rect().move(pos_x, pos_y)

        self.boosters = {}
        self.boosters_activated = {SPEED_BOOSTER: False,
                                   DAMAGE_BOOSTER: False,
                                   ARMOR_BOOSTER: False}

    def shoot(self):
        if self.is_reloaded:
            for _ in range(self.dmg * 2):
                FireParticle(self)
            ClassicTank.shoot_sound.play()
            self.is_reloaded = False
            ClassicBullet(self)

    def update(self, *args):
        if self.hp > CLASSIC_TANK_CFG["hp"] * 2 / 3:
            color = SOFT_GOLD
        elif self.hp >= CLASSIC_TANK_CFG["hp"] / 3:
            color = ORANGE
        else:
            color = RED
        pg.draw.rect(screen, color, pg.Rect(self.rect.left - 5, self.rect.top - 20, 50, 10), width=2)
        if not self.boosters_activated[ARMOR_BOOSTER]:
            pg.draw.rect(screen, color,
                         pg.Rect(self.rect.left - 5, self.rect.top - 20, 50 * self.hp // CLASSIC_TANK_CFG["hp"], 10))
        else:
            pg.draw.rect(screen, color,
                         pg.Rect(self.rect.left - 5, self.rect.top - 20, 50 * self.hp // (CLASSIC_TANK_CFG["hp"] * 2),
                                 10))

        if self.hp <= 0:
            self.kill_tank()
        if not self.is_reloaded:
            if self.reload_timer < self.reload:
                self.reload_timer += 1
            else:
                self.reload_timer = 0
                self.is_reloaded = True

        to_pop = []
        for booster in self.boosters.keys():
            if self.boosters[booster] <= 0 and self.boosters_activated[booster]:
                self.boosters_activated[booster] = False
                if booster == SPEED_BOOSTER:
                    self.speed = CLASSIC_TANK_CFG["speed"]
                elif booster == DAMAGE_BOOSTER:
                    self.dmg = CLASSIC_TANK_CFG["damage"]
                elif booster == ARMOR_BOOSTER:
                    self.hp = self.hp // 2
                to_pop.append(booster)
            else:
                self.boosters[booster] -= 1

        for booster_to_pop in to_pop:
            self.boosters.pop(booster_to_pop)

        if self.boosters_activated[SPEED_BOOSTER]:
            pass

    def kill_tank(self):
        particle_count = 5
        velocities_x = range(-5, 6)
        velocities_y = range(-20, -5)
        for _ in range(particle_count):
            ParticleKilledTank((self.rect.centerx, self.rect.centery),
                               random.choice(velocities_x), random.choice(velocities_y))


        ClassicTank.kill_sound.play()
        self.killed = True
        self.kill()

    def activate_booster(self, booster):
        if booster.booster_type != HEALTH_BOOSTER:
            self.boosters[booster.booster_type] = BOOSTERS_CFG[f"{booster.booster_type}_time"]
            self.boosters_activated[booster.booster_type] = True
            if booster.booster_type == SPEED_BOOSTER:
                self.speed = CLASSIC_TANK_CFG["speed"] * 2
            elif booster.booster_type == DAMAGE_BOOSTER:
                self.dmg = CLASSIC_TANK_CFG["damage"] * 2
            elif booster.booster_type == ARMOR_BOOSTER:
                self.hp = CLASSIC_TANK_CFG["hp"] * 2

        else:
            self.hp = self.hp + BOOSTERS_CFG["hb_healing"]
            if self.boosters_activated[ARMOR_BOOSTER]:
                if self.hp > CLASSIC_TANK_CFG["hp"] * 2:
                    self.hp = CLASSIC_TANK_CFG["hp"] * 2
            else:
                if self.hp > CLASSIC_TANK_CFG["hp"]:
                    self.hp = CLASSIC_TANK_CFG["hp"]


class ClassicTankPlayer(ClassicTank):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, player_group, enemies_group)

        self.objectname = NICKNAME

    def update(self, *args):
        if not self.killed:
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
        else:
            pass

    def kill_tank(self):
        super().kill_tank()
        self.killed = True
        pg.display.set_caption("GAME OVER")


class ClassicTankBot(ClassicTank):
    def __init__(self, pos_x, pos_y, group, group_to_kill, speed=3):
        super().__init__(pos_x, pos_y, group, group_to_kill)
        self.objectname = "bot"
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
                        if target_y - self.rect.centery > self.fire_distance:
                            self.direction = DIRECTION_DOWN
                            if not pg.sprite.spritecollideany(self, self.group_to_kill):
                                self.rect = self.rect.move(0, self.speed)
                        elif target_y - self.rect.centery < -self.fire_distance:
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
                        if target_x - self.rect.centerx > self.fire_distance:
                            self.direction = DIRECTION_RIGHT
                            if not pg.sprite.spritecollideany(self, self.group_to_kill):
                                self.rect = self.rect.move(self.speed, 0)
                        elif target_x - self.rect.centerx < -self.fire_distance:
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
    tank_hit_sound.set_volume(0.3)

    def __init__(self, owner: ClassicTank):
        super().__init__(all_sprites, bullet_group)
        self.owner = owner

        self.speed = CLASSIC_BULLET_CFG["speed"]
        self.distance = owner.fire_distance
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
                if self.owner.group != tank.group:
                    tank.hp -= self.damage
                    ClassicBullet.tank_hit_sound.play()
                    ParticleHitTank(self.rect.center, self.damage)

            hits = pg.sprite.groupcollide(wall_group, bullet_group, False, True)
            for wall in hits:
                wall: BrickWall
                wall.hp -= self.damage

                ParticleHitBrick(self.rect.center, random.choice(range(-5, 6)), random.choice(range(-20, -10)))
            ClassicBulletParticle(self)
        else:
            for _ in range(20):
                ClassicBulletParticle(self)
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
        self.time = 60
        self.current_time = 60

    def update(self):
        if self.current_time > 0:
            self.current_time -= 1
            self.image.set_alpha(255 * self.current_time // self.time)
            self.velocity[1] += self.accel
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
        else:
            self.kill()


class FlyingParticle(pg.sprite.Sprite):
    def __init__(self, pos, image: pg.Surface, time: float, velocity=(1, -1)):
        super().__init__(all_sprites)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

        self.time = time * FPS
        self.current_time = self.time

        self.velocity = velocity

    def update(self):
        self.image.set_alpha(255 * self.current_time // self.time)
        if self.current_time >= 0:
            self.rect = self.rect.move(*self.velocity)
            self.current_time -= 1
        else:
            self.kill()


class ParticleKilledTank(GravityParticle):
    def __init__(self, pos, dx, dy):
        super().__init__(pos, dx, dy, 1, pg.transform.scale(load_image("gear.png"), (30, 30)))


class ParticleHitTank(FlyingParticle):
    def __init__(self, pos, damage):
        self.font = pg.font.Font(None, 40)
        hp_text = self.font.render("-" + str(damage), True, SOFT_GOLD)
        super().__init__(pos, hp_text, 1, (random.randint(-2, 3), random.randint(-2, 3)))


class ParticleHitBrick(GravityParticle):
    def __init__(self, pos, dx, dy):
        super().__init__(pos, dx, dy, 1, load_image("brick_particle.png"))


class ClassicBulletParticle(pg.sprite.Sprite):
    def __init__(self, bullet: ClassicBullet):
        super().__init__(all_sprites)
        self.image = images["bul_part" + bullet.direction]
        self.time = 5
        self.rect = self.image.get_rect()
        self.velocity = []
        if bullet.direction == DIRECTION_UP:
            self.rect.midtop = bullet.rect.midbottom
            self.velocity = [random.randint(-1, 2), random.randint(-9, -6)]
        elif bullet.direction == DIRECTION_DOWN:
            self.rect.midbottom = bullet.rect.midtop
            self.velocity = [random.randint(-1, 2), random.randint(5, 10)]
        elif bullet.direction == DIRECTION_RIGHT:
            self.rect.midright = bullet.rect.midleft
            self.velocity = [random.randint(5, 10), random.randint(-1, 2)]
        elif bullet.direction == DIRECTION_LEFT:
            self.rect.midleft = bullet.rect.midright
            self.velocity = [random.randint(-9, -6), random.randint(-1, 2)]

    def update(self):
        self.image.set_alpha(255 * self.time // 10)
        if self.time:
            self.time -= 1
            self.rect = self.rect.move(*self.velocity)
        else:
            self.kill()


class FireParticle(pg.sprite.Sprite):
    def __init__(self, tank: ClassicTank):
        super().__init__(all_sprites)
        self.image = images["fire_part" + tank.direction]
        self.time = 12
        self.rect = self.image.get_rect()
        self.velocity = []
        if tank.direction == DIRECTION_DOWN:
            self.rect.midtop = tank.rect.midbottom
            self.velocity = [random.randint(-3, 4), random.randint(4, 7)]
        elif tank.direction == DIRECTION_UP:
            self.rect.midbottom = tank.rect.midtop
            self.velocity = [random.randint(-3, 4), random.randint(-6, -3)]
        elif tank.direction == DIRECTION_LEFT:
            self.rect.midright = tank.rect.midleft
            self.velocity = [random.randint(-6, -3), random.randint(-3, 4)]
        elif tank.direction == DIRECTION_RIGHT:
            self.rect.midleft = tank.rect.midright
            self.velocity = [random.randint(4, 7), random.randint(-3, 4)]

    def update(self):
        self.image.set_alpha(255 * self.time // 10)
        if self.time:
            self.time -= 1
            self.rect = self.rect.move(*self.velocity)
        else:
            self.kill()


class BrickWall(pg.sprite.Sprite):
    images = [load_image(f"brickwall_{i}.png") for i in range(4)]
    brick_hit_sound = pg.mixer.Sound("data/sounds/brick_hit_sound.mp3")
    brick_hit_sound.set_volume(0.1)

    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, wall_group)
        self.image = BrickWall.images[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery = pos_y

        self.hp = 40

    def update(self):
        if 20 < self.hp <= 30:
            self.image = BrickWall.images[1]
        elif 10 < self.hp <= 20:
            self.image = BrickWall.images[2]
        elif 0 < self.hp <= 10:
            self.image = BrickWall.images[3]
        elif self.hp <= 0:
            BrickWall.brick_hit_sound.play()
            self.break_wall()

    def break_wall(self):
        self.kill()


class Booster(pg.sprite.Sprite):
    activation_sound = pg.mixer.Sound("data/sounds/activation.mp3")

    def __init__(self, image, booster_type, time, pos_x, pos_y):
        super().__init__(booster_group, all_sprites)
        self.image = image
        self.booster_type = booster_type
        self.time = time
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)
        self.time_before_remove = BOOSTERS_CFG["time_before_remove"]

        self.font = pg.font.Font(None, 20)
        self.hp_rect = self.rect.copy().move(0, -20)
        self.time_to_fly = 120

    def update(self):
        if self.time_before_remove:
            hp_text = self.font.render(str(self.time_before_remove), True, SOFT_GOLD)
            screen.blit(hp_text, self.hp_rect)
            self.time_before_remove -= 1
            collides = pg.sprite.groupcollide(tanks_group, booster_group, False, True)
            for tank in collides:
                tank: ClassicTank
                Booster.activation_sound.play()
                tank.activate_booster(self)
                print(self.booster_type)
        else:
            self.image.set_alpha(255 * self.time_to_fly // 120)
            self.rect = self.rect.move(0, -1)
            self.hp_rect = self.hp_rect.move(0, -1)

            self.time_to_fly -= 1
            hp_text = self.font.render("~" + str(self.time_to_fly), True, RED)
            screen.blit(hp_text, self.hp_rect)
            if self.time_to_fly <= 0:
                self.kill()


class SpeedBooster(Booster):
    def __init__(self, pos_x, pos_y):
        super().__init__(load_image("speed_booster.png"), SPEED_BOOSTER, BOOSTERS_CFG["sb_time"], pos_x, pos_y)


class DamageBooster(Booster):
    def __init__(self, pos_x, pos_y):
        super().__init__(load_image("damage_booster.png"), DAMAGE_BOOSTER, BOOSTERS_CFG["db_time"], pos_x, pos_y)


class ArmorBooster(Booster):
    def __init__(self, pos_x, pos_y):
        super().__init__(load_image("armor_booster.png"), ARMOR_BOOSTER, BOOSTERS_CFG["ab_time"], pos_x, pos_y)


class HealthBooster(Booster):
    def __init__(self, pos_x, pos_y):
        super().__init__(load_image("health_booster.png"), HEALTH_BOOSTER, 0, pos_x, pos_y)


class MapBoard:
    def __init__(self, width, height, left=50, top=50, cell_size=50, color=pg.Color("#1F2310")):
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

    def get_cell_center(self, x, y):
        """Метод, возвращающий центр клетки координат (x, y) на карте"""
        return (self.left + self.cell_size // 2 + x * self.cell_size,
                self.top + self.cell_size // 2 + y * self.cell_size)


class InterfaceForClassicTank:
    font = pg.font.Font("data/font/ARCADE_N.TTF", 15)

    def __init__(self, tank: ClassicTank):
        self.tank = tank
        self.hp_rect = pg.Rect(710, 635, 100, 30)
        self.reload_rect = pg.Rect(710, 660, 100, 30)

        self.sp_b_rect = pg.Rect(50 * (1 + 5) + 10, 610, 80, 10)
        self.ar_b_rect = pg.Rect(50 * (1 + 7) + 10, 610, 80, 10)
        self.dd_b_rect = pg.Rect(50 * (1 + 9) + 10, 610, 80, 10)

        self.name_rect = pg.Rect(50 * (1 + 5), 570, 400, 30)

        self.dmg_rect = pg.Rect(50, 600, 100, 30)
        self.distance_rect = pg.Rect(50, 630, 100, 30)
        self.speed_rect = pg.Rect(50, 660, 100, 30)

    def update(self):
        pg.draw.circle(screen, GRAY, self.tank.rect.center, 20)

        pg.draw.rect(screen, SOFT_GOLD, pg.Rect(50 * (1 + 5), 600, 400, 30), border_radius=5, width=3)
        pg.draw.rect(screen, DARKRED, pg.Rect(50 * (1 + 5), 640, 400, 15), border_radius=3, width=2)
        pg.draw.rect(screen, YELLOW, pg.Rect(50 * (1 + 5), 665, 400, 15), border_radius=3, width=2)
        if isinstance(self.tank, ClassicTankPlayer):
            InterfaceForClassicTank.font.underline = True
            InterfaceForClassicTank.font.bold = True
        if not self.tank.killed:
            screen.blit(InterfaceForClassicTank.font.render(self.tank.objectname, True, SOFT_GOLD), self.name_rect)
        else:
            screen.blit(InterfaceForClassicTank.font.render(self.tank.objectname + " (killed)", True, DARKRED),
                        self.name_rect)
        InterfaceForClassicTank.font.underline = False
        InterfaceForClassicTank.font.bold = False

        if not self.tank.boosters_activated[ARMOR_BOOSTER]:
            pg.draw.rect(screen, DARKRED, pg.Rect(50 * (1 + 5), 640, 400 * self.tank.hp // CLASSIC_TANK_CFG["hp"], 15),
                     border_radius=3)
        else:
            pg.draw.rect(screen, DARKRED, pg.Rect(50 * (1 + 5), 640, 400 * self.tank.hp // (CLASSIC_TANK_CFG["hp"] * 2),
                                                  15), border_radius=3)
        screen.blit(InterfaceForClassicTank.font.render(f"{self.tank.hp / CLASSIC_TANK_CFG['hp'] * 100}%",
                                                        True, DARKRED), self.hp_rect)

        if not self.tank.is_reloaded:
            pg.draw.rect(screen, YELLOW, pg.Rect(50 * (1 + 5), 665,
                        400 * self.tank.reload_timer // self.tank.reload, 15), border_radius=3)
            screen.blit(InterfaceForClassicTank.font.render(f"{((self.tank.reload - self.tank.reload_timer) / 60):0.2f}",
                                                            True, YELLOW), self.reload_rect)
        else:
            pg.draw.rect(screen, YELLOW, pg.Rect(50 * (1 + 5), 665, 400, 15), border_radius=3)

        if self.tank.boosters_activated[SPEED_BOOSTER]:
            pg.draw.rect(screen, YELLOW, self.sp_b_rect, border_radius=3)
        if self.tank.boosters_activated[ARMOR_BOOSTER]:
            pg.draw.rect(screen, BROWN, self.ar_b_rect, border_radius=3)
        if self.tank.boosters_activated[DAMAGE_BOOSTER]:
            pg.draw.rect(screen, RED, self.dd_b_rect, border_radius=3)

        screen.blit(InterfaceForClassicTank.font.render(f"Damage:     {self.tank.dmg}", True, SOFT_GOLD),
                    self.dmg_rect)
        screen.blit(InterfaceForClassicTank.font.render(f"Fire range: {self.tank.fire_distance}", True, SOFT_GOLD),
                    self.distance_rect)
        screen.blit(InterfaceForClassicTank.font.render(f"Speed:      {self.tank.speed}", True, SOFT_GOLD),
                    self.speed_rect)


screen = pg.display.set_mode(SIZE)
screen.fill(BLACK)
pg.display.set_caption("Tanks Retro Game")

map_board = MapBoard(16, 10)
player = ClassicTankPlayer(30, 30)
enemybot = ClassicTankBot(500, 500, enemies_group, player_group, speed=2)
teammatebot = ClassicTankBot(200, 50, player_group, enemies_group)
wall1 = BrickWall(*map_board.get_cell_center(2, 5))
wall2 = BrickWall(*map_board.get_cell_center(2, 6))
wall3 = BrickWall(*map_board.get_cell_center(3, 5))
wall4 = BrickWall(*map_board.get_cell_center(5, 5))
dambooster = DamageBooster(*map_board.get_cell_center(9, 1))
spebooster = SpeedBooster(*map_board.get_cell_center(10, 1))
armbooster = ArmorBooster(*map_board.get_cell_center(11, 1))
heabooster = HealthBooster(*map_board.get_cell_center(12, 1))

interface = InterfaceForClassicTank(player)
clock = pg.time.Clock()
while True:
    screen.fill(BLACK)
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            terminate()
        if event.type == pg.MOUSEBUTTONDOWN:
            x, y = event.pos
            for tank in tanks_group.sprites():
                if tank.rect.left <= x <= tank.rect.right and tank.rect.top <= y <= tank.rect.bottom:
                    interface = InterfaceForClassicTank(tank)
                    for _ in range(30):
                        FlyingParticle((x, y), load_image("fire_particle.png"), 1,
                                       (random.randint(-5, 6), random.randint(-5, 6)))

    keys_pressed = pg.key.get_pressed()
    if keys_pressed[pg.K_ESCAPE]:
        terminate()
    player.update(keys_pressed)
    map_board.render(screen)

    interface.update()
    all_sprites.draw(screen)
    all_sprites.update()

    pg.display.flip()
