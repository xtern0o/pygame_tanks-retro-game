import os
import sys
import datetime as dt
import pygame as pg

from source.constants import *


def load_image(name):
    fullname = os.path.join('source/data/images', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    return image


def terminate():
    pg.quit()
    sys.exit()


def log(strdata: str, small=None):
    with open("source/data/logs.txt", mode="a", encoding="utf-8") as f:
        if small is None:
            f.write(dt.datetime.now().strftime("========\n[!] | [%Y, %b %w] ") + strdata + "\n========\n")
        else:
            f.write(dt.datetime.now().strftime("--- [%Y, %b %w] ") + strdata + "\n")


def show_screen(filename: str, screen):
    clock = pg.time.Clock()
    time = 0
    if filename != "error_screen.png":
        while True:
            im = load_image(filename)
            im.set_alpha(255 * time // FPS // 2)
            screen.blit(pg.transform.scale(im, (W, H)), pg.Rect(0, 0, W, H))
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    terminate()
                if event.type in (pg.MOUSEBUTTONDOWN, pg.KEYDOWN):
                    if filename not in ("next_map_screen.png", "startscreen.png"):
                        terminate()
                    else:
                        return None
            pg.display.flip()
            clock.tick(FPS)
            time += 1
    else:
        while True:
            screen.blit(pg.transform.scale(load_image("error_screen.png"), (W, H)), pg.Rect(0, 0, W, H))
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    terminate()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    terminate()
            pg.display.flip()
            clock.tick(FPS)