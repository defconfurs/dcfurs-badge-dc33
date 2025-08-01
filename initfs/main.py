from machine import Timer, Pin
from micropython import schedule
import math
import time
from random import random
from touch import TouchController
import array
import gc
import animations

from is31fl3737 import is31fl3737, rgb_value

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
        self.half_bright = False
        self.blush_count = 0
        self.blush_mix = 0.5
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

        print("Hack the Monarchy!")
        self.timer = Timer(mode=Timer.PERIODIC, freq=15, callback=self.isr_update)

    def next(self, seek=1):
        """Seek to the next animation"""
        self.disp.clear()
        self.animation_index = (self.animation_index + seek)
        if self.animation_index >= len(self.animation_list): self.animation_index = 0
        if self.animation_index < 0: self.animation_index = len(self.animation_list)-1
        self.animation_current = self.animation_list[self.animation_index](self)
        print(f"Playing animation: {self.animation_current.__qualname__}")

    def blush(self, mix):
        pass
        # if mix > 1.0: mix = 1.0
        # if mix < 0.0: mix = 0.0
        # for i in range(len(self.disp.cheeks)):
        #     self.disp.cheeks[i].r = (self.disp.cheeks[i].r * (1-mix)) + (mix * 255)
        #     self.disp.cheeks[i].g = (self.disp.cheeks[i].g * (1-mix)) + (mix * 10)
        #     self.disp.cheeks[i].b = (self.disp.cheeks[i].b * (1-mix)) + (mix * 10)

    def isr_update(self,*args):
        schedule(self.update, self)

    def update(self,*args):
        self.touch.update()
        if (self.touch.channels[3].level > 0.3):
            # Invoke the animation's boop method, if present.
            # if (hasattr(self.animation_current, "boop") and
            #     callable(self.animation_current.boop) and
            #     self.blush_count < 50):
            #     self.animation_current.boop()

            # Start blushing
            self.blush_count = 50
            if self.blush_mix < 1.0:
                self.blush_mix += 0.5
        else:
            # Fade out the blush
            if self.blush_count > 0:
                self.blush_count -= 1
            elif self.blush_mix > 0.0:
                    self.blush_mix -= 0.05

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

        # # Mix the blush effect into the cheeks - then restore the state of the
        # # cheeks when we're done so we don't interfere with any animation state
        # backup = [rgb_value(i.r, i.g, i.b) for i in self.disp.cheeks]
        # self.blush(self.blush_mix)
        self.disp.update()
        # for i in range(len(backup)):
        #     self.disp.cheeks[i].copy(backup[i])

        gc.collect()

    def run(self):
        while True:
            self.update()
            time.sleep(1/15)


global t
t = badge()
#t.run()
