"""
Модели данных для API анализа произношения.

Содержит Pydantic модели для запросов, ответов и внутренних структур данных.
Эти модели обеспечивают валидацию данных и автоматическую генерацию документации API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class HealthResponse(BaseModel):
    """Ответ проверки здоровья сервиса."""
    status: str = Field(..., description="Статус сервиса (healthy/unhealthy)")
    timestamp: str = Field(..., description="Время проверки")
    version: str = Field(..., description="Версия приложения")
    dependencies: Dict[str, Any] = Field(..., description="Статус зависимостей")
