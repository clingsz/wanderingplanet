#!/usr/bin/env python
""" pg.examples.stars
"""
import random
import math
import pygame as pg
import math

from tkinter import *
from tkinter import messagebox
from copy import deepcopy

WINSIZE = [800, 600]
NUMSTARS = 200
GRAVITY_CONSTANT = 0.1
WINCENTER = [0, 0]
SCALE = 1
UNIVERSE_RADIUS = 3000
START_TICK = 0
NO_GRAVITY = True
GRAVITY_DELAY = 100
SHRINK_DELAY = 1000
lock_star = None
LIFE_YEAR = 0
DIR = None


class Color:
    white = 255, 240, 200
    gray = 128, 128, 128
    blue = 0, 153, 153
    red = 255, 128, 0
    black = 20, 20, 40
    darkred = 102, 0, 0
    yellow = 240, 240, 20
    green = 20, 230, 20

stage = [
    [1, "Nothing"], #0
    [100, "SingleCell"], #1
    [500, "Ecosystem"], #2
    [1000, "Plants"], #3
    [3000, "Dinasour"], #4
    [5000, "Human"], #5
    [7000, "Civilization"], #6
    [10000, "SpaceTechs"], #7
    [15000, "FuseEngine"], #8
    [20000, "Antimatter"], #9
    [25000, "WarpMachine"], #9
]

def get_life_stage():
    global LIFE_YEAR, stage
    for i,s in enumerate(stage):
        if LIFE_YEAR<s[0]:
            return i,s[1]
    return 9, "SuperPower"

def raw_to_window(raw_pos):
    return (SCALE*(raw_pos[0]- WINCENTER[0]) + WINSIZE[0]/2 , SCALE*(raw_pos[1] - WINCENTER[1])+ WINSIZE[1]/2)

def window_to_raw(win_pos):
    return [(win_pos[0] - WINSIZE[0]/2)/SCALE + WINCENTER[0]  , (win_pos[1] - WINSIZE[1]/2)/SCALE + WINCENTER[1]]

def show_txt(screen, txt):
    myfont = pg.font.SysFont('Comic Sans MS', 20)
    textsurface = myfont.render(txt, False, Color.white)
    screen.blit(textsurface,(WINSIZE[0]/12,10))

def show_paused(screen):
    myfont = pg.font.SysFont('Comic Sans MS', 20)
    textsurface = myfont.render("Game Paused [Press Space to Continue]", False, Color.white)
    screen.blit(textsurface,(WINSIZE[0]/3,WINSIZE[1]-50))

def show_year(screen, year):
    myfont = pg.font.SysFont('Comic Sans MS', 20)
    textsurface = myfont.render(f"YEAR:{year}      ", False, Color.white, Color.black)
    screen.blit(textsurface,(WINSIZE[0]-170, 10))

def show_life_year(screen, year):
    myfont = pg.font.SysFont('Comic Sans MS', 20)
    textsurface = myfont.render(f"LIFE YEAR:{year}      ", False, Color.white, Color.black)
    screen.blit(textsurface,(WINSIZE[0]-170, 50))

def show_life_stage(screen, life_stage):
    myfont = pg.font.SysFont('Comic Sans MS', 20)
    textsurface = myfont.render(f"Age: {life_stage}       ", False, Color.white, Color.black)
    screen.blit(textsurface,(WINSIZE[0]-170, 90))

def show_r(screen, r):
    myfont = pg.font.SysFont('Comic Sans MS', 20)
    textsurface = myfont.render(f"Radius: {r:.1f}       ", False, Color.white, Color.black)
    screen.blit(textsurface,(WINSIZE[0]-170, 130))
    textsurface = myfont.render(f"Gravity: {GRAVITY_CONSTANT:.1f}       ", False, Color.white, Color.black)
    screen.blit(textsurface,(WINSIZE[0]-170, 170))


HIT_STAR = 0
over_star = None

COLOR_MAP = {
    10: Color.gray,
    50: Color.blue,
    100: Color.red,
}
def find_color(r):
    for k in COLOR_MAP:
        if r <= k:
            return COLOR_MAP[k]
    return Color.white

