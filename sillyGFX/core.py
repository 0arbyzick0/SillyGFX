from micropython import const
from time import ticks_us, ticks_diff, sleep_ms
from random import randint, random
from math import sin, cos
import sillyGFX.fonts, time, uctypes, framebuf, ssd1306
from sillyGFX.fonts import get_font_5x7
from machine import SPI, Pin
# Константы стилей
SOLID = const(0)
DOTTED = const(1)
FILL = const(1)
NO_FILL = const(0)
DASHED = const(2)
HORIZONTAL = const(0)
VERTICAL = const(1)
DIAGONAL = const(2)
# Константы выравнивания текста
LEFT = const(0)
CENTER = const(1)
RIGHT = const(2)

MONO_HLSB = framebuf.MONO_HLSB  # 1-bit монохромный (горизонтальная упаковка)
MONO_VLSB = framebuf.MONO_VLSB  # 1-bit монохромный (вертикальная упаковка)
RGB565 = framebuf.RGB565       # 16-bit цветной
GS4_HMSB = framebuf.GS4_HMSB   # 4-bit градации серого

class SillyGFX:
    def __init__(self, width=128, height=64, i2c=None, i2c_addr=0x3C):
        self.width = width
        self.height = height
        self.format = framebuf.MONO_VLSB  # Обязательно для SSD1306!
        self.buffer = bytearray((width * height + 7) // 8)
        self.fb = framebuf.FrameBuffer(self.buffer, width, height, self.format)
        
        if i2c:
            self.init_i2c(i2c, i2c_addr)
    
    def init_i2c(self, i2c, addr=0x3C):
        """Инициализация I2C дисплея"""
        self.i2c = i2c
        self.i2c_addr = addr
        
        # Команды инициализации SSD1306
        init_seq = bytearray([
            0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40,
            0x8D, 0x14, 0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12,
            0x81, 0xCF, 0xD9, 0xF1, 0xDB, 0x40, 0xA4, 0xA6,
            0xAF
        ])
        
        # Отправка команд
        for cmd in init_seq:
            self._i2c_write(0x00, cmd)
            time.sleep_ms(1)
    
    def _i2c_write(self, reg, data):
        """Запись в I2C"""
        self.i2c.writeto(self.i2c_addr, bytearray([reg, data]))
    
    def update(self):
        """Ультра-надёжное обновление экрана"""
        try:
            # 1. Установка области вывода (командный режим: 0x00)
            self.i2c.writeto(self.i2c_addr, b'\x00\x21\x00\x7F')  # Все столбцы (0-127)
            self.i2c.writeto(self.i2c_addr, b'\x00\x22\x00\x07')  # Все страницы (0-7)
            
            # 2. Отправка данных (режим данных: 0x40)
            self.i2c.writeto(self.i2c_addr, b'\x40' + self.buffer)
            
        except Exception as e:
            print("Ошибка обновления:", e)
            # Аварийный сброс
            self.reset_display()  


    def _fallback_update(self, x=0, y=0, w=None, h=None):
        """Медленный, но надёжный метод для любых дисплеев"""
        w = w if w is not None else self.width
        h = h if h is not None else self.height
        
        buf = memoryview(self.buffer)
        bytes_per_row = (self.width + 7) // 8
        
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                byte = buf[(yy // 8) * bytes_per_row + (xx // 8)]
                bit = byte & (1 << (yy % 8))
                self.display.pixel(xx, yy, bit)
            
    def swap_buffers(self):
        """Безопасное переключение буферов"""
        self.buffer, self.back_buffer = self.back_buffer, self.buffer
        self.update()
    
    def _update_spi(self):
        """Исправленная версия для SSD1306"""
        self.dc_pin.value(1)
        self.cs_pin.value(0)
        
        # Для SSD1306 отправляем данные страницами по 8 строк
        for page in range(0, self.height // 8):
            # Устанавливаем текущую страницу (команда 0xB0..0xB7)
            self.dc_pin.value(0)
            self.spi.write(bytearray([0xB0 | page, 0x00, 0x10]))
            self.dc_pin.value(1)
            
            # Отправляем строку из буфера
            start = page * self.width
            end = start + self.width
            self.spi.write(self.buffer[start:end])
        
        self.cs_pin.value(1)
    
    def _update_i2c(self):
        """Оптимизированный I2C с пачковой отправкой"""
        buf = bytearray([0x40]) + self.buffer  # 0x40 = Co=0, D/C=1 (данные)
        for i in range(0, len(buf), 32):  # Отправляем по 32 байта (макс. для I2C)
            self.i2c.writeto(self.i2c_addr, buf[i:i+32])

    # --- БАЗОВЫЕ МЕТОДЫ ---
    def _safety_net(self):
        """Ловим все промахи до их удара!"""
        if not hasattr(self, 'oled'):
            raise RuntimeError("Дисплей не подключен! Передай экран в конструктор.")
        if not hasattr(self.oled, 'pixel'):
            raise AttributeError("У экрана нет pixel() — странный дисплей!")
    
    def fill_screen(self, color=0):
        """Заливка экрана"""
        self.fb.fill(color)
        
    def fill_area(self, x, y, w, h, color=1):
        """Оптимизированная заливка прямоугольной области"""
        x_end = min(x + w, self.width)
        y_end = min(y + h, self.height)
        
        for yy in range(max(y, 0), y_end):
            self.hline(max(x, 0), yy, x_end - max(x, 0), color)
            
    def gradient_fill(self, color_start=0, color_end=1):
        """Вертикальный градиент (для будущей цветной версии)"""
        for y in range(self.height):
            ratio = y / self.height
            color = color_start if ratio < 0.5 else color_end
            self.hline(0, y, self.width, color)
        
    def clear(self):
        """Очистка экрана (алиас для fill_screen)"""
        self.fill_screen(0)
    
    def scroll(self, dx, dy):
        """Прокрутка содержимого буфера"""
        new_buffer = bytearray(len(self.buffer))
        for y in range(self.height):
            for x in range(self.width):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.pixel(x, y):
                        new_buffer[(ny // 8) * self.width + nx] ^= (1 << (ny % 8))
        self.buffer = new_buffer

    def rotate(self, degrees):
        """Поворот буфера на 90/180/270 градусов"""
        # Реализация поворота
        pass

    # --- ГРАФИКА ---
    def draw_bitmap(self, bitmap, x, y, w, h, color=1):
        """Отрисовка монохромного bitmap (1 бит на пиксель)"""
        for dy in range(h):
            for dx in range(w):
                byte = bitmap[dy * ((w + 7) // 8) + (dx // 8)]
                if byte & (1 << (dx % 8)):
                    self.pixel(x + dx, y + dy, color)
        self.update(1)  # Или прямой вызов self.oled.show()
    
    def draw_bmp(self, filename, x, y, threshold=128, dither=False):
        """Поддержка 1-bit, 8-bit и 24-bit BMP"""
        try:
            with open(filename, 'rb') as f:
                # Чтение заголовка
                header = f.read(54)
                if len(header) < 54 or header[0] != 0x42 or header[1] != 0x4D:
                    return
                    
                # Параметры изображения
                width = int.from_bytes(header[18:22], 'little')
                height = int.from_bytes(header[22:26], 'little')
                bpp = int.from_bytes(header[28:30], 'little')
                data_offset = int.from_bytes(header[10:14], 'little')
                
                # Чтение палитры для 8-bit
                palette = []
                if bpp == 8:
                    f.seek(54)  # Читаем палитру после заголовка
                    palette_data = f.read(1024)  # 256 цветов по 4 байта
                    for i in range(256):
                        blue = palette_data[i*4]
                        green = palette_data[i*4+1]
                        red = palette_data[i*4+2]
                        palette.append((red, green, blue))
                
                # Переход к данным пикселей
                f.seek(data_offset)
                row_size = ((width * bpp + 31) // 32) * 4
                
                for row in range(height):
                    row_data = f.read(row_size)
                    if not row_data:
                        break
                        
                    for col in range(width):
                        if bpp == 1:
                            # 1-bit
                            byte = row_data[col//8]
                            pixel = (byte >> (7 - (col%8))) & 1
                        elif bpp == 8:
                            # 8-bit
                            index = row_data[col]
                            red, green, blue = palette[index]
                            brightness = 0.299*red + 0.587*green + 0.114*blue
                            pixel = 1 if brightness > threshold else 0
                        else:
                            # 24-bit
                            offset = col*3
                            if offset+2 >= len(row_data):
                                continue
                            blue, green, red = row_data[offset], row_data[offset+1], row_data[offset+2]
                            brightness = 0.299*red + 0.587*green + 0.114*blue
                            pixel = 1 if brightness > threshold else 0
                        
                        # Дизеринг
                        if dither and pixel == 0 and random()*255 < brightness%256:
                            pixel = 1
                        
                        # Отрисовка
                        self.pixel(x + col, y + (height - 1 - row), pixel)
                        
        except Exception as e:
            print("BMP Error:", e)
            
    def draw_xbm(self, xbm_data, x, y, w, h, color=1, is_file=False):
        """
        Рисует XBM изображение. Поддерживает:
        - Готовые bytearray (is_file=False)
        - Непосредственно .xbm файлы (is_file=True)
        """
        if is_file:
            try:
                # Чтение и парсинг файла
                with open(xbm_data, 'r') as f:
                    content = f.read()
                
                # Автоматическое извлечение данных
                start = content.find('{') + 1
                end = content.find('}')
                data_str = content[start:end].replace('0x', '').replace(',', ' ').split()
                
                # Конвертация в bytearray
                xbm_data = bytearray([int(b, 16) for b in data_str if b])
            except Exception as e:
                print(f"XBM Error: {e}")
                return

        # Отрисовка (старый код)
        for dy in range(h):
            for dx in range(w):
                byte = xbm_data[dy * ((w + 7) // 8) + (dx // 8)]
                if byte & (1 << (dx % 8)):
                    self.pixel(x + dx, y + dy, color)
        self.update(1)  # Или прямой вызов self.oled.show()

    def line(self, x0, y0, x1, y1, color=1, style=SOLID):
        """Расширенная линия с поддержкой DASHED"""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        dot_counter = 0
        
        dash_length = 3 if style == DASHED else 1
        
        while True:
            if (style == SOLID or 
                (style == DOTTED and dot_counter % 2 == 0) or
                (style == DASHED and dot_counter % (dash_length * 2) < dash_length)):
                self.pixel(x0, y0, color)
            dot_counter += 1
            
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
        
    def hline(self, x, y, w, color=1, style=SOLID):
        """Оптимизированная горизонтальная линия со стилями"""
        if y < 0 or y >= self.height:
            return
            
        x_start = max(x, 0)
        x_end = min(x + w, self.width)
        dot_counter = x_start if style != SOLID else 0
        
        for x_pos in range(x_start, x_end):
            if style == SOLID or (style == DOTTED and dot_counter % 2 == 0):
                self.pixel(x_pos, y, color)
            dot_counter += 1

    def vline(self, x, y, h, color=1, style=SOLID):
        """Оптимизированная вертикальная линия со стилями"""
        if x < 0 or x >= self.width:
            return
            
        y_start = max(y, 0)
        y_end = min(y + h, self.height)
        dot_counter = y_start if style != SOLID else 0
        
        for y_pos in range(y_start, y_end):
            if style == SOLID or (style == DOTTED and dot_counter % 2 == 0):
                self.pixel(x, y_pos, color)
            dot_counter += 1

    def rect(self, x, y, w, h, color=1, fill=NO_FILL, style=SOLID):
        """Оптимизированный прямоугольник с заливкой и стилями"""
        if fill:
            for dy in range(h):
                self.hline(x, y+dy, w, color)
        else:
            # Оптимизированные границы
            self.hline(x, y, w, color, style)  # Верх
            self.hline(x, y + h - 1, w, color, style)  # Низ
            self.vline(x, y, h, color, style)  # Лево
            self.vline(x + w - 1, y, h, color, style)  # Право
    
    def triangle(self, x0, y0, x1, y1, x2, y2, color=1, fill=NO_FILL):
        """Треугольник с заливкой"""
        if fill:
            # Алгоритм заливки треугольника
            def draw_flat_bottom_triangle(x1, y1, x2, y2, x3, y3):
                for y in range(y1, y2 + 1):
                    x_start = x1 + (x2 - x1) * (y - y1) // (y2 - y1)
                    x_end = x1 + (x3 - x1) * (y - y1) // (y3 - y1)
                    self.line(x_start, y, x_end, y, color)
            
            # Сортировка вершин по Y
            if y0 > y1: x0, y0, x1, y1 = x1, y1, x0, y0
            if y0 > y2: x0, y0, x2, y2 = x2, y2, x0, y0
            if y1 > y2: x1, y1, x2, y2 = x2, y2, x1, y1
            
            if y1 == y2:
                draw_flat_bottom_triangle(x0, y0, x1, y1, x2, y2)
            elif y0 == y1:
                draw_flat_top_triangle(x0, y0, x1, y1, x2, y2)
            else:
                # Разделение на два треугольника
                x_mid = x0 + (x2 - x0) * (y1 - y0) // (y2 - y0)
                draw_flat_bottom_triangle(x0, y0, x1, y1, x_mid, y1)
                draw_flat_top_triangle(x1, y1, x_mid, y1, x2, y2)
        else:
            self.line(x0, y0, x1, y1, color)
            self.line(x1, y1, x2, y2, color)
            self.line(x2, y2, x0, y0, color)

    def rounded_rect(self, x, y, w, h, r, color=1, fill=NO_FILL):
        """Прямоугольник со скругленными углами"""
        if fill:
            # Заливка центра
            self.rect(x + r, y, w - 2 * r, h, color, FILL)
            self.rect(x, y + r, w, h - 2 * r, color, FILL)
            # Заливка углов
            self.circle(x + r, y + r, r, color, FILL)
            self.circle(x + w - r - 1, y + r, r, color, FILL)
            self.circle(x + r, y + h - r - 1, r, color, FILL)
            self.circle(x + w - r - 1, y + h - r - 1, r, color, FILL)
        else:
            # Рамка
            self.line(x + r, y, x + w - r - 1, y, color)
            self.line(x + r, y + h - 1, x + w - r - 1, y + h - 1, color)
            self.line(x, y + r, x, y + h - r - 1, color)
            self.line(x + w - 1, y + r, x + w - 1, y + h - r - 1, color)
            # Углы
            self.circle(x + r, y + r, r, color, NO_FILL)
            self.circle(x + w - r - 1, y + r, r, color, NO_FILL)
            self.circle(x + r, y + h - r - 1, r, color, NO_FILL)
            self.circle(x + w - r - 1, y + h - r - 1, r, color, NO_FILL)

    def circle(self, x, y, r, color=1, fill=NO_FILL):
        """Оптимизированная окружность с заливкой"""
        f = 1 - r
        ddf_x = 1
        ddf_y = -2 * r
        x0 = 0
        y0 = r
        
        while x0 <= y0:
            if fill:
                # Заливка оптимизирована через hline
                self.hline(x - y0, y + x0, 2 * y0 + 1, color)
                self.hline(x - y0, y - x0, 2 * y0 + 1, color)
                self.hline(x - x0, y + y0, 2 * x0 + 1, color)
                self.hline(x - x0, y - y0, 2 * x0 + 1, color)
            else:
                # Только граница
                self.pixel(x + x0, y + y0, color)
                self.pixel(x - x0, y + y0, color)
                self.pixel(x + x0, y - y0, color)
                self.pixel(x - x0, y - y0, color)
                self.pixel(x + y0, y + x0, color)
                self.pixel(x - y0, y + x0, color)
                self.pixel(x + y0, y - x0, color)
                self.pixel(x - y0, y - x0, color)
            
            if f >= 0:
                y0 -= 1
                ddf_y += 2
                f += ddf_y
            x0 += 1
            ddf_x += 2
            f += ddf_x
    # --- ТЕКСТ ---
    def char(self, char, x, y, color=1):
        """Вывод одного символа"""
        self.text(char, x, y, color)
        
    def set_font(self, font_data, width=5, height=7):
        """Безопасная установка шрифта с проверкой данных"""
        try:
            # Проверяем, что font_data - словарь
            if not isinstance(font_data, dict):
                raise ValueError("Font data must be a dictionary")
            
            # Проверяем первый доступный символ
            sample_char = next(iter(font_data.values()))
            if not isinstance(sample_char, (list, bytes, bytearray)):
                raise ValueError("Each character must be a list/bytes of pixel data")
                
            # Устанавливаем шрифт
            self._font = font_data
            self._font_width = width
            self._font_height = height
            
            print(f"Font set: {len(font_data)} chars, {width}x{height} pixels")
            
        except Exception as e:
            print(f"Font loading error: {e}")
            # Устанавливаем шрифт по умолчанию
            self._font = {'?': [0x00, 0x00, 0x00, 0x00, 0x00]}
            self._font_width = 5
            self._font_height = 7

    def text(self, text, x, y, color=1):
        """Вывод текста с принудительной обработкой кириллицы"""
        for char in text:
            # Получаем Unicode-код символа
            char_code = ord(char)
            
            # Ручная подмена проблемных символов
            if char_code == 0x418:  # Кириллическая 'И'
                char_data = self._font.get('И', [0]*5)
            elif char_code == 0x439:  # Кириллическая 'й'
                char_data = self._font.get('й', [0]*5)
            else:
                char_data = self._font.get(char, [0]*5)
            
            # Отрисовка
            for col in range(len(char_data)):
                for row in range(7):
                    if char_data[col] & (1 << row):
                        self.pixel(x+col, y+row, color)
            x += len(char_data) + 1

    def pixel(self, x, y, color):
        """Установка пикселя с проверкой границ"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.fb.pixel(x, y, color)                          
    
    # --- ДРУГОЕ ---
    