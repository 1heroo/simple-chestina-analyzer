#!/usr/bin/env python3
"""
Простой скрипт для тестирования Azure Pronunciation Assessment
Анализирует example.mp3 с текстом "jmenuji se"
"""

import os
import json
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройки Azure
AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')

print(f"Azure Key: {'найден' if AZURE_SPEECH_KEY else 'не найден'}")
print(f"Azure Region: {AZURE_SPEECH_REGION}")

# Проверяем настройки
if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
    print("Настройте переменные окружения:")
    print("AZURE_SPEECH_KEY=your_key")
    print("AZURE_SPEECH_REGION=eastus")
    exit(1)

# Пытаемся импортировать Azure SDK
try:
    import azure.cognitiveservices.speech as speechsdk
    print("Azure Speech SDK импортирован успешно")
except ImportError as e:
    print(f"Ошибка импорта Azure Speech SDK: {e}")
    print("Установите SDK: pip install azure-cognitiveservices-speech")
    exit(1)
except Exception as e:
    print(f"Неожиданная ошибка при импорте: {e}")
    exit(1)

# Настройка Azure Speech SDK
try:
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION
    )
    speech_config.speech_recognition_language = "cs-CZ"  # Чешский язык
    print("SpeechConfig создан успешно")
except Exception as e:
    print(f"Ошибка создания SpeechConfig: {e}")
    print("Возможные причины:")
    print("1. Неверный формат региона (должен быть 'eastus', а не 'East US')")
    print("2. Неверный API ключ")
    print("3. Отсутствуют Visual C++ Redistributables")
    print("4. Проблемы с сетевым подключением")
    exit(1)

# Путь к файлу
audio_file = "manual_tests/azure_tests/records/example.wav"
reference_text = "jmenuji se"

# Проверяем файл
if not os.path.exists(audio_file):
    print(f"Файл {audio_file} не найден")
    exit(1)

print(f"Анализируем файл: {audio_file}")
print(f"Референсный текст: '{reference_text}'")

# Настройка аудио
try:
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file)
    print("AudioConfig создан успешно")
except Exception as e:
    print(f"Ошибка создания AudioConfig: {e}")
    exit(1)

# Настройка оценки произношения
try:
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Word,
        enable_miscue=True
    )
    
    # Включаем анализ просодии
    pronunciation_config.enable_prosody_assessment()
    print("PronunciationAssessmentConfig создан успешно")
except Exception as e:
    print(f"Ошибка создания PronunciationAssessmentConfig: {e}")
    exit(1)

# Создаем распознаватель
try:
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    
    # Применяем конфигурацию оценки
    pronunciation_config.apply_to(speech_recognizer)
    print("SpeechRecognizer создан и настроен успешно")
except Exception as e:
    print(f"Ошибка создания SpeechRecognizer: {e}")
    print("Это может быть связано с отсутствием Visual C++ Redistributables")
    exit(1)

print("Отправляем в Azure...")

# Выполняем анализ
try:
    result = speech_recognizer.recognize_once()
    print("Анализ выполнен успешно")
except Exception as e:
    print(f"Ошибка выполнения анализа: {e}")
    exit(1)

print("\n" + "="*50)
print("СЫРОЙ РЕЗУЛЬТАТ ОТ AZURE:")
print("="*50)

if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print(f"Распознанный текст: '{result.text}'")
    
    # Получаем сырой JSON ответ
    json_result = result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
    
    if json_result:
        # Парсим и красиво выводим JSON
        parsed_result = json.loads(json_result)
        print("\nПОЛНЫЙ JSON ОТВЕТ:")
        print(json.dumps(parsed_result, indent=2, ensure_ascii=False))
        
        # Извлекаем основные метрики
        nb_result = parsed_result.get('NBest', [{}])[0]
        pronunciation_assessment = nb_result.get('PronunciationAssessment', {})
        
        print("\nОСНОВНЫЕ МЕТРИКИ:")
        print(f"Общая оценка: {pronunciation_assessment.get('PronScore', 0):.1f}%")
        print(f"Точность: {pronunciation_assessment.get('AccuracyScore', 0):.1f}%")
        print(f"Беглость: {pronunciation_assessment.get('FluencyScore', 0):.1f}%")
        print(f"Полнота: {pronunciation_assessment.get('CompletenessScore', 0):.1f}%")
        print(f"Просодия: {pronunciation_assessment.get('ProsodyScore', 0):.1f}%")
        
        # Анализ слов
        words = nb_result.get('Words', [])
        if words:
            print(f"\nАНАЛИЗ СЛОВ ({len(words)} слов):")
            for i, word in enumerate(words, 1):
                word_text = word.get('Word', '')
                word_assessment = word.get('PronunciationAssessment', {})
                accuracy = word_assessment.get('AccuracyScore', 0)
                error_type = word_assessment.get('ErrorType', 'None')
                
                print(f"{i}. '{word_text}' - точность: {accuracy:.1f}%, ошибка: {error_type}")
                
                # Фонемы если есть
                phonemes = word.get('Phonemes', [])
                if phonemes:
                    print(f"   Фонемы:")
                    for phoneme in phonemes:
                        ph_text = phoneme.get('Phoneme', '')
                        ph_assessment = phoneme.get('PronunciationAssessment', {})
                        ph_accuracy = ph_assessment.get('AccuracyScore', 0)
                        print(f"     [{ph_text}] - {ph_accuracy:.1f}%")
    else:
        print("JSON результат недоступен")
        
elif result.reason == speechsdk.ResultReason.NoMatch:
    print("Речь не распознана")
    
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation = result.cancellation_details
    print(f"Анализ отменен: {cancellation.reason}")
    if cancellation.reason == speechsdk.CancellationReason.Error:
        print(f"Ошибка: {cancellation.error_details}")
        
else:
    print(f"Неожиданный результат: {result.reason}")

print("\n" + "="*50)