class Star(object):
    def __init__(self, sid):
        r = random.random() * 10 + 0.5

        ax, ay = 0, 0

        dir = random.randrange(100000)
        velmult = random.random() * 0.9 + 0.1
        velmult *= 5
        vel = [math.sin(dir) * velmult, math.cos(dir) * velmult]

        # dir = random.randrange(100000)
        # posmult = random.random() * 0.9 + 0.1
        # posmult *= 200
        # x,y = [math.sin(dir) * posmult, math.cos(dir) * posmult]
        x,y = 0,0
        self.r = r
        self.xy = [x, y]
        self.axy = [ax, ay]
        self.vxy = vel
        self.sid = sid
        self.alive = True
        self.merge_to = None
        self.out = False
    def draw(self, screen, color=None):
        raw_pos = (self.xy[0], self.xy[1])
        pos = raw_to_window(raw_pos)
        r = roundint(self.r * SCALE)[0]
        pos = roundint(pos)

        if color is None:
            color = find_color(self.r)
        pg.draw.circle(screen, color, pos, r)
        if self == over_star:
            pg.draw.circle(screen, Color.yellow, pos, r+1, 1)

        if self == lock_star:
            pg.draw.circle(screen, Color.green, pos, r+2, 1)
            F = 10
            new_pos = roundint([pos[0]+self.vxy[0]*F, pos[1]+self.vxy[1]*F])
            pg.draw.line(screen, color, pos, new_pos, 1)

        # F = 1e8
        # new_pos_a = roundint([pos[0]+self.axy[0]*F, pos[1]+self.axy[1]*F])
        # new_pos_r = roundint([pos[0] + self.r*2, pos[1]])
        # # pg.draw.line(screen, color, pos, new_pos_r, 1)
        # try:
        #     pg.draw.line(screen, color, pos, new_pos_a, 2)
        # except:
        #     pass
        # pg.draw.line(screen, color, pos, [pos[0]+self.axy[0]*10, pos[1]+self.axy[1]*10], 20)
        # for x in range(-r,r+1):
        #     for y in range(-r,r+1):
        #         if (x*x + y*y) <= r*r:
        #             draw_pos = (pos[0] + x, pos[1] + y)
        #             screen.set_at(draw_pos, color)

    def tick(self, stars):
        global HIT_BOUND, DIR, lock_star, END_GAME

        dx = 0
        dy = 0
        num_stage = get_life_stage()[0]
        if self == lock_star:
            if self.r >= 50:
                END_GAME = "Your planet is too big, and it became a hot star. Game Over"

        if DIR is not None and self == lock_star:
            if DIR == pg.K_w:
                dy = -1
            elif DIR==pg.K_d:
                dx = 1
            elif DIR==pg.K_a:
                dx = -1
            elif DIR==pg.K_s:
                dy = 1
            dx = dx * 0.01 * 1.5**num_stage
            dy = dy * 0.01 * 1.5**num_stage
            DIR = None
        if not NO_GRAVITY:
            self.vxy = [self.vxy[0] + self.axy[0] + dx, self.vxy[1] + self.axy[1] + dy]

        self.xy = [self.xy[0] + self.vxy[0], self.xy[1] + self.vxy[1]]
        d2 = self.xy[0] ** 2 + self.xy[1] ** 2
        # hit bound
        if d2 >= (UNIVERSE_RADIUS-self.r) **2:
            if self == lock_star and HIT_BOUND == 0:
                HIT_BOUND = 1
            if not self.out:
                x,y = self.xy
                norm = math.sqrt(x*x + y*y)
                x = -x/norm
                y = -y/norm
                vx, vy = self.vxy
                dp = vx*x + vy*y
                nvx = vx - 2*dp*x
                nvy = vy - 2*dp*y
                self.vxy = [nvx, nvy]
                self.out = True
            else:
                nd = UNIVERSE_RADIUS - self.r
                d = math.sqrt(d2)
                self.xy = [self.xy[0]/d*nd, self.xy[1]/d*nd]
                self.out = False
        else:
            self.out = False


    def get_mass(self):
        return self.r**2 * 3.14

    def update_force(self, stars):
        self.axy = [0, 0]
        for s in stars:
            if s is not self:
                # print(self.sid, self.xy, s.sid, s.xy)
                dx = s.xy[0] - self.xy[0]
                dy = s.xy[1] - self.xy[1]
                d2 =  dx*dx + dy*dy
                d = math.sqrt(d2)
                if d2 == 0:
                    continue
                a = GRAVITY_CONSTANT * s.get_mass() / d2
                ax = a/d*dx
                ay = a/d*dy
                # print(ax, ay)
                self.axy[0] += ax
                self.axy[1] += ay

def initialize_stars():
    stars = []
    for i in range(NUMSTARS):
        stars.append(Star(i))
    return stars

def roundint(x):
    if type(x) is tuple:
        x = list(x)
    elif type(x) is not list:
        x = [x]

    return [int(round(i)) for i in x]

