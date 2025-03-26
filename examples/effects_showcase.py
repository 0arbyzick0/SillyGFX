from sillyGFX import SillyGFX
from machine import I2C
import time

i2c = I2C(0, scl=Pin(5), sda=Pin(4))
gfx = SillyGFX(128, 64, i2c=i2c)

effects = [
    ("Шторка", lambda: gfx.effects.wipe()),
    ("Пиксельный дождь", lambda: gfx.effects.pixel_rain()),
    ("ЭЛТ-полосы", lambda: gfx.effects.tv_scanlines()),
    ("Взрыв частиц", lambda: gfx.effects.particle_explosion(64, 32)),
    ("Печатная машинка", 
     lambda: gfx.effects.typewriter_text("SillyGFX рулит!", 10, 20))
]

for name, effect in effects:
    gfx.fill_screen(0)
    gfx.text(name, 10, 10, 1)
    gfx.update()
    time.sleep(1)
    
    effect()
    time.sleep(1)
