from sillyGFX import SillyGFX
from machine import I2C
import time

i2c = I2C(0, scl=Pin(5), sda=Pin(4))
gfx = SillyGFX(128, 64, i2c=i2c)

# Показ BMP (файл должен быть в формате 1-bit)
try:
    gfx.draw_bmp("logo.bmp", 0, 0)
    gfx.update()
except Exception as e:
    gfx.text("Error loading BMP", 10, 10, 1)
    gfx.update()

time.sleep(2)

# Генерация XBM на лету
xbm_data = [
    0b11000011,
    0b10000001,
    0b00111100,
    0b01000010,
    0b01000010,
    0b00111100,
    0b10000001,
    0b11000011
]
gfx.draw_xbm(xbm_data, 50, 20, 8, 8)
gfx.update()
