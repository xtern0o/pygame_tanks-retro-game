import os

from source.gameobjects import *
from source.functions import terminate


pg.init()


pg.display.set_caption("Tanks Retro Game")

# map_board = MapBoard(16, 10)
# player = ClassicTankPlayer(30, 30)
# enemybot = ClassicTankBot(500, 500, enemies_group, player_group, speed=2)
# teammatebot = ClassicTankBot(200, 50, player_group, enemies_group)
# wall1 = BrickWall(*map_board.get_cell_center(2, 5))
# wall2 = BrickWall(*map_board.get_cell_center(2, 6))
# wall3 = BrickWall(*map_board.get_cell_center(3, 5))
# wall4 = BrickWall(*map_board.get_cell_center(5, 5))
# dambooster = DamageBooster(*map_board.get_cell_center(9, 1))
# spebooster = SpeedBooster(*map_board.get_cell_center(10, 1))
# armbooster = ArmorBooster(*map_board.get_cell_center(11, 1))
# heabooster = HealthBooster(*map_board.get_cell_center(12, 1))

map_board = MapBoard(16, 10)

levels_folder = os.listdir("source/data/levels")
for level_file in levels_folder:
    with open("source/data/levels/" + level_file, mode="r", encoding="utf-8") as file:
        level_info = file.readlines()
    level_name, player_pos = map_board.genereate_level(level_info)

    player = ClassicTankPlayer(*player_pos)
    interface = InterfaceForClassicTank(player)
    clock = pg.time.Clock()

    level_go = True
    while level_go:
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
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_c:
                    # next level
                    level_go = False


        map_board.render(screen)

        keys_pressed = pg.key.get_pressed()
        if keys_pressed[pg.K_ESCAPE]:
            terminate()
        player.update(keys_pressed)

        interface.update()
        all_sprites.draw(screen)
        all_sprites.update()

        pg.display.flip()
