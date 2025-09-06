# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Создаем непривилегированного пользователя
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
    && chown -R user:user /app
USER user

# Открываем порт
EXPOSE 8000

# Команда для запуска приложения
CMD ["python", "main.py"]
