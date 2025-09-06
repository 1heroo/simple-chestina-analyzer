#!/usr/bin/env python3
"""
Прямой тест Azure API для сравнения с нашим сервисом
"""

import httpx
import base64
import json
import asyncio
from pathlib import Path
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')

print(f"Проверка ключа Azure: {'найден' if AZURE_SPEECH_KEY else 'не найден'}")
print(f"Регион Azure: {AZURE_SPEECH_REGION}")

if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
    print("Переменные окружения не настроены. Укажите AZURE_SPEECH_KEY и AZURE_SPEECH_REGION.")
    exit(1)


def create_test_audio_data():
    """Создание валидных тестовых WAV данных."""
    import struct
    import math
    
    # Параметры аудио
    sample_rate = 16000
    duration = 1  # 1 секунда
    num_samples = sample_rate * duration
    
    # WAV заголовок
    wav_header = b'RIFF'
    wav_header += struct.pack('<I', 36 + num_samples * 2)  # Размер файла - 8
    wav_header += b'WAVE'
    wav_header += b'fmt '
    wav_header += struct.pack('<I', 16)  # Размер fmt chunk
    wav_header += struct.pack('<H', 1)   # Формат PCM
    wav_header += struct.pack('<H', 1)   # Моно
    wav_header += struct.pack('<I', sample_rate)  # Частота дискретизации
    wav_header += struct.pack('<I', sample_rate * 2)  # Байт в секунду
    wav_header += struct.pack('<H', 2)   # Блок выравнивания
    wav_header += struct.pack('<H', 16)  # Бит на сэмпл
    wav_header += b'data'
    wav_header += struct.pack('<I', num_samples * 2)  # Размер данных
    
    # Генерируем простой синусоидальный сигнал (тон 440 Гц)
    audio_data = b''
    for i in range(num_samples):
        sample = int(16000 * math.sin(2 * math.pi * 440 * i / sample_rate))
        audio_data += struct.pack('<h', sample)
    
    return wav_header + audio_data


async def test_direct_azure_api():
    """Прямой тест Azure API."""
    print("Прямой тест Azure Pronunciation Assessment API")
    
    # Создаем тестовые аудио данные
    audio_bytes = create_test_audio_data()
    reference_text = "jmenuji se"
    
    print(f"Размер аудио (байт): {len(audio_bytes)}")
    print(f"Референсный текст: '{reference_text}'")
    print(f"Первые 20 байт: {audio_bytes[:20]}")
    
    # URL для REST API
    base_url = f"https://{AZURE_SPEECH_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    
    # Параметры оценки произношения
    pronunciation_params = {
        'ReferenceText': reference_text,
        'GradingSystem': 'HundredMark',
        'Dimension': 'Comprehensive',
        'EnableMiscue': 'true'
    }
    
    # Заголовки
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_SPEECH_KEY,
        'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
        'Accept': 'application/json',
        'Pronunciation-Assessment': json.dumps(pronunciation_params)
    }
    
    # Параметры URL
    params = {
        'language': 'cs-CZ',
        'format': 'detailed'
    }
    
    print("Отправка прямого запроса к Azure API...")
    print(f"URL: {base_url}")
    print(f"Params: {params}")
    print(f"Headers: {headers}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                base_url,
                params=params,
                headers=headers,
                content=audio_bytes
            )
            
            print(f"Код состояния ответа: {response.status_code}")
            print(f"Заголовки ответа: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("Прямой запрос к Azure выполнен успешно.")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                # Извлекаем основные метрики
                if 'NBest' in result and result['NBest']:
                    best_result = result['NBest'][0]
                    
                    if 'PronunciationAssessment' in best_result:
                        pa = best_result['PronunciationAssessment']
                        
                        print(f"\nОсновные метрики:")
                        print(f"Распознанный текст: '{best_result.get('Display', '')}'")
                        print(f"Общая оценка: {pa.get('PronScore', 0):.1f}%")
                        print(f"Точность: {pa.get('AccuracyScore', 0):.1f}%")
                        print(f"Беглость: {pa.get('FluencyScore', 0):.1f}%")
                        print(f"Полнота: {pa.get('CompletenessScore', 0):.1f}%")
                        
            else:
                print(f"Ошибка прямого запроса: {response.status_code}")
                print(f"Ответ: {response.text}")
                
                # Попробуем получить детальную ошибку
                try:
                    error_detail = response.json()
                    print(f"Детали ошибки: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
                except:
                    print("Не удалось распарсить ошибку как JSON")
                    
    except Exception as e:
        print(f"Исключение при прямом запросе: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("ПРЯМОЙ ТЕСТ AZURE PRONUNCIATION ASSESSMENT API")
    print("=" * 60)
    
    asyncio.run(test_direct_azure_api())
