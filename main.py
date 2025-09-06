"""
Главное FastAPI приложение для анализа произношения.

Модульная архитектура приложения для мобильного бекенда с поддержкой:
- Анализа произношения через Azure Cognitive Services
- CORS для мобильных приложений
- Детального логирования и мониторинга
- Масштабируемой структуры для будущего развития
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

from src.routes import router
from src.applications.azure_handling.routes import router as azure_router
from src.config import get_app_config, validate_azure_config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Получение конфигурации
app_config = get_app_config()

# Создание FastAPI приложения
app = FastAPI(
    title=app_config.app_name,
    description="Модульный API для анализа произношения речи с использованием Azure Cognitive Services. Разработан для мобильных приложений с поддержкой масштабирования.",
    version=app_config.version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Настройка CORS для мобильных приложений
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Middleware для доверенных хостов (безопасность)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # В продакшене следует ограничить
)

# Подключение маршрутов
app.include_router(router, prefix="/api/v1")
app.include_router(azure_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """
    Событие запуска приложения.
    
    Выполняет инициализацию и проверку конфигурации.
    """
    logger.info(f"Запуск {app_config.app_name} v{app_config.version}")
    
    # Проверка конфигурации Azure
    if not validate_azure_config():
        logger.error("Неверная конфигурация Azure")
        raise RuntimeError("Неверная конфигурация Azure")
    
    logger.info("Azure конфигурация валидна")
    logger.info(f"Сервер запущен на {app_config.host}:{app_config.port}")
    logger.info("API документация доступна на /docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Событие остановки приложения."""
    logger.info("Остановка приложения")

# Корневой эндпоинт
@app.get("/")
async def root():
    """
    Корневой эндпоинт API.
    
    Returns:
        dict: Информация о сервисе
    """
    return {
        "message": f"Добро пожаловать в {app_config.app_name}",
        "version": app_config.version,
        "docs": "/docs",
        "health": "/api/v1/health",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Запуск сервера
    uvicorn.run(
        "main:app",
        host=app_config.host,
        port=app_config.port,
        reload=app_config.debug,
        log_level="info"
    )
