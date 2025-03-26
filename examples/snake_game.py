from sillyGFX import SillyGFX
from machine import I2C, Pin
import time
import random

i2c = I2C(0, scl=Pin(5), sda=Pin(4))
gfx = SillyGFX(128, 64, i2c=i2c)

# Инициализация игры
snake = [[32, 16], [32, 24], [32, 32]]
food = [random.randint(0, 15)*8, random.randint(0, 7)*8]
direction = 0  # 0=вверх, 1=вправо, 2=вниз, 3=влево

while True:
    # Управление (можно адаптировать под ваши кнопки)
    new_dir = direction
    # Здесь должен быть код чтения кнопок
    
    # Движение змейки
    head = snake[0].copy()
    if direction == 0: head[1] -= 8
    elif direction == 1: head[0] += 8
    elif direction == 2: head[1] += 8
    else: head[0] -= 8
    
    # Проверка столкновений
    if (head in snake or 
        head[0] < 0 or head[0] >= 128 or 
        head[1] < 0 or head[1] >= 64):
        break
        
    # Проверка еды
    if head == food:
        food = [random.randint(0, 15)*8, random.randint(0, 7)*8]
    else:
        snake.pop()
    
    snake.insert(0, head)
    
    # Отрисовка
    gfx.fill_screen(0)
    for segment in snake:
        gfx.rect(segment[0], segment[1], 8, 8, 1, fill=True)
    gfx.rect(food[0], food[1], 8, 8, 1)
    gfx.update()
    time.sleep_ms(200)

# Конец игры
gfx.text("Game Over!", 40, 30, 1)
gfx.update()
