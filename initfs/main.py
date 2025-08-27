from machine import Timer, Pin, UART
import machine
from micropython import schedule
import math
import time
from random import random
from touch import TouchController
import array
import gc
import animations
import lora_e5_radio

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


class ScritchDetector:
    def __init__(self, eps_ms=500, min_ms=100, max_ms=1000, cooldown_ms=200):
        self.EPS_MS = eps_ms          # allow small simultaneity between adjacent pads
        self.MIN_MS = min_ms          # 0.1 s
        self.MAX_MS = max_ms          # 1.0 s
        self.COOLDOWN_MS = cooldown_ms
        self._since_ts = 0            # ignore touch starts older than this
        self._last_fire_ts = -10**9

    def _is_monotonic_nondec(self, times, idxs):
        # Check t[idx0] <= t[idx1] <= t[idx2] <= t[idx3] with EPS tolerance
        for a, b in zip(idxs, idxs[1:]):
            if times[a] > times[b] + self.EPS_MS:
                return False
        return True

    def check(self, now_ms, touch_start_time, is_touched, touch_end_time):
        """
        Returns:
          'DOWN'
          'UP'
          None if no swipe.
        Notes:
          - Uses only start times to determine order.
          - Allows multiple pads to be touched at the same time (within EPS).
          - Rejects out-of-order (e.g., pad 2 before pad 1 for an Up->Down).
        """

        # Cooldown to avoid double-firing on the same swipe cluster
        if now_ms - self._last_fire_ts < self.COOLDOWN_MS:
            return None

        # Require that all four pads have a start newer than the last accepted cluster boundary
        starts = touch_start_time  # alias
        if not all(touch_start_time) or not all(touch_end_time) or not all(starts[i] > self._since_ts for i in range(4)):
            return None

        # Compute the swipe window bounds from starts
        tmin = min(starts)
        tmax = max(starts)
        span = tmax - tmin
        if span < self.MIN_MS or span > self.MAX_MS:
            return None

        # Validate monotone order for L->R or R->L with tolerance
        left_to_right_idxs  = (0, 1, 2, 3)
        right_to_left_idxs  = (3, 2, 1, 0)

        is_LR = self._is_monotonic_nondec(starts, left_to_right_idxs)
        is_RL = self._is_monotonic_nondec(starts, right_to_left_idxs)

        if not (is_LR or is_RL):
            # Out-of-order (e.g., pad 2 fired clearly before pad 1), reject
            return None

        # Optional: sanity that each pad actually engaged (still touching or had an end ≥ start)
        for i in range(4):
            if touch_end_time[i] < starts[i] and not is_touched[i]:
                # If a pad reports an end before its start and is not currently touched, data is inconsistent
                return None

        # Success — record cluster boundary & cooldown anchor
        self._since_ts = tmax           # ignore starts at or before this for the next detection
        self._last_fire_ts = now_ms

        return 'UP' if is_LR and not is_RL else 'DOWN'


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
        self.boop_count = 0 #20
        self.boop_mix = 0.0 #1.0
        self.boop_offset = 0
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

        # Stuff for scritch gesture detection (move finger back and forth across TCH1-4 quickly)
        self.touch_start_time = [None] * 4  # Track start time of touches
        self.touch_end_time = [None] * 4  # Track end time of touches
        self.is_touched = [False] * 4  # Track end time of touches
        self.last_expr_scritch = None # Last detected scritch direction (up or down)
        self.scritch_mix = 0 # Capped at 1.0
        self.scritch_mix_target = 0 # This can go a bit over 1.0 to maintain a more steady effect with continual scritching
        self.scritch_detector = ScritchDetector(eps_ms=500, min_ms=100, max_ms=1000, cooldown_ms=200)
        self.prevent_isr_update = False # Used to prevent race condition with ISR update during scritch effect
        
        # Stuff for remote boop handling
        self.boop_ended_last_loop = False
        self.boop_source = None # "local" or "remote"
        self.radio = lora_e5_radio.LoraE5Radio()

        # Setup the initial animation
        self.animation_list = animations.all()
        self.animation_index = 0
        self.next(0)

        #self.pallet = [[0.0,0.0,0.0] for i in range(1024)]
        self.pallet = [array.array("f", [0.0,0.0,0.0]) for i in range(1024)]
        self.pallet_functions[self.pallet_index](self.pallet)

        #                            0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  25  26  27  28  29  30  31
        self.boop_img = bytearray([  0,  0,  0,  0,  0,  0,171,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,182,163, 30,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
                                     0,  0,  0,  0,  0,  0,183,174, 30,  0, 30,175, 30,  0, 30,175, 30,  0,168,  0,159,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
                                     0,  0,  0,  0,  0,  0,171,  0,159,  0,171,  0,171,  0,171,  0,171,  0,173,159, 30,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
                                     0,  0,  0,  0,  0,  0,172,157, 30,  0, 30,154, 30,  0, 30,154, 30,  0,182, 10,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0])


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

    def boop(self, mix, boop_source):
        if mix > 1.0: mix = 1.0
        if mix < 0.0: mix = 0.0
        int_mix = int(255*(1.0-mix))

        for led in self.disp.leds:
                led.value[0] = (led.value[0]*int_mix)>>8
                led.value[1] = (led.value[1]*int_mix)>>8
                led.value[2] = (led.value[2]*int_mix)>>8
        boop_addr = self.boop_offset
        for y in range(3,-1,-1):
            for x in range(7):
                boop_addr &= 0x7F
                pixel = self.boop_img[boop_addr]
                self.disp.eye_grid[x][y].value[0] += pixel if self.boop_source == "local" else 0
                self.disp.eye_grid[x][y].value[1] += pixel
                self.disp.eye_grid[x][y].value[2] += pixel if self.boop_source == "local" else 0
                boop_addr += 1
            boop_addr += 25

    def scritch_effect(self, mix):
        if mix > 1.0: mix = 1.0
        if mix < 0.0: mix = 0.0
        for i in range(len(self.disp.leds)):
                self.disp.leds[i].r = (self.disp.leds[i].r * (1 - mix)) + (mix * 255)
                self.disp.leds[i].g = (self.disp.leds[i].g * (1 - mix)) + (mix * 5)
                self.disp.leds[i].b = (self.disp.leds[i].b * (1 - mix)) + (mix * 5)

    def isr_update(self,*args):
        if not self.prevent_isr_update:
            schedule(self.update, self)

    def touch_readings_update(self):
        self.touch.update()
        current_time = time.ticks_ms()
        prev_is_touched = self.is_touched
        curr_is_touched = [tc.level > 0.18 for tc in self.touch.channels]
        for ch_num, ch_is_touched in enumerate(curr_is_touched):
            if ch_is_touched and not prev_is_touched[ch_num]:
                self.touch_start_time[ch_num] = current_time

            if not ch_is_touched and prev_is_touched[ch_num]:
                self.touch_end_time[ch_num] = current_time
        self.is_touched = curr_is_touched
    
    def should_prevent_boop_detection(self, current_time):
        # Detect if user is likely performing scritch gesture. If so, prevent booping.

        if ( (not self.touch_start_time[0] and not self.touch_start_time[1] and self.touch_start_time[2] and not self.touch_start_time[3])
            or (self.touch.channels[0].level < 0.2 and self.touch.channels[1].level < 0.2  and self.touch.channels[3].level < 0.2) and \
                #(self.touch_start_time[0] and self.touch_start_time[1] and self.touch_start_time[2] and self.touch_start_time[3]) and \
                ((not  self.touch_start_time[0] or self.touch_start_time[0] < (current_time - 750)) and (not self.touch_start_time[1] or self.touch_start_time[1] < (current_time - 750)) and (not  self.touch_start_time[3] or self.touch_start_time[3] < (current_time - 750))) and \
                #(self.touch_end_time[0] and self.touch_end_time[1] and self.touch_end_time[3]) and \
                ((not self.touch_end_time[0] or self.touch_end_time[0] < (current_time - 300)) and (not self.touch_end_time[1] or self.touch_end_time[1] < (current_time - 300)) and (not self.touch_end_time[3] or self.touch_end_time[3] < (current_time - 300)))):
            print("should not prevent boop")

            return False
    
        return True
        
    def update(self,*args):
        current_time = time.ticks_ms()

        self.last_boop_level = self.boop_level
        self.boop_level = self.touch.channels[2].level
        if (self.boop_level > 0.3 and self.boop_count == 0 and not self.should_prevent_boop_detection(current_time)):
            if (self.last_boop_level <= 0.3):
                self.prevent_isr_update = True
                # Transmit LoRa packet to trigger boops on nearby badges
                self.radio.tx_boop()

                self.boop_offset = 0
                self.boop_mix    = 1.0
                self.boop_source = "local"

            # Start booping
            self.boop_count = 20
           
        elif self.radio.check_for_boop_message():
            # Detect LoRa packet from boop on nearby badge
            print("detected remote boop")
            self.boop_offset = 0
            self.boop_mix    = 1.0
            self.boop_count = 20
            self.boop_source = "remote"

        else:
            if self.boop_ended_last_loop:
                # Loop run after the one where boop_count reached 0
                if not self.radio.rx_is_armed:
                    self.radio.arm_radio_rx()
                self.boop_ended_last_loop = False
        
            # Fade out the boop
            if self.boop_count > 0:
                self.boop_count -= 1
                if self.boop_count == 0:
                    self.boop_ended_last_loop = True
            elif self.boop_mix > 0.0:
                    self.boop_mix -= 0.1

        dirn = self.scritch_detector.check(current_time, self.touch_start_time, self.is_touched, self.touch_end_time)
        if (dirn != self.last_expr_scritch):
            self.last_expr_scritch = dirn
            if dirn:
                self.scritch_mix_target = min(self.scritch_mix_target + 0.4, 1.3)
                # Prevent ISR update due to race condition:
                self.prevent_isr_update = True
        
        if self.scritch_mix_target > 0.0:
            self.scritch_mix = max(min(self.scritch_mix_target, 1.0) - 0.03, 0)
            self.scritch_mix_target = max(self.scritch_mix_target - 0.03, 0)
        
        
        if self.scritch_mix == 0 and self.boop_mix == 0:
            self.prevent_isr_update = False
        else:
            self.prevent_isr_update = True

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

        # Mix the boop effect and scritch effects in - then restore the state
        # when we're done so we don't interfere with any animation state
        if (self.boop_mix > 0.0) or (self.scritch_mix > 0.0):
            backup = [rgb_value(i.value[0], i.value[1], i.value[2]) for i in self.disp.downward]
        if (self.boop_mix > 0.0):
            self.boop(self.boop_mix, self.boop_source)
        if (self.scritch_mix > 0.0):
            self.scritch_effect(self.scritch_mix)
        self.disp.update()
        if (self.boop_mix > 0.0):
            self.boop_offset += 1
        if (self.boop_mix > 0.0) or (self.scritch_mix > 0.0):
            for i in range(len(backup)):
                self.disp.downward[i].copy(backup[i])

        gc.collect()

    def run(self):
        while True:
            # Run touch reading update more often than animtion update, to detect swipes/scritches better
            for _ in range(20):
                if self.prevent_isr_update:
                    # Shorter sleep time to compensate for not having isr update
                    time.sleep_ms(1)
                else:
                    time.sleep_ms(5)
                self.touch_readings_update()

            self.update()


global t
t = badge()
# t.run()
