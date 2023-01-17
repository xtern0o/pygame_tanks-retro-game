import pygame as pg
import random
from math import sin

from source.functions import *
from source.config import *
from source.constants import *


pg.init()

all_sprites = pg.sprite.Group()
tanks_group = pg.sprite.Group()     # ClassicTank
enemies_group = pg.sprite.Group()   # ClassicTankEnemy
player_group = pg.sprite.Group()    # ClassicTankPlayer
wall_group = pg.sprite.Group()      # BrickWall
bullet_group = pg.sprite.Group()    # ClassicBullet
booster_group = pg.sprite.Group()   # Booster
mine_group = pg.sprite.Group()      # Mine
border_group = pg.sprite.Group()    # Border
bash_group = pg.sprite.Group()      # Bash
boom_group = pg.sprite.Group()      # Boom

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
    "fire_part_down": pg.transform.rotate(load_image("fire_particle.png"), 90),

    "artillery_up": load_image("artillery_tank.png"),
    "artillery_down": pg.transform.flip(load_image("artillery_tank.png"), False, True),
    "artillery_right": pg.transform.rotate(load_image("artillery_tank.png"), 90),
    "artillery_left": pg.transform.rotate(load_image("artillery_tank.png"), -90),

}
screen = pg.display.set_mode(SIZE)
screen.fill(BLACK)


class ClassicTank(pg.sprite.Sprite):
    shoot_sound = pg.mixer.Sound("source/data/sounds/classic_tank_shoot.mp3")
    shoot_sound.set_volume(0.1)
    kill_sound = pg.mixer.Sound("source/data/sounds/tank_boom.mp3")
    kill_sound.set_volume(0.1)
    font = pg.font.Font(None, 30)

    def __init__(self, pos_x, pos_y, group, enemy_group: pg.sprite.Group):
        super().__init__(all_sprites, group, tanks_group)

        self.objectname = "ClassicTank"
        self.killed = False
        self.score = 0

        self.mines_count = CLASSIC_TANK_CFG["mines_count"]
        self.mine_reload = CLASSIC_TANK_CFG["mine_reload"] * FPS
        self.mine_reloaded = True
        self.mine_reload_timer = 0

        self.in_bush = False

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
        self.rect = self.image.get_rect()
        self.rect.center = pos_x, pos_y

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
            log(f"{self.objectname} выстрелил", small=True)

    def update(self, *args):
        if self.hp > CLASSIC_TANK_CFG["hp"] * 2 / 3:
            color = SOFT_GOLD
        elif self.hp >= CLASSIC_TANK_CFG["hp"] / 3:
            color = ORANGE
        else:
            color = RED
        if not self.in_bush:
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

        if pg.sprite.spritecollideany(self, bash_group):
            self.in_bush = True
        else:
            self.in_bush = False
        if self.in_bush:
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)

        if not self.mine_reloaded:
            if self.mine_reload_timer < self.mine_reload:
                self.mine_reload_timer += 1
            else:
                self.mine_reload_timer = 0
                self.mine_reloaded = True

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
        log(f"{self.objectname} уничтожен", small=True)

    def activate_booster(self, booster):
        log(f"{self.objectname} активировал бустер: {booster.booster_type}", small=True)
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
            HealingParticle(booster)

    def place_mine(self):
        log(f"{self.objectname} разместил мину по координатам ({self.rect.centerx}, {self.rect.centery})", small=True)
        if self.mines_count and self.mine_reloaded:
            Mine(*self.rect.center, self.group, self.enemy_group, self)
            self.mines_count -= 1
            self.mine_reloaded = False


