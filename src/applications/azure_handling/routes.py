"""
Маршруты для Azure анализа произношения.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from .schemas import (
    PronunciationRequest,
    PronunciationResponse,
    BatchPronunciationRequest,
    BatchPronunciationResponse,
    ErrorResponse
)
from .services import AzureSpeechService, AudioProcessingService

# Настройка логирования
logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter(prefix="/azure", tags=["Azure Pronunciation"])

# Зависимости
def get_azure_service() -> AzureSpeechService:
    """Получение экземпляра Azure Speech Service."""
    return AzureSpeechService()

def get_audio_service() -> AudioProcessingService:
    """Получение экземпляра Audio Processing Service."""
    return AudioProcessingService()


@router.post(
    "/pronunciation-assessment",
    response_model=PronunciationResponse,
    summary="Анализ произношения через Azure",
    description="Анализ произношения речи с использованием Azure Cognitive Services"
)
async def pronunciation_assessment(
    request: PronunciationRequest,
    azure_service: AzureSpeechService = Depends(get_azure_service),
    audio_service: AudioProcessingService = Depends(get_audio_service)
):
    """
    Анализ произношения речи через Azure.
    
    Args:
        request: Данные для анализа произношения
        azure_service: Сервис Azure Speech
        audio_service: Сервис обработки аудио
        
    Returns:
        PronunciationResponse: Результат анализа произношения
    """
    try:
        logger.info(f"Начат анализ произношения для текста: '{request.reference_text}'")
        
        # Валидация аудио данных
        try:
            import base64
            audio_bytes = base64.b64decode(request.audio_data)
            audio_info = audio_service.get_audio_info(audio_bytes)
            
            if not audio_info.valid:
                raise HTTPException(
                    status_code=400,
                    detail=f"Неверный формат аудио: {audio_info.error or 'Неизвестная ошибка'}"
                )
                
            logger.info(f"Аудио файл валиден: {audio_info}")
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка валидации аудио: {str(e)}")
        
        # Выполнение анализа
        result = await azure_service.analyze_pronunciation(request)
        
        logger.info(f"Анализ завершен успешно. Общая оценка: {result.scores.pronunciation_score}")
        return result
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        logger.error(f"Таймаут: {str(e)}")
        raise HTTPException(status_code=504, detail=str(e))
    except ConnectionError as e:
        logger.error(f"Ошибка подключения: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Внутренняя ошибка: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")


@router.post(
    "/pronunciation-assessment/batch",
    response_model=BatchPronunciationResponse,
    summary="Пакетный анализ произношения через Azure",
    description="Анализ нескольких аудио файлов за один запрос"
)
async def batch_pronunciation_assessment(
    request: BatchPronunciationRequest,
    azure_service: AzureSpeechService = Depends(get_azure_service)
):
    """
    Пакетный анализ произношения через Azure.
    
    Args:
        request: Пакет запросов для анализа
        azure_service: Сервис Azure Speech
        
    Returns:
        BatchPronunciationResponse: Результаты пакетного анализа
    """
    try:
        logger.info(f"Начат пакетный анализ {len(request.requests)} запросов")
        
        results = []
        failed_requests = []
        
        for i, req in enumerate(request.requests):
            try:
                result = await azure_service.analyze_pronunciation(req)
                results.append(result)
            except Exception as e:
                logger.error(f"Ошибка в запросе {i}: {str(e)}")
                failed_requests.append({
                    "index": i,
                    "error": str(e),
                    "reference_text": req.reference_text
                })
        
        logger.info(f"Пакетный анализ завершен. Успешно: {len(results)}, Ошибок: {len(failed_requests)}")
        
        return BatchPronunciationResponse(
            status='success',
            results=results,
            failed_requests=failed_requests,
            total_processed=len(request.requests),
            successful_count=len(results),
            failed_count=len(failed_requests)
        )
        
    except Exception as e:
        logger.error(f"Ошибка пакетного анализа: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка пакетного анализа: {str(e)}")


@router.get(
    "/health",
    summary="Проверка здоровья Azure сервиса",
    description="Проверка доступности Azure Cognitive Services"
)
async def azure_health_check(azure_service: AzureSpeechService = Depends(get_azure_service)):
    """Проверка здоровья Azure сервиса."""
    try:
        connection_status = await azure_service.check_connection()
            
        return {
            "status": "healthy" if connection_status else "unhealthy",
            "provider": "Azure Cognitive Services",
            "connection": "connected" if connection_status else "disconnected"
        }
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья Azure: {str(e)}")
        return {
            "status": "unhealthy",
            "provider": "Azure Cognitive Services",
            "connection": "error",
            "error": str(e)
        }


@router.get(
    "/languages",
    summary="Поддерживаемые языки Azure",
    description="Список языков, поддерживаемых Azure Cognitive Services"
)
async def azure_supported_languages():
    """Поддерживаемые языки Azure."""
    return {
        "provider": "Azure Cognitive Services",
        "languages": [
            {"code": "cs-CZ", "name": "Чешский", "region": "Чехия"},
            {"code": "en-US", "name": "Английский", "region": "США"},
            {"code": "de-DE", "name": "Немецкий", "region": "Германия"},
            {"code": "fr-FR", "name": "Французский", "region": "Франция"},
            {"code": "es-ES", "name": "Испанский", "region": "Испания"},
            {"code": "it-IT", "name": "Итальянский", "region": "Италия"},
            {"code": "pt-BR", "name": "Португальский", "region": "Бразилия"},
            {"code": "ru-RU", "name": "Русский", "region": "Россия"},
            {"code": "zh-CN", "name": "Китайский", "region": "Китай"},
            {"code": "ja-JP", "name": "Японский", "region": "Япония"},
            {"code": "ko-KR", "name": "Корейский", "region": "Корея"}
        ],
        "default": "cs-CZ",
        "total": 11
    }
