import os
import sys
import datetime as dt
import pygame as pg


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


def log(strdata: str):
    strdata += dt.datetime.now().strftime("[%Y, %b %w] ")
    with open("data/logs.txt", mode="w", encoding="utf-8") as f:
        f.write(strdata)

