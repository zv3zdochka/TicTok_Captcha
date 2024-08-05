import cv2
import numpy as np

# Загрузка изображения
image = cv2.imread('img.png', cv2.IMREAD_COLOR)

# Преобразование изображения в оттенки серого
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Использование бинаризации для выделения контуров
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
cv2.imshow('binary', binary)
# Проведение жирных черных линий с помощью морфологической операции расширения
kernel = np.ones((1, 1), np.uint8)
dilated = cv2.dilate(binary, kernel, iterations=10)

cv2.imshow('Dilated Image', dilated)

# Поиск контуров
contours, _ = cv2.findContours(dilated, cv2.CAP_ANDROID, cv2.CHAIN_APPROX_SIMPLE)

# Отображение контуров
contour_image = np.zeros_like(image)

# Функция для проверки замкнутости контура

# Рисуем все замкнутые контуры
for contour in contours:
    cv2.drawContours(contour_image, [contour], -1, (0, 255, 0), 2)

# Сохранение изображения с контурами
cv2.imwrite('contours_image.jpg', contour_image)

# Отображение изображения
cv2.imshow('Contours', contour_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
