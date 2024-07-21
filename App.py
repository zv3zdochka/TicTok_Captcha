import pygame
import sys
from pygame.locals import *
from pynput.mouse import Listener

# Инициализация Pygame
pygame.init()

# Загрузка изображения фона
background_image = '4cd190c1-ba76-4ddc-b544-bd55c918c568.png'
background = pygame.image.load(background_image)

# Размер экрана
screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

# Масштабирование изображения под размер экрана
background = pygame.transform.scale(background, (screen_width, screen_height))

# Переменная для записи состояния
recording = False
clicks = []

# Файл для записи координат
output_file = 'mouse_movements.txt'

# Функция для обработки событий мыши
def on_move(x, y):
    global recording
    if recording:
        with open(output_file, 'a') as f:
            f.write(f'Move: {x}, {y}\n')

def on_click(x, y, button, pressed):
    global recording
    if recording:
        action = 'Pressed' if pressed else 'Released'
        with open(output_file, 'a') as f:
            f.write(f'Click {action}: {x}, {y}\n')

# Запуск слушателя для мыши
mouse_listener = Listener(on_move=on_move, on_click=on_click)
mouse_listener.start()

# Основной цикл приложения
running = True
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_r:  # Нажатие клавиши 'r' для начала/остановки записи
                recording = not recording
                if not recording:
                    print(f"Запись остановлена, координаты сохранены в {output_file}")
            if event.key == K_q:  # Нажатие клавиши 'q' для выхода
                running = False

    # Отрисовка фона
    screen.blit(background, (0, 0))
    pygame.display.flip()

# Остановка слушателя
mouse_listener.stop()

# Завершение работы Pygame
pygame.quit()
sys.exit()
