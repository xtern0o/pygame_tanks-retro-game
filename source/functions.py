import os
import sys
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


# def level_validator(level):
#     # кол-во строк
#     if not 12 <= len(level) <= 13:
#         return False
#
#     # кол-во элементов в строках
#     for row in level[1:-1]:
#         if len()
