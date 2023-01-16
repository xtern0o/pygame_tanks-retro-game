import pygame as pg

SIZE = W, H = 900, 700
FPS = 60

BOOSTER_SPAWN = pg.USEREVENT + 1

DIRECTION_UP = "_up"
DIRECTION_DOWN = "_down"
DIRECTION_RIGHT = "_right"
DIRECTION_LEFT = "_left"
DIRECTIONS = (DIRECTION_UP, DIRECTION_DOWN, DIRECTION_RIGHT, DIRECTION_LEFT)

SPEED_BOOSTER = "sb"
DAMAGE_BOOSTER = "db"
ARMOR_BOOSTER = "ab"
HEALTH_BOOSTER = "hb"

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
DARKGRAY = pg.Color("darkgray")