class ClassicTankPlayer(ClassicTank):
    def __init__(self, pos_x, pos_y):
        self.team = player_group
        self.enemy = enemies_group
        super().__init__(pos_x, pos_y, self.team, self.enemy)
        self.objectname = NICKNAME1
        self.buttons = {
            "_up": p1_up,
            "_down": p1_down,
            "_right": p1_right,
            "_left": p1_left,
            "_fire": p1_fire,
            "_mine": p1_mine
        }

    def update(self, *args):
        if not self.killed:
            super().update(*args)
            if args:
                if args[0][self.buttons["_fire"]]:
                    self.shoot()

                if args[0][self.buttons[DIRECTION_UP]]:
                    self.rect = self.rect.move(0, -self.speed)
                    self.direction = DIRECTION_UP
                    if pg.sprite.spritecollideany(self, wall_group) or pg.sprite.spritecollideany(self, self.enemy):
                        self.rect = self.rect.move(0, self.speed)
                elif args[0][self.buttons[DIRECTION_DOWN]]:
                    self.rect = self.rect.move(0, self.speed)
                    self.direction = DIRECTION_DOWN
                    if pg.sprite.spritecollideany(self, wall_group) or pg.sprite.spritecollideany(self, self.enemy):
                        self.rect = self.rect.move(0, -self.speed)
                elif args[0][self.buttons[DIRECTION_LEFT]]:
                    self.rect = self.rect.move(-self.speed, 0)
                    self.direction = DIRECTION_LEFT
                    if pg.sprite.spritecollideany(self, wall_group) or pg.sprite.spritecollideany(self, self.enemy):
                        self.rect = self.rect.move(self.speed, 0)
                elif args[0][self.buttons[DIRECTION_RIGHT]]:
                    self.rect = self.rect.move(self.speed, 0)
                    self.direction = DIRECTION_RIGHT
                    if pg.sprite.spritecollideany(self, wall_group) or pg.sprite.spritecollideany(self, self.enemy):
                        self.rect = self.rect.move(-self.speed, 0)
                self.image = images["classic_tank" + self.direction]
                self.image.get_rect().center = self.rect.center

                if args[0][self.buttons["_mine"]]:
                    self.place_mine()
        else:
            pass

    def kill_tank(self):
        super().kill_tank()
        self.killed = True
        pg.display.set_caption("GAME OVER")


class ClassicTankSecondPlayer(ClassicTank):
    def __init__(self, pos_x, pos_y):
        self.team = enemies_group
        self.enemy = player_group
        super().__init__(pos_x, pos_y, self.team, self.enemy)
        self.objectname = NICKNAME2
        self.buttons = {
            "_up": p2_up,
            "_down": p2_down,
            "_right": p2_right,
            "_left": p2_left,
            "_fire": p2_fire,
            "_mine": p2_mine
        }

    def update(self, *args):
        if not self.killed:
            super().update(*args)
            if args:
                if args[0][self.buttons["_fire"]]:
                    self.shoot()

                if args[0][self.buttons[DIRECTION_UP]]:
                    self.rect = self.rect.move(0, -self.speed)
                    self.direction = DIRECTION_UP
                    if pg.sprite.spritecollideany(self, wall_group) or pg.sprite.spritecollideany(self, self.enemy):
                        self.rect = self.rect.move(0, self.speed)
                elif args[0][self.buttons[DIRECTION_DOWN]]:
                    self.rect = self.rect.move(0, self.speed)
                    self.direction = DIRECTION_DOWN
                    if pg.sprite.spritecollideany(self, wall_group) or pg.sprite.spritecollideany(self, self.enemy):
                        self.rect = self.rect.move(0, -self.speed)
                elif args[0][self.buttons[DIRECTION_LEFT]]:
                    self.rect = self.rect.move(-self.speed, 0)
                    self.direction = DIRECTION_LEFT
                    if pg.sprite.spritecollideany(self, wall_group) or pg.sprite.spritecollideany(self, self.enemy):
                        self.rect = self.rect.move(self.speed, 0)
                elif args[0][self.buttons[DIRECTION_RIGHT]]:
                    self.rect = self.rect.move(self.speed, 0)
                    self.direction = DIRECTION_RIGHT
                    if pg.sprite.spritecollideany(self, wall_group) or pg.sprite.spritecollideany(self, self.enemy):
                        self.rect = self.rect.move(-self.speed, 0)
                self.image = images["classic_tank" + self.direction]
                self.image.get_rect().center = self.rect.center

                if args[0][self.buttons["_mine"]]:
                    self.place_mine()
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
    tank_hit_sound = pg.mixer.Sound("source/data/sounds/hit_sound.mp3")
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

            if tank := pg.sprite.spritecollideany(self, self.owner.enemy_group):
                tank.hp -= self.damage
                ClassicBullet.tank_hit_sound.play()
                ParticleHitTank(self.rect.center, self.damage)
                if tank.hp - self.damage <= 0:
                    self.owner.score += 50
                else:
                    self.owner.score += 10
                self.kill()

            if wall := pg.sprite.spritecollideany(self, wall_group):
                wall.hp -= self.damage
                ParticleHitBrick(self.rect.center, random.choice(range(-5, 6)), random.choice(range(-20, -10)))
                self.kill()

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