def get_dist(xy1, xy2):
    dx = xy1[0] - xy2[0]
    dy = xy1[1] - xy2[1]
    d2 =  dx*dx + dy*dy
    d = math.sqrt(d2)
    return d

def ratiolize(xy1, xy2, r1r, r2r):
    return  [xy1[0] *r1r + xy2[0]*r2r, xy1[1]*r1r + xy2[1]*r2r]

END_GAME = None

def handle_hit_star(s1, s2, d):
    global LIFE_YEAR, HIT_STAR, END_GAME
    r1s = s1.r * s1.r
    r2s = s2.r * s2.r
    r1 = s1.r
    r2 = s2.r
    o = r1 + r2 - d
    nr2 = max(r2 - o, 0)
    drs = r2s - nr2

    r1r = r1s/(r1s + drs)
    r2r = drs/(r1s + drs)
    s1.r = math.sqrt(r1s + drs)
    s1.xy = ratiolize(s1.xy, s2.xy, r1r, r2r)
    s1.vxy = ratiolize(s1.vxy, s2.vxy, r1r, r2r)
    s1.axy = ratiolize(s1.axy, s2.axy, r1r, r2r)

    if nr2 == 0:
        s2.merge_to = s1
        s2.alive = False
        if s1 == lock_star:
            LIFE_YEAR = max(0, LIFE_YEAR-100)
            if HIT_STAR == 0:
                HIT_STAR = 1
        if s2 == lock_star:
            END_GAME = "You planet has been crushed by a big star. Game Over"
    else:
        s2.r = nr2

def check_merge(stars):
    n = len(stars)
    for i in range(n-1):
        for j in range(i+1,n):
            s1 = stars[i]
            s2 = stars[j]
            if s1.alive and s2.alive:
                d = get_dist(s1.xy, s2.xy)
                if s1.r + s2.r > d:
                    # print(s1.xy, s1.r, s2.xy, s2.r, d)
                    if s1.r >= s2.r:
                        handle_hit_star(s1, s2, d)
                    else:
                        handle_hit_star(s2, s1, d)

    # TODO: need better handling of new loc and velocity/acceleration/etc
    return [s for s in stars if s.alive]


def draw_stars(screen, stars, color=None):
    "used to draw (and clear) the stars"
    for s in stars:
        s.draw(screen, color)

def draw_universe(screen, color):
    pos = raw_to_window([0, 0])
    r = roundint(UNIVERSE_RADIUS * SCALE)[0]
    pos = roundint(pos)
    pg.draw.circle(screen,color, pos, r, 1)


def move_stars(stars):
    "animate the star values"
    for s in stars:
        s.update_force(stars)

    for s in stars:
        s.tick(stars)

def refresh(screen):
    screen.fill(Color.black)

PICK_STAR_DELAY = 50

YEAR_EVENTS = {
    0: "In the beginning, BIG BANG!",
    GRAVITY_DELAY: "Gravity!",
    GRAVITY_DELAY+10: "You can use WASD to apply a little force!",
    # GRAVITY_DELAY+100: "You can use WASD to apply a little force!",
    SHRINK_DELAY: "Universe shrink! Gravity stronger!",
    # 200: "Press left or right to speed up and down, scroll up or down to scale.",
    30000: "Now it's the end of the everything...",
}

HIT_BOUND = 0

paused = False
EVENT = 0
NEW_AGE = 1

def check_event(year, screen):
    global paused, HIT_BOUND, EVENT
    if HIT_BOUND == 1:
        show_txt(screen, "You just hit the boundary of the universe.")
        paused=True
        HIT_BOUND = 2
    if year in YEAR_EVENTS:
        show_txt(screen, YEAR_EVENTS[year])
        if not paused:
            paused = True
    if year-1 in YEAR_EVENTS:
        refresh(screen)

CHOOSE_STAR = False

