class led_highlight:
    def __init__(self, badge):
        self.badge = badge
        self.led_num = 0
    
    def update(self):
        for i in range(len(self.badge.disp.leds)):
            self.badge.disp.leds[i].hsv(1.0, 0.0, 0)
        self.badge.disp.leds[self.led_num].hsv(1.0, 0.0, 200)

    def button(self):
        self.led_num += 1
        if self.led_num > len(self.badge.disp.leds):
            self.led_num = 0
        print("led: %d"%self.led_num)