class HealingParticle(FlyingParticle):
    def __init__(self, hbooster):
        txt = InterfaceForClassicTank.font.render("+" + str(BOOSTERS_CFG["hb_healing"]), True, GREEN)
        super().__init__(hbooster.rect.center, txt, 1, (0, -2))


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
    brick_hit_sound = pg.mixer.Sound("source/data/sounds/brick_hit_sound.mp3")
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


class Bush(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, bash_group)
        self.image = load_image("kust.png")
        self.rect = self.image.get_rect()
        self.rect.center = pos_x, pos_y

    def update(self):
        pass


class Booster(pg.sprite.Sprite):
    activation_sound = pg.mixer.Sound("source/data/sounds/activation.mp3")

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

        self.first_centery = self.rect.centery

    def update(self):
        if self.time_before_remove:
            hp_text = self.font.render(str(self.time_before_remove), True, SOFT_GOLD)
            screen.blit(hp_text, self.hp_rect)
            self.time_before_remove -= 1
            if tank := pg.sprite.spritecollideany(self, tanks_group):
                Booster.activation_sound.play()
                tank.activate_booster(self)
                self.kill()
            self.rect.centery = self.first_centery + int(sin(self.time_before_remove / 16) * 10)
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


class Mine(pg.sprite.Sprite):
    explode = pg.mixer.Sound("source/data/sounds/mine_explode.mp3")
    explode.set_volume(0.5)

    def __init__(self, pos_x, pos_y, group, group_to_kill, parent=None):
        super().__init__(all_sprites, mine_group)
        self.parent = parent
        self.image = load_image("mine.png")
        self.rect = self.image.get_rect()
        self.rect.center = pos_x, pos_y
        self.boom_radius = MINE_CFG["boom_rad"]
        self.team = group
        self.enemy = group_to_kill
        self.time_before_invisible = MINE_CFG["time_before_invisible"] * FPS
        self.damage = MINE_CFG["damage"]

    def update(self):
        if self.time_before_invisible > 0:
            self.time_before_invisible -= 1
            self.image.set_alpha(255 * self.time_before_invisible / MINE_CFG["time_before_invisible"])
        if tank := pg.sprite.spritecollideany(self, self.enemy):
            tank.hp -= self.damage
            if self.parent:
                self.parent.score += MINE_CFG["damage"]
            Mine.explode.play()
            self.kill()
            for _ in range(30):
                FlyingParticle(self.rect.center, load_image("fire_particle.png"), 1,
                               (random.randint(-5, 6), random.randint(-5, 6)))


