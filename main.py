from source.gameobjects import *
from source.functions import *


pg.init()


def spawn_random_booster():
    x, y = random.randint(0, 15), random.randint(0, 9)
    if map_board.get_board()[y][x] not in ('#', '%', '1', '2', '3', '4'):
        b = random.randint(0, 4)
        if b == 0:
            SpeedBooster(*map_board.get_cell_center(x, y))
        elif b == 1:
            DamageBooster(*map_board.get_cell_center(x, y))
        elif b == 2:
            ArmorBooster(*map_board.get_cell_center(x, y))
        else:
            HealthBooster(*map_board.get_cell_center(x, y))
        return None
    spawn_random_booster()


pg.display.set_caption("Tanks Retro Game")

clock = pg.time.Clock()
show_screen("startscreen.png", screen)

map_board = MapBoard(16, 10)

border1 = Border(True, 0, 50)
border2 = Border(True, 0, 550)
border3 = Border(False, 50, 0)
border4 = Border(False, 850, 0)

level_rect = pg.Rect(pg.Rect(10, 5, 880, 30))
level_name_rect = pg.Rect(pg.Rect(30, 10, 900, 20))
levels_folder = os.listdir("source/data/levels")
for i, level_file in enumerate(levels_folder):
    with open("source/data/levels/" + level_file, mode="r", encoding="utf-8") as file:
        level_info = file.readlines()
    try:
        level_name, player1_pos, player2_pos = map_board.genereate_level(level_info)
        level_name = level_name[:-1]
        level_name += " [{} / {}]]".format(i + 1, len(levels_folder))

        if not player2_pos:
            player = ClassicTankPlayer(*map_board.get_cell_center(*player1_pos))
            interface = InterfaceForClassicTank(player)
            twoplayers_mode = False
        else:
            player1 = ClassicTankPlayer(*map_board.get_cell_center(*player1_pos))
            player2 = ClassicTankSecondPlayer(*map_board.get_cell_center(*player2_pos))
            interface = InterfaceForClassicTank(player1)
            twoplayers_mode = True
    except Exception:
        show_screen("error_screen.png", screen)
        break

    pg.time.set_timer(BOOSTER_SPAWN, GLOBAL_CFG["booster_spawn_frequency"] * 1000)

    level_run = True
    while level_run:
        screen.fill(BLACK)
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == BOOSTER_SPAWN:
                spawn_random_booster()

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
                    log(f"СМЕНА КАРТЫ")
                    show_screen("next_map_screen.png", screen)
                    level_run = False
                    for sprite in all_sprites:
                        sprite.kill()

        pg.draw.rect(screen, SOFT_GOLD, level_rect, border_radius=4)
        font = InterfaceForClassicTank.font
        screen.blit(font.render(level_name[:-1], True, BLACK), level_name_rect)

        map_board.render(screen)

        keys_pressed = pg.key.get_pressed()
        if keys_pressed[pg.K_ESCAPE]:
            terminate()

        if twoplayers_mode:
            player1.update(keys_pressed)
            player2.update(keys_pressed)
            if player1.killed and not player2.killed:
                log(f"Результаты дуэли: {player1.objectname} < {player2.objectname}")
                show_screen("2_win.png", screen)
            elif player2.killed and not player1.killed:
                log(f"Результаты дуэли: {player1.objectname} > {player2.objectname}")
                show_screen("1_win.png", screen)
        else:
            player.update(keys_pressed)
            if player.killed:
                show_screen("lose_screen.png", screen)
                log(f"Игрок набрал: <{player.score}>")

        interface.update()
        all_sprites.draw(screen)
        all_sprites.update()

        pg.display.flip()

show_screen("end_screen.png", screen)