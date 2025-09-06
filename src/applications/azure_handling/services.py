"""
Azure Cognitive Services для анализа произношения.
"""

import base64
import json
import os
import tempfile
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass

import httpx
import azure.cognitiveservices.speech as speechsdk

from .schemas import PronunciationRequest, PronunciationResponse, Scores, WordAnalysis
from ...config import get_azure_config
# Настройка логирования
import logging

logger = logging.getLogger(__name__)


@dataclass
class AzureRequestConfig:
    """Конфигурация запроса к Azure API."""
    reference_text: str
    language: str
    grading_system: str = "HundredMark"
    dimension: str = "Comprehensive"


@dataclass
class AzureResponse:
    """Структура ответа от Azure API."""
    recognized_text: str
    reference_text: str
    pronunciation_score: float
    accuracy_score: float
    fluency_score: float
    completeness_score: float
    words_analysis: list
    raw_response: dict = None


@dataclass
class AudioInfo:
    """Информация об аудио файле."""
    valid: bool
    format: str = None
    size: int = None
    error: str = None


class AzureSpeechService:
    """Azure Speech Service для анализа произношения (SDK)."""
    
    def __init__(self):
        """Инициализация сервиса с конфигурацией Azure."""
        self.config = get_azure_config()
        # Базовый URL может пригодиться для health check REST HEAD, но основной путь — через SDK
        self.base_url = f"https://{self.config.speech_region}.stt.speech.microsoft.com"
    
    def _detect_audio_extension(self, audio_bytes: bytes) -> str:
        """Определение подходящего расширения файла по сигнатуре."""
        try:
            if len(audio_bytes) >= 12 and audio_bytes[:4] == b"RIFF" and audio_bytes[8:12] == b"WAVE":
                return ".wav"
            if len(audio_bytes) >= 3 and (audio_bytes[:3] == b"ID3" or audio_bytes[:2] == b"\xff\xfb"):
                return ".mp3"
            return ".wav"
        except Exception:
            return ".wav"
    
    def _parse_sdk_json(self, json_result: Dict[str, Any], reference_text: str) -> AzureResponse:
        """Парсинг JSON результата из SDK (SpeechServiceResponse_JsonResult)."""
        try:
            # Извлечение основных данных
            recognized_text = json_result.get('DisplayText', '').strip()
            nb_result = json_result.get('NBest', [{}])[0]
            pronunciation_assessment = nb_result.get('PronunciationAssessment', {})
            
            # Анализ слов
            words_analysis = []
            words = nb_result.get('Words', [])
            for word in words:
                word_assessment = word.get('PronunciationAssessment', {})
                word_analysis = WordAnalysis(
                    word=word.get('Word', ''),
                    accuracy_score=word_assessment.get('AccuracyScore', 0.0),
                    error_type=word_assessment.get('ErrorType', 'None')
                )
                words_analysis.append(word_analysis)
            
            return AzureResponse(
                recognized_text=recognized_text,
                reference_text=reference_text,
                pronunciation_score=pronunciation_assessment.get('PronScore', 0.0),
                accuracy_score=pronunciation_assessment.get('AccuracyScore', 0.0),
                fluency_score=pronunciation_assessment.get('FluencyScore', 0.0),
                completeness_score=pronunciation_assessment.get('CompletenessScore', 0.0),
                words_analysis=words_analysis,
                raw_response=json_result
            )
        except Exception as e:
            raise Exception(f"Ошибка парсинга ответа Azure SDK: {str(e)}")
    
    async def analyze_pronunciation(self, request: PronunciationRequest) -> PronunciationResponse:
        """
        Анализ произношения через Azure Speech SDK.
        
        Args:
            request: Запрос на анализ произношения
        
        Returns:
            PronunciationResponse: Результат анализа
        """
        try:
            # Декодирование аудио данных
            audio_bytes = base64.b64decode(request.audio_data)
            ext = self._detect_audio_extension(audio_bytes)
            
            # Логирование для отладки
            logger.info("Подготовка анализа через Azure Speech SDK")
            logger.info(f"Audio size: {len(audio_bytes)} bytes, detected ext: {ext}")
            logger.info(f"Reference text: '{request.reference_text}'")
            logger.info(f"Language: {request.language or self.config.default_language}")
            
            # Записываем во временный файл, чтобы SDK корректно определил формат
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            
            try:
                # Настройка SDK
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.config.speech_key,
                    region=self.config.speech_region
                )
                speech_config.speech_recognition_language = request.language or self.config.default_language
                
                audio_config = speechsdk.audio.AudioConfig(filename=tmp_path)
                
                pronunciation_config = speechsdk.PronunciationAssessmentConfig(
                    reference_text=request.reference_text,
                    grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                    granularity=speechsdk.PronunciationAssessmentGranularity.Word,
                    enable_miscue=True
                )
                pronunciation_config.enable_prosody_assessment()
                
                speech_recognizer = speechsdk.SpeechRecognizer(
                    speech_config=speech_config,
                    audio_config=audio_config
                )
                pronunciation_config.apply_to(speech_recognizer)
                
                # Выполняем распознавание в пуле потоков, т.к. метод синхронный
                result = await asyncio.to_thread(speech_recognizer.recognize_once)
                
                if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    json_str = result.properties.get(
                        speechsdk.PropertyId.SpeechServiceResponse_JsonResult
                    )
                    if not json_str:
                        raise Exception("JSON результат от Azure SDK недоступен")
                    parsed = json.loads(json_str)
                    azure_response = self._parse_sdk_json(parsed, request.reference_text)
                elif result.reason == speechsdk.ResultReason.NoMatch:
                    raise Exception("Речь не распознана (NoMatch)")
                elif result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = result.cancellation_details
                    err = f"Отменено: {cancellation.reason}. Детали: {getattr(cancellation, 'error_details', '')}"
                    raise Exception(err)
                else:
                    raise Exception(f"Неожиданный результат Azure SDK: {result.reason}")
            
            finally:
                # Удаляем временный файл
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
            
            # Формируем ответ
            scores = Scores(
                pronunciation_score=azure_response.pronunciation_score,
                accuracy_score=azure_response.accuracy_score,
                fluency_score=azure_response.fluency_score,
                completeness_score=azure_response.completeness_score
            )
            
            return PronunciationResponse(
                status='success',
                recognized_text=azure_response.recognized_text,
                reference_text=azure_response.reference_text,
                scores=scores,
                words_analysis=azure_response.words_analysis
            )
        except Exception as e:
            raise Exception(f"Ошибка анализа произношения через SDK: {str(e)}")
    
    async def check_connection(self) -> bool:
        """Проверка базовой готовности Azure Speech SDK и сетевого доступа."""
        try:
            # Проверяем возможность создать конфигурацию и выполнить простой HEAD до STT endpoint
            _ = speechsdk.SpeechConfig(
                subscription=self.config.speech_key,
                region=self.config.speech_region
            )
            test_url = f"{self.base_url}/speech/recognition/conversation/cognitiveservices/v1"
            headers = {
                'Ocp-Apim-Subscription-Key': self.config.speech_key,
                'Content-Type': 'application/json'
            }
            async with httpx.AsyncClient() as client:
                response = await client.head(test_url, headers=headers, timeout=5.0)
                return response.status_code in [200, 401, 403, 405]
        except Exception as e:
            logger.error(f"Connection check error: {str(e)}")
            return False


class AudioProcessingService:
    """Сервис для обработки аудио данных."""
    
    def get_audio_info(self, audio_bytes: bytes) -> AudioInfo:
        """Получение информации об аудио файле."""
        try:
            # Базовая проверка аудио данных
            if len(audio_bytes) < 44:  # Минимальный размер WAV заголовка
                return AudioInfo(valid=False, error="Слишком маленький размер файла")
            
            # Проверка WAV заголовка
            if audio_bytes[:4] == b'RIFF' and audio_bytes[8:12] == b'WAVE':
                return AudioInfo(
                    valid=True,
                    format="WAV",
                    size=len(audio_bytes)
                )
            
            # Для других форматов - базовая проверка размера
            if len(audio_bytes) > 100:  # Минимальный разумный размер
                return AudioInfo(
                    valid=True,
                    format="Unknown",
                    size=len(audio_bytes)
                )
            
            return AudioInfo(valid=False, error="Неподдерживаемый формат аудио")
            
        except Exception as e:
            return AudioInfo(valid=False, error=f"Ошибка обработки аудио: {str(e)}")
