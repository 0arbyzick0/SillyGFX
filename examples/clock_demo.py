from sillyGFX import SillyGFX
from machine import I2C, RTC
import time

i2c = I2C(0, scl=Pin(5), sda=Pin(4))
gfx = SillyGFX(128, 64, i2c=i2c)
rtc = RTC()

while True:
    now = rtc.datetime()
    hour, minute = now[4], now[5]
    
    gfx.fill_screen(0)
    
    # Циферблат
    gfx.circle(64, 32, 30, 1)
    
    # Стрелки
    angle_h = (hour % 12) * 30 - 90
    angle_m = minute * 6 - 90
    gfx.line(64, 32, 
            64 + int(20 * cos(angle_h * 3.14 / 180)),
            32 + int(20 * sin(angle_h * 3.14 / 180)), 1)
    gfx.line(64, 32,
            64 + int(25 * cos(angle_m * 3.14 / 180)),
            32 + int(25 * sin(angle_m * 3.14 / 180)), 1)
    
    # Цифровое время
    time_str = "{:02d}:{:02d}".format(hour, minute)
    gfx.text(time_str, 50, 50, 1)
    
    gfx.update()
    time.sleep(1)
