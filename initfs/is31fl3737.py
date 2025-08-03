from machine import I2C, Pin
from micropython import const
import math
import array

class rgb_value(object):
    def __init__(self, r=0, g=0, b=0, h=0, s=0, v=0):
        self.value = array.array("B", [0]*3)
        if h or s or v:
            self.hsv(h,s,v)
        else:
            self.value[0] = r
            self.value[1] = g
            self.value[2] = b
            self.addr = int(0)

    @property 
    def r(self): return self.value[0]
    @property
    def g(self): return self.value[1]
    @property
    def b(self): return self.value[2]
    @r.setter
    def r(self, value):
        self.value[0] = int(value)
    @g.setter
    def g(self, value):
        self.value[1] = int(value)
    @b.setter
    def b(self, value):
        self.value[2] = int(value)

    def __repr__(self):
        return f"<RGB: {self.value[0]}, {self.value[1]}, {self.value[2]}>"

    def set(self, r, g, b):
        self.value[0] = r
        self.value[1] = g
        self.value[2] = b

    def copy(self, other):
        self.value[0] = other.value[0]
        self.value[1] = other.value[1]
        self.value[2] = other.value[2]

    def hsv(self, hue, sat, val=255):
        """
        Set the pixel colour from HSV coordinates
        
        hue: floating point in the range of 0.0 to 1.0
        sat: floating point in the range of 0.0 to 1.0
        val: integer intensity in the range of 0 to 255
        """
        # Convert hue to an angle and compute the remainder mod 60
        hue = int(hue * 360) % 360
        rem = hue % 60

        # Convert saturation into a byte and do the rest in fixed point.
        sat = int(sat * 256)
        val = int(val)
        p = val * (256 - sat) >> 8
        q = val * (256 - (rem * sat // 60)) >> 8
        t = val * (256 - (60 - rem) * sat // 60) >> 8

        if hue < 60:
            self.r = val
            self.g = t
            self.b = p
        elif hue < 120:
            self.r = q
            self.g = val
            self.b = p
        elif hue < 180:
            self.r = p
            self.g = val
            self.b = t
        elif hue < 240:
            self.r = p
            self.g = q
            self.b = val
        elif hue < 300:
            self.r = t
            self.g = p
            self.b = val
        elif hue < 360:
            self.r = val
            self.g = p
            self.b = q

class is31fl3737(object):
    I2C_ADDR = 80

    REF_CONF      = const(0)
    REG_PAGE_SEL  = const(0xFD)
    REG_PAGE_LOCK = const(0xFE)
    REG_INT_MASK  = const(0xF0)
    REG_INT_STAT  = const(0xF1)

    # Page 0
    REG_LEDONOFF = const(0x0000) # ON or OFF state control for each LED. Write only.
    REG_LEDOPEN  = const(0x0018) # Open state for each LED. Read only.
    REG_LEDSHORT = const(0x0030) # Short state for each LED. Read only.

    # Registers in Page 1.
    REG_LEDPWM = const(0x0100) # PWM duty for each LED. Write only.

    # Registers in Page 2.
    REG_LEDABM = const(0x0200) # Auto breath mode for each LED. Write only.

    # Registers in Page 3.
    REG_CR    = const(0x0300) # Configuration Register. Write only.
    REG_GCC   = const(0x0301) # Global Current Control register. Write only.
    REG_ABM1  = const(0x0302) # Auto breath control register for ABM-1. Write only.
    REG_ABM2  = const(0x0306) # Auto breath control register for ABM-2. Write only.
    REG_ABM3  = const(0x030A) # Auto breath control register for ABM-3. Write only.
    REG_TUR   = const(0x030E) # Time update register. Write only.
    REG_SWPUR = const(0x030F) # SWy Pull-Up Resistor selection register. Write only.
    REG_CSPDR = const(0x0310) # CSx Pull-Down Resistor selection register. Write only.
    REG_RESET = const(0x0311) # Reset register. Read only.

    leds        = [rgb_value() for i in range(50)]
    left_eye    = []
    right_eye   = [leds[ 1],
                   leds[25], leds[13],
                   leds[38], leds[26], leds[14], leds[ 2],
                   leds[39], leds[27], leds[15], leds[ 3],
                   leds[40], leds[28], leds[16], leds[ 4], leds[37],
                   leds[41], leds[29], leds[17], leds[ 5], leds[ 6],
                   leds[30], leds[18], leds[42]]
    eye_grid    = [[leds[ 0], leds[ 0], leds[ 1], leds[ 0], leds[ 0]], # note: sideways so it's [x][y]
                   [leds[ 0], leds[25], leds[13], leds[ 0], leds[ 0]], # note 2: all '0's do not show
                   [leds[38], leds[26], leds[14], leds[ 2], leds[ 0]],
                   [leds[39], leds[27], leds[15], leds[ 3], leds[ 0]],
                   [leds[40], leds[28], leds[16], leds[ 4], leds[37]],
                   [leds[41], leds[29], leds[17], leds[ 5], leds[ 6]],
                   [leds[ 0], leds[30], leds[18], leds[ 0], leds[42]]]
    chin        = [leds[7],leds[8],leds[9],leds[10],leds[11],leds[12],leds[19],leds[20],leds[21],leds[22],leds[23],leds[24]]
    clockwise   = [leds[1],leds[2], leds[37], leds[6], leds[42], leds[3], leds[4], leds[5], leds[13], leds[14], leds[15],
                   leds[16],leds[17],leds[18],leds[30],leds[29],leds[28],leds[27],leds[26],leds[25],
                   leds[41],leds[40],leds[39],leds[38],
                   leds[24],leds[23],leds[22],leds[21],leds[20],leds[19],leds[12],leds[11],leds[10],leds[9],leds[8],leds[7]]
    downward    = [leds[42],leds[6],leds[37],
                   leds[2],leds[3],leds[4],leds[5],
                   leds[13],leds[14],leds[15],leds[16],leds[17],leds[18],
                   leds[1],
                   leds[25],leds[26],leds[27],leds[28],leds[29],leds[30],
                   leds[38],leds[39],leds[40],leds[41],
                   leds[24],leds[23],leds[22],leds[21],leds[20],leds[19],leds[7],leds[8],leds[10],leds[9],leds[12],leds[11]]

    def __init__(self):
        self.i2c = I2C(0, scl=Pin(1), sda=Pin(0))
        self.sdb = Pin(3, Pin.OUT)
        self.leds_raw = bytearray(256)
        self.brightness = 256

        for i in range(len(self.leds)-1):
            addr = int((i) % 12)
            if addr > 5: addr += 2
            addr += ((i) // 12)*0x30
            self.leds[i+1].addr = addr&0xFF

        self.power_on()
        self.init()

    def power_on(self):
        self.sdb(1)
    def power_off(self):
        self.sdb(0)

    def set_page(self, page_num:int):
        self.i2c.writeto_mem(self.I2C_ADDR, self.REG_PAGE_LOCK, b"\xC5")
        self.i2c.writeto_mem(self.I2C_ADDR, self.REG_PAGE_SEL, bytes([page_num & 0x3]))
    
    def read_paged_reg(self, addr):
        self.set_page(addr>>8)
        return self.i2c.readfrom_mem(self.I2C_ADDR, addr&0xFF, 1)
    
    def write_paged_reg(self, addr, value):
        self.set_page(addr>>8)
        self.i2c.writeto_mem(self.I2C_ADDR, addr&0xFF, bytes([value & 0xFF]))
    
    def init(self):
        # Read reset register to reset device.
        self.read_paged_reg(self.REG_RESET)
        # Clear software reset in configuration register.
        self.write_paged_reg(self.REG_CR, 0x01) # SSD bit
        # Clear state of all LEDs in internal buffer and sync buffer to device.
        self.set_page(0)
        self.i2c.writeto_mem(self.I2C_ADDR, 0, bytes([0xFF]*0x18)) # turn on all the LEDs
        self.set_page(2)
        self.i2c.writeto_mem(self.I2C_ADDR, 0, bytes([0x00]*0xBF)) # turn off auto breath mode

        for i in range(256):
            self.leds_raw[i] = 0
        self.update()
        self.set_page(3)
        self.i2c.writeto_mem(self.I2C_ADDR, 0, bytes([1]))
        self.i2c.writeto_mem(self.I2C_ADDR, 1, bytes([50]))

    def update(self):
        for i in range(48):
            led = self.leds[i]
            self.leds_raw[led.addr+0x00] = led.value[2]*self.brightness//256
            self.leds_raw[led.addr+0x10] = led.value[1]*self.brightness//256
            self.leds_raw[led.addr+0x20] = led.value[0]*self.brightness//256
        self.set_page(1)
        self.i2c.writeto_mem(self.I2C_ADDR,   0, self.leds_raw[  0:127])
        self.i2c.writeto_mem(self.I2C_ADDR, 128, self.leds_raw[128:255])

    def clear(self):
        for i in range(49):
            self.leds[i].set(0, 0, 0)
        self.update()
