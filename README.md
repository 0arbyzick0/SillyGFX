### SillyGFX - Ультимативная библиотека на MicroPython для графики!


## Особенности
- Полная поддержка кириллицы (все русские буквы в шрифтах 5x7 и 8x16)

- Аппаратное ускорение для SPI/I2C

- 20+ готовых эффектов анимации

- Оптимизированная работа даже на слабых устройствах

- Поддержка BMP/XBM изображений

## Установка
Перемести папку SillyGFX в папку /lib на твоём микроконтроллере!

## Быстрый тест
```python
from machine import I2C
from sillyGFX import SillyGFX

# Инициализация
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
gfx = SillyGFX(128, 64, i2c=i2c)

# Рисование
gfx.fill_screen(0)
gfx.rect(10, 10, 50, 30, 1, fill=True)
gfx.text("Привет!", 20, 25, 1)

# Эффекты
gfx.effects.crt_power_on()
gfx.update()
```

### Документация
## Основные методы
# Графика
```python
pixel(x, y, color)          # Точка
line(x1, y1, x2, y2, color) # Линия
rect(x, y, w, h, color, fill=False) # Прямоугольник
circle(x, y, r, color)      # Окружность
triangle(x1,y1,x2,y2,x3,y3,color) # Треугольник
```
# Текст
```python
text(text, x, y, color=1)   # Вывод текста
set_font(font_data, width, height) # Выбор шрифта
char(char, x, y, color)     # Один символ
```
# Изображения
```python
draw_bmp(filename, x, y)    # BMP изображение
draw_xbm(data, x, y, w, h)  # XBM изображение
```
# Эффекта (effects.py)
```python
# Основные
wipe(direction=0)           # Шторка (0=гориз, 1=верт)
crt_power_on(duration=1000) # Эффект включения ЭЛТ
pixel_rain(density=0.5)     # Падающие пиксели

# Текст
typewriter_text(text, x, y) # Печатная машинка
scroll_text(text, y)        # Бегущая строка

# Графика
particle_explosion(x,y)     # Взрыв частиц
ripple(x, y, radius)        # Круги на воде
parallax_scroll(layers)     # Параллакс-эффект

# Спецэффекты
tv_scanlines(cycles=5)      # Полосы ЭЛТ
crt_static(duration=1000)   # Телевизионные помехи
```

### Сравнение

| Функция |	SillyGFX | Adafruit GFX | U8g2 |
|         |          |              |      |
| Русские шрифты | ✅ | ❌ | ✅ |
|         |          |              |      |
| Эффекты |	20+ |	3	| 5 |
|         |          |              |      |
| Поддержка BMP |	✅ |	❌ |	✅ |
|         |          |              |      |
| Потребление RAM |	1.2KB |	2.5KB |	3KB |

### Поддерживаемые платы
- Raspberry Pi Pico
- ESP8266/ESP32
- STM32 (с MicroPython)
- Любые другие с 1MB+ Flash

### Участие в проекте
1. Форкните репозиторий
2. Создайте ветку (git checkout -b feature/new-effect)
3. Сделайте коммит (git commit -am 'Add cool effect')
4. Запушьте (git push origin feature/new-effect)
5. Откройте Pull Request

### Лицензия
MIT License - свободное использование с указанием авторства

## ✨ Ваш вклад в развитие проекта:
Поставьте звезду, если проект вам понравился!

## 💡 Вопросы? 
Открывайте Issue на GitHub!

спасибо всем за open-source
