from sillyGFX import SillyGFX
from machine import I2C, Pin
import time

i2c = I2C(0, scl=Pin(5), sda=Pin(4))
gfx = SillyGFX(128, 64, i2c=i2c)

# Эффектное включение
gfx.effects.crt_power_on()

# Основная графика
gfx.fill_screen(0)
gfx.rect(10, 10, 50, 30, 1, fill=True)
gfx.circle(90, 20, 15, 1)
gfx.triangle(30, 50, 50, 50, 40, 30, 1, fill=True)

# Работа с текстом
gfx.text("SillyGFX", 60, 10, 1)
gfx.text("Привет, мир!", 15, 45, 1)

gfx.update()
time.sleep(2)

# Эффектное выключение
gfx.effects.crt_power_off()
