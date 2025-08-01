from machine import Timer, Pin
import machine
from micropython import schedule
import math
import time
from random import random
from touch import TouchController
import array
import gc
import animations

from is31fl3737 import is31fl3737, rgb_value

machine.freq(240000000)

def pallet_rainbow(target):
    for i in range(len(target)):
        target[i][0] = i/len(target)
        target[i][1] = 1.0
        target[i][2] = 255

def pallet_set_colour(target, hue, hue_spread, sat, sat_spread):
    offset = 0.0
    start = 0
    end   = 0
    count = int(len(target)/16)
    for i in range(16):
        dir_change = random() * 0.1
        if offset + dir_change >  hue_spread/2: dir_change = -dir_change
        if offset - dir_change < -hue_spread/2: dir_change = -dir_change
        offset += dir_change
        if offset >  hue_spread/2: offset =  hue_spread/2
        if offset < -hue_spread/2: offset = -hue_spread/2
        
        end   = offset
        step_size = (start - end)/count
        for j in range(count):
            pos = j / count
            offset = (step_size * pos) + start
            target[i*count + j][0] = hue+offset
            target[i*count + j][1] = sat
            target[i*count + j][2] = 255
        start = end
    end   = 0
    step_size = (start - end)/count
    for j in range(count):
        pos = j / count
        offset = (step_size * pos) + start
        target[len(target)-count+j][0] = hue+offset
        target[len(target)-count+j][1] = sat
        target[len(target)-count+j][2] = 255


def pallet_blue(target):
    pallet_set_colour(target, 0.5, 0.3, 0.8, 0.4)

def pallet_red(target):
    pallet_set_colour(target, 0.75, 0.3, 0.8, 0.4)

def pallet_green(target):
    pallet_set_colour(target, 0.0, 0.3, 0.8, 0.4)

def pallet_purple(target):
    pallet_set_colour(target, 0.25, 0.3, 0.8, 0.4)

