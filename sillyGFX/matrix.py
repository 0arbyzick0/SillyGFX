from machine import Pin, SPI, I2C
import framebuf, time, neopixel, sillyGFX.fonts, time, uctypes, framebuf, ssd1306
from micropython import const
from time import ticks_us, ticks_diff, sleep_ms
from random import randint, random
from math import sin, cos
from sillyGFX.fonts import get_font_5x7
from machine import SPI, Pin

MONO_HLSB = framebuf.MONO_HLSB  # 1-bit монохромный (горизонтальная упаковка)
MONO_VLSB = framebuf.MONO_VLSB  # 1-bit монохромный (вертикальная упаковка)
RGB565 = framebuf.RGB565       # 16-bit цветной
GS4_HMSB = framebuf.GS4_HMSB   # 4-bit градации серого

class Matrix:
    def __init__(self, width, height, format=MONO_VLSB, interface='spi', **kwargs):
        """
        Универсальный контроллер матриц
        
        :param width: Ширина в пикселях
        :param height: Высота в пикселях
        :param interface: 'spi', 'i2c', 'onewire'
        :param kwargs: Параметры интерфейса
        """
        self.width = width
        self.height = height
        self.interface = interface
        
        # Инициализация интерфейса
        if interface == 'spi':
            self._init_spi(**kwargs)
        elif interface == 'i2c':
            self._init_i2c(**kwargs)
        elif interface == 'onewire':
            self._init_onewire(**kwargs)
        else:
            raise ValueError("Unsupported interface")
        
        # Настройка буфера
        self._init_buffer()
    
    def _init_spi(self, spi_bus=1, baudrate=10_000_000, **kwargs):
        """Инициализация SPI матрицы (MAX7219 и аналоги)"""
        self.spi = SPI(spi_bus, baudrate=baudrate, 
                      polarity=0, phase=0,
                      sck=Pin(kwargs.get('sck', 14)),
                      mosi=Pin(kwargs.get('mosi', 13)))
        self.cs = Pin(kwargs.get('cs', 15), Pin.OUT)
        
    def _update_spi(self):
        """Вывод на SPI матрицу"""
        for y in range(8):  # Для 8x8 матриц
            row_data = 0
            for x in range(8):
                if self.fb.pixel(x, y):
                    row_data |= (1 << (7 - x))
            
            self.cs(0)
            self.spi.write(bytes([y + 1, row_data]))
            self.cs(1)
        
        
    def _init_i2c(self, i2c_bus=0, address=0x70, **kwargs):
        """Инициализация I2C матрицы (HT16K33 и аналоги)"""
        self.i2c = I2C(i2c_bus, 
                      scl=Pin(kwargs.get('scl', 5)),
                      sda=Pin(kwargs.get('sda', 4)))
        self.address = address
        self._i2c_init_seq()
    
    def _i2c_init_seq(self):
        """Последовательность инициализации HT16K33"""
        self.i2c.writeto(self.address, b'\x21')  # Включить осциллятор
        self.i2c.writeto(self.address, b'\x81')  # Включить дисплей
        self.i2c.writeto(self.address, b'\xEF')  # Макс. яркость

    def _update_i2c(self):
        """Вывод на I2C матрицу"""
        display_buffer = bytearray(16)  # HT16K33 буфер
        for y in range(8):
            row_data = 0
            for x in range(8):
                if self.fb.pixel(x, y):
                    row_data |= (1 << x)
            display_buffer[y*2] = row_data & 0xFF
            display_buffer[y*2+1] = row_data >> 8
        
        self.i2c.writeto_mem(self.address, 0x00, display_buffer)
    
    def _init_onewire(self, pin=13, **kwargs):
        """Инициализация однопроводной матрицы (WS2812/NeoPixel)"""
        self.np = neopixel.NeoPixel(Pin(pin), 
                                  self.width * self.height,
                                  bpp=kwargs.get('bpp', 3))
    
    def _update_onewire(self):
        """Вывод буфера на однопроводную матрицу"""
        for i in range(self.width * self.height):
            r = self.buffer[3*i]
            g = self.buffer[3*i+1]
            b = self.buffer[3*i+2]
            self.np[i] = (r, g, b)
        self.np.write()
    
    
    def _init_buffer(self):
        """Создание графического буфера"""
        if self.interface == 'onewire':
            self.buffer = bytearray(self.width * self.height * 3)
        else:
            self.buffer = bytearray((self.width * self.height + 7) // 8)
            self.fb = framebuf.FrameBuffer(self.buffer, 
                                         self.width, 
                                         self.height, 
                                         framebuf.MONO_VLSB)
    
    def update(self):
        """Обновление матрицы"""
        if self.interface == 'onewire':
            self._update_onewire()
        elif self.interface == 'spi':
            self._update_spi()
    
    def set_brightness(self, level):
        """Установка яркости (0-15)"""
        if self.interface == 'spi':
            self.cs(0)
            self.spi.write(bytes([0x0A, min(15, level)]))
            self.cs(1)
        elif self.interface == 'i2c':
            self.i2c.writeto(self.address, bytes([0xE0 | min(15, level)]))
        elif self.interface == 'onewire':
            # Для NeoPixel яркость регулируется программно
            pass

    def clear(self):
        """Очистка матрицы"""
        if self.interface == 'onewire':
            self.buffer = bytearray(len(self.buffer))
        else:
            self.fb.fill(0)
        self.update()
        
    def set_font(self, font_data, width=5, height=7):
        """Безопасная установка шрифта"""
        self._font = font_data  # Основное хранилище
        self._font_width = width
        self._font_height = height
        
        # Автоматическая загрузка стандартного шрифта при ошибке
        if not isinstance(font_data, dict):
            from sillyGFX.fonts.font5x7 import DATA as default_font
            self._font = default_font
            print("Внимание: передан неверный шрифт, загружен стандартный")
    
    def text(self, text, x, y, color=1, spacing=1):
        """Вывод текста на матрицу"""
        if not hasattr(self, '_font'):
            self.set_font()  # Используем шрифт по умолчанию
            
        for char in text:
            char_data = self._font.get(char, self._font.get('?'))
            for col in range(self._font_width):
                for row in range(self._font_height):
                    if char_data[col] & (1 << row):
                        self.pixel(x + col, y + row, color)
            x += self._font_width + spacing
    
    def scroll_text(self, text, color=1, speed=50):
        """Прокрутка текста справа налево"""
        text_width = len(text) * (self._font_width + 1)
        for x_pos in range(self.width, -text_width, -1):
            self.clear()
            self.text(text, x_pos, 1, color)
            self.update()
            time.sleep_ms(speed)
    
    def fill_screen(self, x, y, w, h, color=1):
        """Заливка области (нужна для wipe и других эффектов)"""
        for dy in range(h):
            for dx in range(w):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.pixel(nx, ny, color)
    
    def hline(self, x, y, w, color=1):
        """Горизонтальная линия (нужна для scanlines)"""
        for dx in range(w):
            nx = x + dx
            if 0 <= nx < self.width and 0 <= y < self.height:
                self.pixel(nx, y, color)
    
    @property
    def fb(self):
        """Свойство для совместимости с эффектами, ожидающими FrameBuffer"""
        if not hasattr(self, '_fb_compat'):
            # Создаем обертку для совместимости
            class FBCompat:
                def __init__(self, matrix):
                    self.matrix = matrix
                
                def pixel(self, x, y, color=None):
                    if color is not None:
                        self.matrix.pixel(x, y, color)
                    # Для чтения пикселя нужно реализовать отдельно
                    return 0  # Заглушка
                    
            self._fb_compat = FBCompat(self)
        return self._fb_compat
