"""
Тест Azure эндпоинта /azure/pronunciation-assessment
"""

import httpx
import asyncio
import json
import base64


from pathlib import Path


BASE_URL = "http://85.198.82.170:12500"


def load_example_audio():
    # Путь к example.mp3 в той же папке
    audio_path = Path(__file__).parent / "records/example.wav"
    print(audio_path)

    if audio_path.exists():
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        return base64.b64encode(audio_bytes).decode('utf-8')
    else:
        print(f"⚠️ Файл {audio_path} не найден, используем тестовые данные")
        return create_test_audio_data()


def create_test_audio_data():
    """Создание валидных тестовых WAV данных."""
    import struct
    
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
    import math
    audio_data = b''
    for i in range(num_samples):
        sample = int(16000 * math.sin(2 * math.pi * 440 * i / sample_rate))
        audio_data += struct.pack('<h', sample)
    
    complete_wav = wav_header + audio_data
    return base64.b64encode(complete_wav).decode('utf-8')


async def test_pronunciation_endpoint():
    """Тест анализа произношения."""
    print("🔍 Тестирование /api/v1/azure/pronunciation-assessment")
    
    # Подготовка тестовых данных с реальным аудио
    test_data = {
        "audio_data": load_example_audio(),
        "reference_text": "jmenuji se",
        "language": "cs-CZ"
    }
    
    print(f"📝 Тестируем с чешским текстом: '{test_data['reference_text']}'")
    print(f"🌍 Язык: {test_data['language']}")
    print(f"📊 Размер аудио данных: {len(test_data['audio_data'])} символов base64")
    
    # Проверим первые байты декодированного аудио
    import base64
    try:
        audio_bytes = base64.b64decode(test_data['audio_data'])
        print(f"📊 Размер декодированного аудио: {len(audio_bytes)} байт")
        print(f"📊 Первые 20 байт: {audio_bytes[:20]}")
        
        # Проверим WAV заголовок
        if audio_bytes[:4] == b'RIFF' and audio_bytes[8:12] == b'WAVE':
            print("✅ Валидный WAV заголовок")
        else:
            print("❌ Неверный WAV заголовок")
    except Exception as e:
        print(f"❌ Ошибка декодирования base64: {e}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/azure/pronunciation-assessment",
                json=test_data
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Успешный ответ:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Проверка структуры ответа
                required_fields = ["status", "recognized_text", "reference_text", "scores", "words_analysis"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"❌ Отсутствуют поля: {missing_fields}")
                else:
                    print("✅ Все обязательные поля присутствуют")
                    
                # Проверка статуса
                if data.get("status") == "success":
                    print("✅ Статус: success")
                else:
                    print(f"⚠️ Статус: {data.get('status')}")
                    
                # Проверка scores
                scores = data.get("scores", {})
                if scores:
                    score_fields = ["pronunciation_score", "accuracy_score", "fluency_score", "completeness_score"]
                    missing_score_fields = [field for field in score_fields if field not in scores]
                    
                    if missing_score_fields:
                        print(f"⚠️ В scores отсутствуют поля: {missing_score_fields}")
                    else:
                        print("✅ Структура scores корректна")
                        print(f"Pronunciation Score: {scores.get('pronunciation_score')}")
                        
                # Проверка words_analysis
                words_analysis = data.get("words_analysis", [])
                if isinstance(words_analysis, list):
                    print(f"✅ Words analysis содержит {len(words_analysis)} элементов")
                else:
                    print("⚠️ Words analysis не является списком")
                    
            elif response.status_code == 400:
                print("⚠️ Ошибка валидации (ожидаемо для тестовых данных):")
                print(f"Response: {response.text}")
            elif response.status_code == 500:
                print("❌ Внутренняя ошибка сервера:")
                print(f"Response: {response.text}")
            else:
                print(f"❌ Неожиданная ошибка: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Ошибка выполнения теста: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ AZURE PRONUNCIATION ЭНДПОИНТА")
    print("=" * 60)
    
    asyncio.run(test_pronunciation_endpoint())
