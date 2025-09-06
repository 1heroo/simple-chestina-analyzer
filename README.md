# Pronunciation Assessment API

Модульное FastAPI приложение для анализа произношения речи с использованием Azure Cognitive Services. Разработано для мобильных приложений с масштабируемой архитектурой и Docker поддержкой.

## Архитектура

```
azure_script_f/
├── .env                     # Переменные окружения
├── .dockerignore           # Исключения для Docker
├── Dockerfile              # Docker образ приложения
├── docker-compose.local.yml # Docker Compose для разработки
├── docker-compose.prod.yml  # Docker Compose для продакшена
├── main.py                 # Главное приложение FastAPI
├── requirements.txt        # Python зависимости
├── README.md
├── nginx/                  # Конфигурации Nginx
│   ├── local.conf         # Локальная конфигурация
│   └── prod.conf          # Продакшен конфигурация
└── src/                   # Исходный код приложения
    ├── __init__.py        # Инициализация пакета
    ├── config.py          # Конфигурация и настройки
    ├── models.py          # Pydantic модели данных
    ├── services.py        # Бизнес-логика и сервисы
    └── routes.py          # API маршруты
```

## Возможности

- **Анализ произношения**: Оценка качества произношения речи
- **Детальный анализ**: Анализ на уровне слов и фонем
- **Пакетная обработка**: Анализ нескольких аудио файлов
- **CORS поддержка**: Готовность для мобильных приложений
- **Мониторинг**: Health checks и логирование
- **Масштабируемость**: Модульная архитектура

## API Эндпоинты

### Основные
- `POST /api/v1/pronunciation-assessment` - Анализ произношения
- `POST /api/v1/pronunciation-assessment/detailed` - Детальный анализ
- `POST /api/v1/pronunciation-assessment/batch` - Пакетный анализ

### Служебные
- `GET /api/v1/health` - Проверка здоровья сервиса
- `GET /api/v1/info` - Информация о сервисе
- `GET /api/v1/languages` - Поддерживаемые языки
- `GET /docs` - Swagger документация

## Установка и запуск

### Локальная разработка (без Docker)

#### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

#### 2. Настройка переменных окружения
Создайте файл `.env` или настройте переменные:
```bash
AZURE_SPEECH_KEY=your_azure_key
AZURE_SPEECH_REGION=eastus
APP_DEBUG=true
```

#### 3. Запуск сервера
```bash
python main.py
```

### Docker разработка

#### 1. Локальная разработка с Docker
```bash
# Запуск только API
docker-compose -f docker-compose.local.yml up pronunciation-api

# Запуск с Nginx
docker-compose -f docker-compose.local.yml --profile with-nginx up
```

#### 2. Продакшен с Docker
```bash
# Основные сервисы
docker-compose -f docker-compose.prod.yml up -d

# С мониторингом (Prometheus + Grafana)
docker-compose -f docker-compose.prod.yml --profile with-monitoring up -d

# С Redis кэшированием
docker-compose -f docker-compose.prod.yml --profile with-redis up -d
```

### Docker команды

```bash
# Сборка образа
docker build -t pronunciation-api .

# Запуск контейнера
docker run -p 8000:8000 --env-file .env pronunciation-api

# Просмотр логов
docker-compose -f docker-compose.local.yml logs -f pronunciation-api

# Остановка сервисов
docker-compose -f docker-compose.local.yml down

# Пересборка образов
docker-compose -f docker-compose.local.yml up --build
```

## Использование

### Базовый анализ произношения

```python
import requests
import base64

# Подготовка данных
with open("audio.wav", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode()

payload = {
    "audio_data": audio_data,
    "reference_text": "jmenuji se",
    "language": "cs-CZ"
}

# Отправка запроса
response = requests.post(
    "http://localhost:8000/api/v1/pronunciation-assessment",
    json=payload
)

result = response.json()
print(f"Общая оценка: {result['scores']['pronunciation_score']}")
```

### Пример ответа

```json
{
  "status": "success",
  "recognized_text": "jmenuji se",
  "reference_text": "jmenuji se",
  "scores": {
    "pronunciation_score": 85.5,
    "accuracy_score": 90.0,
    "fluency_score": 80.0,
    "completeness_score": 100.0,
    "prosody_score": 75.0
  },
  "words_analysis": [
    {
      "word": "jmenuji",
      "accuracy_score": 88.0,
      "error_type": "None"
    },
    {
      "word": "se",
      "accuracy_score": 92.0,
      "error_type": "None"
    }
  ]
}
```

## Конфигурация

### Переменные окружения (.env файл)

