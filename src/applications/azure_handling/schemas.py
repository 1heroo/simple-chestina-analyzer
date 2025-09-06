"""
Схемы данных для Azure анализа произношения.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class PronunciationRequest(BaseModel):
    """Запрос на анализ произношения."""
    audio_data: str = Field(..., description="Аудио данные в base64")
    reference_text: str = Field(..., description="Референсный текст для сравнения")
    language: Optional[str] = Field(default="cs-CZ", description="Язык анализа")


class Scores(BaseModel):
    """Оценки произношения."""
    pronunciation_score: float = Field(..., description="Общая оценка произношения (0-100)")
    accuracy_score: float = Field(..., description="Точность произношения (0-100)")
    fluency_score: float = Field(..., description="Беглость речи (0-100)")
    completeness_score: float = Field(..., description="Полнота произношения (0-100)")


class WordAnalysis(BaseModel):
    """Анализ отдельного слова."""
    word: str = Field(..., description="Слово")
    accuracy_score: float = Field(..., description="Точность произношения слова")
    error_type: str = Field(..., description="Тип ошибки (None, Mispronunciation, Omission, Insertion)")


class PronunciationResponse(BaseModel):
    """Ответ анализа произношения."""
    status: str = Field(..., description="Статус обработки")
    recognized_text: str = Field(..., description="Распознанный текст")
    reference_text: str = Field(..., description="Референсный текст")
    scores: Scores = Field(..., description="Оценки произношения")
    words_analysis: List[WordAnalysis] = Field(..., description="Анализ слов")


class BatchPronunciationRequest(BaseModel):
    """Пакетный запрос на анализ произношения."""
    requests: List[PronunciationRequest] = Field(..., description="Список запросов")


class BatchPronunciationResponse(BaseModel):
    """Ответ пакетного анализа произношения."""
    status: str = Field(..., description="Статус обработки")
    results: List[PronunciationResponse] = Field(..., description="Результаты анализа")
    failed_requests: List[dict] = Field(..., description="Неудачные запросы")
    total_processed: int = Field(..., description="Общее количество обработанных")
    successful_count: int = Field(..., description="Количество успешных")
    failed_count: int = Field(..., description="Количество неудачных")


class ErrorResponse(BaseModel):
    """Ответ с ошибкой."""
    status: str = Field(default="error", description="Статус ошибки")
    message: str = Field(..., description="Сообщение об ошибке")
    details: Optional[str] = Field(None, description="Детали ошибки")