class MapBoard:
    def __init__(self, width, height, left=50, top=50, cell_size=50, color=pg.Color("#1F2310")):
        self.width = width
        self.height = height
        self.board = [["" for _ in range(width)] for __ in range(height)]
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.border_color = color

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def get_board(self):
        return self.board

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                lt = (self.left + x * self.cell_size, self.top + y * self.cell_size)
                pg.draw.rect(screen, self.border_color, (lt, (self.cell_size, self.cell_size)), 1)

    def get_cell_center(self, x, y):
        """Метод, возвращающий центр клетки координат (x, y) на карте"""
        return (self.left + self.cell_size // 2 + x * self.cell_size,
                self.top + self.cell_size // 2 + y * self.cell_size)

    def genereate_level(self, level):
        """Метод, принимающий информацию об уровне генерирует его в игре и возвращает необх. информацию"""
        level_name = str(level[0])

        player1_pos, player2_pos = None, None
        if len(level) == 13:
            player1_pos = list(map(int, level[-2].split()))
            player2_pos = list(map(int, level[-1].split()))
            level_map = level[1:-2]
        elif len(level) == 12:
            player1_pos = list(map(int, level[-1].split()))
            level_map = level[1:-1]
        for i, row in enumerate(level_map):
            for j, elem in enumerate(row):
                if elem == '#':
                    BrickWall(*self.get_cell_center(j, i))
                elif elem == "1":
                    ClassicTankBot(*self.get_cell_center(j, i), player_group, enemies_group)
                elif elem == "2":
                    ClassicTankBot(*self.get_cell_center(j, i), enemies_group, player_group)
                elif elem == "3":
                    Mine(*self.get_cell_center(j, i), player_group, enemies_group)
                elif elem == "4":
                    Mine(*self.get_cell_center(j, i), enemies_group, player_group)
                elif elem == '%':
                    Bush(*self.get_cell_center(j, i))
        self.board = level_map
        return level_name, player1_pos, player2_pos


# Интерфейс
class InterfaceForClassicTank:
    font = pg.font.Font("source/data/font/ARCADE_N.TTF", 15)

    def __init__(self, tank: ClassicTank):
        self.tank = tank
        self.hp_rect = pg.Rect(710, 635, 100, 30)
        self.reload_rect = pg.Rect(710, 660, 100, 30)

        self.sp_b_rect = pg.Rect(50 * (1 + 5) + 10, 610, 80, 10)
        self.ar_b_rect = pg.Rect(50 * (1 + 7) + 10, 610, 80, 10)
        self.dd_b_rect = pg.Rect(50 * (1 + 9) + 10, 610, 80, 10)
        self.mine_rect = pg.Rect(50 * (1 + 11) + 10, 610, 80, 10)

        self.name_rect = pg.Rect(50 * (1 + 5), 570, 400, 30)

        self.dmg_rect = pg.Rect(50, 600, 100, 30)
        self.distance_rect = pg.Rect(50, 630, 100, 30)
        self.speed_rect = pg.Rect(50, 660, 100, 30)
        self.score_rect = pg.Rect(50, 570, 100, 30)

    def update(self):
        if not self.tank.in_bush:
            pg.draw.circle(screen, GRAY, self.tank.rect.center, radius=20, width=5)

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

        screen.blit(InterfaceForClassicTank.font.render("score: " + str(self.tank.score), True, SOFT_GOLD), self.score_rect)

        InterfaceForClassicTank.font.underline = False
        InterfaceForClassicTank.font.bold = False

        if not self.tank.boosters_activated[ARMOR_BOOSTER]:
            pg.draw.rect(screen, DARKRED, pg.Rect(50 * (1 + 5), 640, 400 * self.tank.hp // CLASSIC_TANK_CFG["hp"], 15),
                    border_radius=3)
            screen.blit(InterfaceForClassicTank.font.render(f"{self.tank.hp} / {CLASSIC_TANK_CFG['hp']}",
                                                            True, DARKRED), self.hp_rect)
        else:
            pg.draw.rect(screen, DARKRED, pg.Rect(50 * (1 + 5), 640, 400 * self.tank.hp // (CLASSIC_TANK_CFG["hp"] * 2),
                                                  15), border_radius=3)
            screen.blit(InterfaceForClassicTank.font.render(f"{self.tank.hp} / {CLASSIC_TANK_CFG['hp'] * 2}",
                                                            True, DARKRED), self.hp_rect)

        if not self.tank.is_reloaded:
            pg.draw.rect(screen, YELLOW, pg.Rect(50 * (1 + 5), 665,
                        400 * self.tank.reload_timer // self.tank.reload, 15), border_radius=3)
            screen.blit(InterfaceForClassicTank.font.render(f"{((self.tank.reload - self.tank.reload_timer) / 60):0.2f}",
                                                            True, YELLOW), self.reload_rect)
        else:
            pg.draw.rect(screen, YELLOW, pg.Rect(50 * (1 + 5), 665, 400, 15), border_radius=3)

        if self.tank.mines_count:
            if not self.tank.mine_reloaded:
                pg.draw.rect(screen, DARKGREEN, pg.Rect(50 * (1 + 11) + 10,
                        610, 80 * self.tank.mine_reload_timer // self.tank.mine_reload, 10), border_radius=3)
            else:
                pg.draw.rect(screen, DARKGREEN, pg.Rect(50 * (1 + 11) + 10, 610, 80, 10), border_radius=3)

        for rect in [self.sp_b_rect, self.ar_b_rect, self.dd_b_rect, self.mine_rect]:
            pg.draw.rect(screen, GRAY, rect, width=2, border_radius=3)

        if self.tank.boosters_activated[SPEED_BOOSTER]:
            pg.draw.rect(screen, YELLOW, self.sp_b_rect, border_radius=3)
        if self.tank.boosters_activated[ARMOR_BOOSTER]:
            pg.draw.rect(screen, DARKGREEN, self.ar_b_rect, border_radius=3)
        if self.tank.boosters_activated[DAMAGE_BOOSTER]:
            pg.draw.rect(screen, RED, self.dd_b_rect, border_radius=3)

        screen.blit(InterfaceForClassicTank.font.render(f"Damage:     {self.tank.dmg}", True, SOFT_GOLD),
                    self.dmg_rect)
        screen.blit(InterfaceForClassicTank.font.render(f"Fire range: {self.tank.fire_distance}", True, SOFT_GOLD),
                    self.distance_rect)
        screen.blit(InterfaceForClassicTank.font.render(f"Speed:      {self.tank.speed}", True, SOFT_GOLD),
                    self.speed_rect)