def main():
    global SCALE, UNIVERSE_RADIUS, NO_GRAVITY, paused, CHOOSE_STAR, over_star, lock_star, LIFE_YEAR, END_GAME, HIT_STAR, DIR, NEW_AGE, GRAVITY_CONSTANT
    random.seed(123)

    stars = initialize_stars()
    clock = pg.time.Clock()
    freq = 1

    pg.init()
    pg.font.init()

    screen = pg.display.set_mode(WINSIZE)
    pg.display.set_caption("The Wandering Star")

    refresh(screen)
    tick = 40
    # main game loop
    done = 0
    cnt = 0
    years = -1
    stage = 0
    while not done:
        draw_stars(screen, stars, Color.black)
        draw_universe(screen, Color.black)
        if years == PICK_STAR_DELAY:
            if lock_star is None:
                paused = True
                show_txt(screen, "Pick a star. click to move screen.")
                CHOOSE_STAR = True
            else:
                show_txt(screen, f"Star {lock_star.sid}, Radius {lock_star.r:.1f}. ")
        if years == PICK_STAR_DELAY + 1:
            refresh(screen)
        if not paused:
            for i in range(freq):
                if not NO_GRAVITY:
                    stars = check_merge(stars)
                move_stars(stars)
                if lock_star:
                    # while(lock_star.merge_to is not None):
                    #     lock_star = lock_star.merge_to
                    WINCENTER[:] = lock_star.xy
                years += 1
                if years > PICK_STAR_DELAY:
                    LIFE_YEAR += 1
                if years >= SHRINK_DELAY:
                    UNIVERSE_RADIUS -= 0.1
                    GRAVITY_CONSTANT *= 1.0001
                if years == GRAVITY_DELAY:
                    NO_GRAVITY = False
                if UNIVERSE_RADIUS < 5:
                    return

        draw_stars(screen, stars)
        draw_universe(screen, Color.darkred)
        show_year(screen, years)
        if years > PICK_STAR_DELAY:
            CHOOSE_STAR = False
            show_life_year(screen, LIFE_YEAR)
            num_stage, life_stage = get_life_stage()
            show_life_stage(screen, life_stage)
            show_r(screen, lock_star.r)
            if num_stage>1 and NEW_AGE != num_stage:
                show_txt(screen, f"You Entered a New Age: {life_stage}! Your force is stronger!")
                paused = True
                NEW_AGE = num_stage

        if HIT_STAR == 1:
            show_txt(screen, "Your planet has been hit by another star (-100 life year)")
            paused = True
            HIT_STAR += 1

        # event handling
        check_event(years, screen)
        if years == PICK_STAR_DELAY + 1:
            show_txt(screen, "You started life on this planet!")
            paused = True

        if paused:
            show_paused(screen)

        if END_GAME is not None:
            if isinstance(END_GAME, str):
                show_txt(screen, END_GAME)
                END_GAME = years
            else:
                if END_GAME < years:
                    return
            paused = True

        pg.display.update()
        # handle events
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYUP and e.key == pg.K_ESCAPE):
                done = 1
                break
            elif e.type == pg.KEYDOWN and e.key==pg.K_RIGHT:
                # increase the frequency
                if paused:
                    paused = False
                    refresh(screen)
                else:
                    freq *= 2
                print(freq)
            elif e.type == pg.KEYDOWN and e.key == pg.K_LEFT:
                # decrease the frequency
                if freq > 1:
                    freq = int(freq / 2)
                else:
                    paused = True
                print(freq)
            elif e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                if paused:
                    paused = False
                    refresh(screen)
                else:
                    paused = True
            elif (e.type == pg.KEYDOWN and e.key==pg.K_UP) or (e.type == pg.MOUSEBUTTONDOWN and e.button == 4):
                SCALE = SCALE * 1.2
                print(SCALE)
                refresh(screen)
            elif (e.type == pg.KEYDOWN and e.key == pg.K_DOWN)  or (e.type == pg.MOUSEBUTTONDOWN and e.button == 5):
                SCALE = SCALE / 1.2
                print(SCALE)
                refresh(screen)
            elif (e.type == pg.KEYDOWN and e.key in (pg.K_w, pg.K_s, pg.K_a, pg.K_d)):
                DIR = None
                if years >= PICK_STAR_DELAY:
                    DIR = e.key
            elif e.type == pg.MOUSEMOTION:
                if CHOOSE_STAR:
                    npos = window_to_raw(e.pos)
                    over_star = None
                    for s in stars:
                        if get_dist(s.xy, npos)<s.r:
                            over_star = s
                    if over_star is not None:
                        refresh(screen)

            elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                # rpos = [e]
                if CHOOSE_STAR:
                    npos = window_to_raw(e.pos)
                    lock_star = None
                    for s in stars:
                        if get_dist(s.xy, npos)<s.r:
                            lock_star = s
                    WINCENTER[:] = npos
                    refresh(screen)

        if tick>0:
            clock.tick(tick)
        else:
            clock.tick(1)
        if lock_star is not None:
            pg.display.set_caption(f"YEAR: {years}, R:{lock_star.r:.1f}, ID: {lock_star.sid}, S:{SCALE:.1f}")
        else:
            pg.display.set_caption(f"YEAR: {years}, S:{SCALE:.1f}")

# if python says run, then we should run
if __name__ == "__main__":
    main()
