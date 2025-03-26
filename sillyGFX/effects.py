from time import ticks_ms, sleep_ms
from math import sin, cos
from random import random, randint
from sillyGFX.core import SillyGFX  # Импортируем основной класс


class GFXEffects:
    def __init__(self, gfx):
        self.gfx = gfx  # Принимаем любой объект с нужными методами
    
    def wipe(self, direction=0, speed=5):
        """Универсальная шторка без циклических импортов"""
        step = max(1, speed // 2)
        if direction == 0:  # Horizontal
            for x in range(0, self.gfx.width, step):
                self.gfx.rect(x, 0, step, self.gfx.height, 1, fill=True)
        else:  # Vertical
            for y in range(0, self.gfx.height, step):
                self.gfx.rect(0, y, self.gfx.width, step, 1, fill=True)
        self.gfx.update()
        
    def crt_power_on(self, duration=1000):
        """Оптимизированное включение через rect fill"""
        steps = 20
        for i in range(1, steps+1):
            # Плавное заполнение
            self.gfx.rect(0, 0, 
                         self.gfx.width, 
                         int(self.gfx.height * (i/steps)),
                         1, fill=True)
            # Случайные вспышки
            if i % 5 == 0:
                self.gfx.rect(randint(0, self.gfx.width//2),
                             randint(0, self.gfx.height//2),
                             randint(10,30),
                             randint(2,5),
                             1, fill=True)
            self.gfx.update()
            sleep_ms(duration//steps)

    def crt_power_off(self, duration=800):
        """Оптимизированное выключение"""
        steps = 20
        for i in range(steps):
            scale = 1 - (i/steps)
            w = int(self.gfx.width * scale)
            h = int(self.gfx.height * scale)
            x = (self.gfx.width - w) // 2
            y = (self.gfx.height - h) // 2
            
            self.gfx.fill_screen(0)
            self.gfx.rect(x, y, w, h, 1, fill=False)
            self.gfx.update()
            sleep_ms(duration//steps)
        
        self.gfx.fill_screen(0)
    
    def pixel_rain(self, density=1, cycles=200, color=1):
        """Эффект падающих пикселей с исправленной ошибкой"""
        width = self.gfx.width
        height = self.gfx.height
        
        for _ in range(cycles):
            # Сдвигаем все пиксели вниз
            for y in range(height-1, 0, -1):
                for x in range(width):
                    if self.gfx.fb.pixel(x, y-1):  # Используем напрямую framebuffer
                        self.gfx.fb.pixel(x, y, color)
                        self.gfx.fb.pixel(x, y-1, 0)
            
            # Добавляем новые капли
            if random() < density:
                x = randint(0, width-1)
                self.gfx.fb.pixel(x, 0, color)
            
            self.gfx.update()
            sleep_ms(50)
            
    def sparks(self, count=30, duration=2000):
        """Случайные искры на экране"""
        start = ticks_ms()
        while ticks_diff(ticks_ms(), start) < duration:
            self.gfx.pixel(randint(0, self.gfx.width-1), 
                          randint(0, self.gfx.height-1), 
                          1)
            if randint(0, 10) > 7:
                self.gfx.update()
                sleep_ms(50)
                
    def loading_bar(self, duration=3000):
        """Анимированный прогресс-бар"""
        for x in range(0, self.gfx.width, 3):
            self.gfx.rect(0, self.gfx.height-5, x, 3, 1, fill=True)
            self.gfx.update()
            sleep_ms(duration // (self.gfx.width//3))
        
    def tv_scanlines(self, cycles=5, intensity=0.7):
        """Эффект горизонтальных полос"""
        for _ in range(cycles):
            for y in range(0, self.gfx.height, 2):
                self.gfx.hline(0, y, self.gfx.width, 1)
                self.gfx.hline(0, y+1, self.gfx.width, 0)
            self.gfx.update()
            sleep_ms(100)
    
    # Восстанавливаем изображение
        for y in range(0, self.gfx.height, 2):
            self.gfx.hline(0, y, self.gfx.width, 1)
        self.gfx.update()
    
    def crt_static(self, duration=1000, speed=3):
        """Эффект телевизионных помех"""
        from random import getrandbits
        start = ticks_ms()
        while ticks_diff(ticks_ms(), start) < duration:
            for i in range(len(self.gfx.buffer)):
                self.gfx.buffer[i] = getrandbits(8)
            self.gfx.update(50 // speed)
        self.gfx.fill_screen(0)
        
    def typewriter_text(self, text, x, y, color=1, delay=50):
        """Эффект печатной машинки с мерцающим курсором"""
        for i in range(1, len(text)+1):
            # Очистка области
            self.gfx.fill_rect(x, y, 
                             self.gfx._font_width * len(text), 
                             self.gfx._font_height, 0)
            
            # Вывод текста
            self.gfx.text(text[:i], x, y, color)
            
            # Курсор
            if i < len(text):
                cursor_x = x + i * self.gfx._font_width
                self.gfx.vline(cursor_x, y, self.gfx._font_height, color)
            
            self.gfx.update()
            sleep_ms(delay)
        
        # Убираем курсор
        self.gfx.fill_rect(x + len(text)*self.gfx._font_width, y, 
                          2, self.gfx._font_height, 0)
        self.gfx.update()

    def fade_in(self, steps=10, delay=30):
        """Плавное появление через шум"""
        for i in range(steps):
            # Генерация шума с увеличивающейся плотностью
            for _ in range(i * 20):
                x = randint(0, self.gfx.width-1)
                y = randint(0, self.gfx.height-1)
                self.gfx.pixel(x, y, 1)
            self.gfx.update()
            sleep_ms(delay)
        self.gfx.fill_screen(1)

    def particle_explosion(self, x, y, particles=20, color=1):
        """Взрыв частиц с физикой"""
        positions = []
        for _ in range(particles):
            angle = random() * 2 * pi
            speed = 0.5 + random() * 2
            positions.append([x, y, cos(angle)*speed, sin(angle)*speed])
        
        for _ in range(25):  # Количество кадров анимации
            self.gfx.fill_screen(0)
            for p in positions:
                p[0] += p[2]  # X
                p[1] += p[3]  # Y
                p[3] += 0.1   # Гравитация
                
                if 0 <= p[0] < self.gfx.width and 0 <= p[1] < self.gfx.height:
                    self.gfx.pixel(int(p[0]), int(p[1]), color)
            
            self.gfx.update()
            sleep_ms(50)

    def ripple(self, x, y, max_radius, color=1):
        """Эффект кругов на воде"""
        for r in range(1, max_radius):
            self.gfx.circle(x, y, r, color)
            self.gfx.update()
            sleep_ms(30)
            self.gfx.circle(x, y, r, 0)  # Стираем предыдущий круг
        self.gfx.update()

    def parallax_scroll(self, layers, speed=2):
        """Параллакс-скроллинг для многослойной графики"""
        for offset in range(0, self.gfx.width*2, speed):
            self.gfx.fill_screen(0)
            for depth, layer in enumerate(layers):
                layer_width = len(layer[0]) if hasattr(layer[0], '__len__') else self.gfx.width
                pos = (offset // (depth+1)) % layer_width
                self.gfx.bitmap(layer, -pos, 0)
            self.gfx.update()
            sleep_ms(50)