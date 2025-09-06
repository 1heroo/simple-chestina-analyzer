#!/bin/bash

# Создание директории для SSL сертификатов
mkdir -p /ssl

# Генерация приватного ключа
openssl genrsa -out /ssl/nginx.key 2048

# Генерация self-signed сертификата на 365 дней
openssl req -new -x509 -key /ssl/nginx.key -out /ssl/nginx.crt -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo "SSL certificates generated successfully!"
