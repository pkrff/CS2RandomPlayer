import random

# Создаём список чисел от 1 до 10
numbers = list(range(1, 11))

# Перемешиваем случайным образом
random.shuffle(numbers)

# Делим на два столбика по 5 чисел
left_column = numbers[:5]
right_column = numbers[5:]

# Сортируем каждый столбик по возрастанию
left_column.sort()
right_column.sort()

# Выводим результат
print("Команда 1   Команда 2")
print("---------   ---------")
for i in range(5):
    print(f"{left_column[i]:^9}   {right_column[i]:^9}")