import os

from source.gameobjects import *
from source.functions import terminate


pg.init()


def startscreen():
    while True:
        screen.blit(pg.transform.scale(load_image("startscreen.png"), (W, H)), pg.Rect(0, 0, W, H))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type in (pg.MOUSEBUTTONDOWN, pg.KEYDOWN):
                return None
        pg.display.flip()
        clock.tick(FPS)


def next_level_screen():
    while True:
        screen.blit(pg.transform.scale(load_image("next_map_screen.png"), (W, H)), pg.Rect(0, 0, W, H))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type in (pg.MOUSEBUTTONDOWN, pg.KEYDOWN):
                return None
        pg.display.flip()
        clock.tick(FPS)


pg.display.set_caption("Tanks Retro Game")

clock = pg.time.Clock()
startscreen()

map_board = MapBoard(16, 10)

level_rect = pg.Rect(pg.Rect(0, 10, 900, 20))
level_name_rect = pg.Rect(pg.Rect(10, 10, 900, 20))
levels_folder = os.listdir("source/data/levels")
for i, level_file in enumerate(levels_folder):
    with open("source/data/levels/" + level_file, mode="r", encoding="utf-8") as file:
        level_info = file.readlines()
    level_name, player_pos = map_board.genereate_level(level_info)
    level_name = level_name[:-1]
    level_name += " [{} / {}]]".format(i + 1, len(levels_folder))

    player = ClassicTankPlayer(*map_board.get_cell_center(*player_pos))
    interface = InterfaceForClassicTank(player)

    level_run = True
    while level_run:
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
                        for _ in range(10):
                            FlyingParticle((x, y), load_image("fire_particle.png"), 1,
                                           (random.randint(-5, 6), random.randint(-5, 6)))
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_c:
                    next_level_screen()
                    level_run = False
                    for sprite in all_sprites:
                        sprite.kill()

        pg.draw.rect(screen, SOFT_GOLD, level_rect, border_radius=3)
        font = InterfaceForClassicTank.font
        screen.blit(font.render(level_name[:-1], True, BLACK), level_name_rect)

        map_board.render(screen)

        keys_pressed = pg.key.get_pressed()
        if keys_pressed[pg.K_ESCAPE]:
            terminate()
        player.update(keys_pressed)

        if player.killed:
            pass

        interface.update()
        all_sprites.draw(screen)
        all_sprites.update()

        pg.display.flip()
