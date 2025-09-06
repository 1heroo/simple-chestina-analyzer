"""
Основные маршруты API для приложения анализа произношения.

Содержит общие системные эндпоинты.
"""

from fastapi import APIRouter
from datetime import datetime
import logging

from .schemas import HealthResponse
from .config import get_app_config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter()



@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Проверка здоровья сервиса",
    description="Эндпоинт для проверки состояния API"
)
async def health_check():
    """
    Проверка здоровья сервиса.
    
    Returns:
        HealthResponse: Статус сервиса
    """
    try:
        app_config = get_app_config()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow().isoformat(),
            version=app_config.version,
            dependencies={"api": "running"}
        )
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            version="unknown",
            dependencies={"error": str(e)}
        )


@router.get(
    "/info",
    tags=["System"],
    summary="Информация о сервисе",
    description="Получение информации о версии и конфигурации сервиса"
)
async def service_info():
    """
    Информация о сервисе.
    
    Returns:
        dict: Информация о сервисе
    """
    app_config = get_app_config()
    
    return {
        "name": app_config.app_name,
        "version": app_config.version,
        "description": "FastAPI сервис для анализа произношения",
        "providers": ["Azure Cognitive Services"],
        "endpoints": {
            "azure_pronunciation": "/azure/pronunciation-assessment",
            "azure_batch": "/azure/pronunciation-assessment/batch",
            "azure_health": "/azure/health",
            "azure_languages": "/azure/languages",
            "health": "/health",
            "info": "/info"
        },
        "supported_formats": ["wav", "mp3", "ogg", "flac"],
        "max_audio_duration": "60 seconds",
        "cors_enabled": True
    }