#### Azure настройки
- `AZURE_SPEECH_KEY` - Ключ Azure Speech Service (обязательно)
- `AZURE_SPEECH_REGION` - Регион Azure (по умолчанию: eastus)
- `AZURE_DEFAULT_LANGUAGE` - Язык по умолчанию (по умолчанию: cs-CZ)
- `AZURE_TIMEOUT` - Таймаут запросов в секундах (по умолчанию: 30)

#### Настройки приложения
- `APP_NAME` - Название приложения
- `APP_VERSION` - Версия
- `APP_DEBUG` - Режим отладки (true/false)
- `APP_HOST` - Хост сервера (по умолчанию: 0.0.0.0)
- `APP_PORT` - Порт сервера (по умолчанию: 8000)
- `APP_CORS_ORIGINS` - JSON массив разрешенных CORS origins

#### Пример .env файла
```env
# Azure Configuration
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=eastus
AZURE_DEFAULT_LANGUAGE=cs-CZ
AZURE_TIMEOUT=30

# Application Configuration
APP_NAME=Pronunciation Assessment API
APP_VERSION=1.0.0
APP_DEBUG=false
APP_HOST=0.0.0.0
APP_PORT=8000
APP_CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
```

## Поддерживаемые языки

- Чешский (cs-CZ) - по умолчанию
- Английский (en-US, en-GB)
- Русский (ru-RU)
- Немецкий (de-DE)
- Французский (fr-FR)
- Испанский (es-ES)
- Итальянский (it-IT)
- И другие...

## Мобильная интеграция

API готов для интеграции с мобильными приложениями:

- **CORS настроен** для Ionic/Capacitor
- **JSON API** для простой интеграции
- **Детальные ошибки** для обработки на клиенте
- **Пакетная обработка** для оффлайн режима

### Пример для Ionic/Angular

```typescript
import { HttpClient } from '@angular/common/http';

export class PronunciationService {
  private apiUrl = 'http://localhost:8000/api/v1';

  constructor(private http: HttpClient) {}

  analyzePronunciation(audioData: string, referenceText: string) {
    return this.http.post(`${this.apiUrl}/pronunciation-assessment`, {
      audio_data: audioData,
      reference_text: referenceText,
      language: 'cs-CZ'
    });
  }
}
```

## Docker развертывание

### Локальная разработка
```bash
# Простой запуск API
docker-compose -f docker-compose.local.yml up pronunciation-api

# С Nginx reverse proxy
docker-compose -f docker-compose.local.yml --profile with-nginx up

# Просмотр логов
docker-compose -f docker-compose.local.yml logs -f

# Остановка
docker-compose -f docker-compose.local.yml down
```

### Продакшен развертывание
```bash
# Базовое развертывание (API + Nginx)
docker-compose -f docker-compose.prod.yml up -d

# С мониторингом (добавляет Prometheus + Grafana)
docker-compose -f docker-compose.prod.yml --profile with-monitoring up -d

# С Redis кэшированием
docker-compose -f docker-compose.prod.yml --profile with-redis up -d

# Полная конфигурация
docker-compose -f docker-compose.prod.yml --profile with-monitoring --profile with-redis up -d
```

### Мониторинг в продакшене
- **API Health**: `http://yourdomain.com/api/v1/health`
- **Prometheus**: `http://yourdomain.com:9090`
- **Grafana**: `http://yourdomain.com:3000` (admin/admin)

### SSL сертификаты
Для продакшена поместите SSL сертификаты в папку `ssl/`:
```
ssl/
├── cert.pem
└── key.pem
```

## Развитие

Архитектура приложения подготовлена для расширения:

- **Новые сервисы**: Добавление в `services.py`
- **Новые модели**: Расширение `models.py`
- **Новые эндпоинты**: Добавление в `routes.py`
- **Middleware**: Добавление в `main.py`
- **Конфигурация**: Расширение `config.py`
- **Docker профили**: Добавление новых сервисов в docker-compose

## Мониторинг

- **Health check**: `/api/v1/health`
- **Логирование**: Структурированные логи в JSON формате
- **Метрики**: Prometheus интеграция (опционально)
- **Визуализация**: Grafana дашборды (опционально)
- **Трассировка**: Готовность для OpenTelemetry

## Безопасность

- **CORS**: Настроенный для мобильных приложений
- **SSL/TLS**: Nginx с HTTPS в продакшене
- **Security Headers**: Настроены в Nginx
- **Валидация**: Pydantic модели
- **Ошибки**: Безопасная обработка исключений
- **Конфигурация**: Переменные окружения
- **Изоляция**: Docker контейнеры
- **Ограничения**: Resource limits в продакшене
