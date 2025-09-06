#!/usr/bin/env python3
"""
Тест REST-based Google Cloud Function локально
"""

import requests
import base64
import json

def test_rest_gcf():
    # Читаем тестовый аудио файл
    audio_file = "records/1756836061.wav"
    
    with open(audio_file, 'rb') as f:
        audio_data = f.read()
    
    # Кодируем в base64
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
    
    # Подготавливаем запрос
    payload = {
        "audio_data": audio_b64,
        "reference_text": "jmenuji se",
        "language": "cs-CZ"
    }
    
    # Отправляем запрос к локальному серверу
    url = "https://asure-101155779094.europe-west1.run.app"
    
    print("Отправляем запрос к REST GCF...")
    print(f"Размер аудио: {len(audio_data)} байт")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Анализ выполнен успешно!")
            
            print("\nРЕЗУЛЬТАТЫ:")
            print(f"Распознанный текст: '{result['recognized_text']}'")
            print(f"Референсный текст: '{result['reference_text']}'")
            
            scores = result['scores']
            print("\nОЦЕНКИ:")
            print(f"Общая оценка: {scores['pronunciation_score']:.1f}%")
            print(f"Точность: {scores['accuracy_score']:.1f}%")
            print(f"Беглость: {scores['fluency_score']:.1f}%")
            print(f"Полнота: {scores['completeness_score']:.1f}%")
            print(f"Просодия: {scores['prosody_score']:.1f}%")
            
            print("\nАНАЛИЗ СЛОВ:")
            for i, word in enumerate(result['words_analysis'], 1):
                print(f"{i}. '{word['word']}' - точность: {word['accuracy_score']:.1f}%, ошибка: {word['error_type']}")
        else:
            print(f"Ошибка: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("Не удается подключиться к серверу")
        print("Запустите сначала: python azure_rest_gcf.py")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    test_rest_gcf()