class badge(object):
    def __init__(self):
        self.disp = is31fl3737()
        self.touch = TouchController((4,5,6,7))
        self.touch.channels[0].level_lo = 15000 # eye
        self.touch.channels[0].level_hi = 42000
        self.touch.channels[1].level_lo = 10000 # brows
        self.touch.channels[1].level_hi = 25000
        self.touch.channels[2].level_lo = 10000 # nose
        self.touch.channels[2].level_hi = 38000
        self.touch.channels[3].level_lo = 10000 # teeth
        self.touch.channels[3].level_hi = 34000
        self.boop_level = 0.0
        self.last_boop_level = 0.0
        self.half_bright = False
        self.boop_count = 0
        self.boop_mix = 0.5
        self.boop_offset = -8
        self.pallet_index = 0
        self.pallet_functions = [pallet_rainbow, pallet_blue, pallet_red, pallet_green, pallet_purple]

        self.sw4 = Pin(10)
        self.sw5 = Pin(11)

        self.sw4_state = 0xFF
        self.sw5_state = 0xFF

        self.sw4_count = 0
        self.sw5_count = 0
        self.sw4_last  = 0
        self.sw5_last  = 0

        # Setup the initial animation
        self.animation_list = animations.all()
        self.animation_index = 0
        self.next(0)

        #self.pallet = [[0.0,0.0,0.0] for i in range(1024)]
        self.pallet = [array.array("f", [0.0,0.0,0.0]) for i in range(1024)]
        self.pallet_functions[self.pallet_index](self.pallet)

        #                  0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17
        self.boop_img = (  0,  0,171,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,182,163, 30,  0,
                           0,  0,183,174, 30,  0, 30,175, 30,  0, 30,175, 30,  0,168,  0,159,  0,
                           0,  0,171,  0,159,  0,171,  0,171,  0,171,  0,171,  0,173,159, 30,  0,
                           0,  0,172,157, 30,  0, 30,154, 30,  0, 30,154, 30,  0,182, 10,  0,  0,)


        print("Hack the Monarchy!")
        self.timer = Timer(mode=Timer.PERIODIC, freq=10, callback=self.isr_update)

    def next(self, seek=1):
        """Seek to the next animation"""
        self.disp.clear()
        self.animation_index = (self.animation_index + seek)
        if self.animation_index >= len(self.animation_list): self.animation_index = 0
        if self.animation_index < 0: self.animation_index = len(self.animation_list)-1
        self.animation_current = self.animation_list[self.animation_index](self)
        print(f"Playing animation: {self.animation_current.__qualname__}")

    def boop(self, mix):
        if mix > 1.0: mix = 1.0
        if mix < 0.0: mix = 0.0
        for i in range(len(self.disp.downward)):
            self.disp.downward[i].r = (self.disp.downward[i].r * (1-mix))
            self.disp.downward[i].g = (self.disp.downward[i].g * (1-mix))
            self.disp.downward[i].b = (self.disp.downward[i].b * (1-mix))
        for x in range(7):
            for y in range(4):
                x_offset = x + self.boop_offset
                if x_offset <  0: x_offset = 0
                if x_offset > 17: x_offset = 17
                self.disp.eye_grid[x][y].r += self.boop_img[x_offset+(3-y)*18]
                self.disp.eye_grid[x][y].g += self.boop_img[x_offset+(3-y)*18]
                self.disp.eye_grid[x][y].b += self.boop_img[x_offset+(3-y)*18]


    def isr_update(self,*args):
        schedule(self.update, self)

    def update(self,*args):
        self.touch.update()
        self.last_boop_level = self.boop_level
        self.boop_level = self.touch.channels[2].level
        if (self.boop_level > 0.3):
            if (self.last_boop_level <= 0.3):
                self.boop_offset = -5
                self.boop_mix    = 1.0

            # Start booping
            self.boop_count = 20
        else:
            # Fade out the boop
            if self.boop_count > 0:
                self.boop_count -= 1
            elif self.boop_mix > 0.0:
                    self.boop_mix -= 0.05

        self.sw4_state <<= 1
        self.sw4_state |= self.sw4()
        self.sw5_state <<= 1
        self.sw5_state |= self.sw5()
        if (self.sw4_state & 0x3) == 0x0: self.sw4_count += 1
        else:                             self.sw4_count = 0
        if (self.sw5_state & 0x3) == 0x0: self.sw5_count += 1
        else:                             self.sw5_count = 0
        
        if self.sw4_count == 0 and self.sw4_last > 0:
            if self.sw4_last > 10: # long press
                self.half_bright = not self.half_bright
            else:
                self.next(1)
        elif self.sw5_count == 0 and self.sw5_last > 0:
            if self.sw5_last > 10:
                self.pallet_index += 1
                if self.pallet_index >= len(self.pallet_functions):
                    self.pallet_index = 0
                self.pallet_functions[self.pallet_index](self.pallet)
            else:
                if (hasattr(self.animation_current, "button") and callable(self.animation_current.button)):
                    self.animation_current.button()
                else:
                    self.next(-1)

        self.sw4_last = self.sw4_count
        self.sw5_last = self.sw5_count

        if self.half_bright: self.disp.brightness = 50
        else:                self.disp.brightness = 255

        self.animation_current.update()

        # Mix the boop effect in - then restore the state
        # when we're done so we don't interfere with any animation state

        if (self.boop_mix > 0.0):
            backup = [rgb_value(i.r, i.g, i.b) for i in self.disp.downward]
            self.boop(self.boop_mix)
        self.disp.update()
        if (self.boop_mix > 0.0):
            self.boop_offset += 1
            for i in range(len(backup)):
                self.disp.downward[i].copy(backup[i])

        gc.collect()

    def run(self):
        while True:
            self.update()
            time.sleep(1/10)


global t
t = badge()
#t.run()
