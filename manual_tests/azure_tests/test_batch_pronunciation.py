"""
Тест Azure эндпоинта /azure/pronunciation-assessment/batch
"""

import httpx
import asyncio
import json
import base64


BASE_URL = "http://localhost:8000"


def load_example_audio():
    """Загрузка реального аудио файла example.mp3."""
    from pathlib import Path
    
    # Путь к example.mp3 в той же папке
    audio_path = Path(__file__).parent / "example.mp3"
    
    if audio_path.exists():
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        return base64.b64encode(audio_bytes).decode('utf-8')
    else:
        print(f"Файл {audio_path} не найден. Используются тестовые данные.")
        return create_test_audio_data()


def create_test_audio_data():
    """Создание тестовых аудио данных (фейковый WAV заголовок)."""
    wav_header = b'RIFF' + b'\x24\x00\x00\x00' + b'WAVE' + b'fmt ' + b'\x10\x00\x00\x00'
    wav_header += b'\x01\x00\x01\x00\x44\xAC\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00'
    wav_header += b'data' + b'\x00\x00\x00\x00'
    
    fake_audio_data = wav_header + b'\x00' * 1000
    return base64.b64encode(fake_audio_data).decode('utf-8')


async def test_batch_pronunciation_endpoint():
    """Тест пакетного анализа произношения."""
    print("Тестирование /api/v1/azure/pronunciation-assessment/batch")
    
    # Подготовка тестовых данных с реальным аудио и чешским текстом
    test_data = {
        "requests": [
            {
                "audio_data": load_example_audio(),
                "reference_text": "jmenuji se",
                "language": "cs-CZ"
            },
            {
                "audio_data": load_example_audio(),
                "reference_text": "jmenuji se Pavel",
                "language": "cs-CZ"
            },
            {
                "audio_data": load_example_audio(),
                "reference_text": "jmenuji se Anna",
                "language": "cs-CZ"
            }
        ]
    }
    
    print("Пакетный анализ с чешскими фразами")
    print("Язык: cs-CZ")
    print(f"Количество запросов: {len(test_data['requests'])}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/azure/pronunciation-assessment/batch",
                json=test_data
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("Успешный ответ:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Проверка структуры ответа
                required_fields = ["status", "results", "failed_requests", "total_processed", "successful_count", "failed_count"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"Отсутствуют поля: {missing_fields}")
                else:
                    print("Все обязательные поля присутствуют")
                    
                # Проверка статуса
                if data.get("status") == "success":
                    print("Статус: success")
                else:
                    print(f"Статус: {data.get('status')}")
                    
                # Проверка результатов
                results = data.get("results", [])
                failed_requests = data.get("failed_requests", [])
                total_processed = data.get("total_processed", 0)
                successful_count = data.get("successful_count", 0)
                failed_count = data.get("failed_count", 0)
                
                print(f"Статистика:")
                print(f"  Всего обработано: {total_processed}")
                print(f"  Успешно: {successful_count}")
                print(f"  Неудачно: {failed_count}")
                
                # Проверка соответствия количества
                if total_processed == len(test_data["requests"]):
                    print("Количество обработанных запросов соответствует количеству отправленных")
                else:
                    print(f"Несоответствие: отправлено {len(test_data['requests'])}, обработано {total_processed}")
                    
                if successful_count + failed_count == total_processed:
                    print("Сумма успешных и неудачных соответствует общему количеству")
                else:
                    print("Обнаружено несоответствие в подсчете результатов")
                    
                # Проверка структуры результатов
                if results:
                    first_result = results[0]
                    result_fields = ["status", "recognized_text", "reference_text", "scores", "words_analysis"]
                    missing_result_fields = [field for field in result_fields if field not in first_result]
                    
                    if missing_result_fields:
                        print(f"В результатах отсутствуют поля: {missing_result_fields}")
                    else:
                        print("Структура результатов корректна")
                        
            elif response.status_code == 400:
                print("Ошибка валидации (ожидаемо для тестовых данных):")
                print(f"Response: {response.text}")
            elif response.status_code == 500:
                print("Внутренняя ошибка сервера:")
                print(f"Response: {response.text}")
            else:
                print(f"Неожиданная ошибка: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"Ошибка выполнения теста: {str(e)}")


async def test_batch_validation():
    """Тест валидации пакетных данных."""
    print("\nТестирование валидации пакетных данных")
    
    test_cases = [
        {
            "name": "Пустой список запросов",
            "data": {"requests": []}
        },
        {
            "name": "Отсутствует поле requests",
            "data": {}
        },
        {
            "name": "Неверная структура запроса",
            "data": {"requests": [{"invalid": "data"}]}
        }
    ]
    
    for test_case in test_cases:
        print(f"\nТест: {test_case['name']}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{BASE_URL}/api/v1/azure/pronunciation-assessment/batch",
                    json=test_case["data"]
                )
                
                if response.status_code in [400, 422]:
                    print("Корректная валидация (код 400/422)")
                else:
                    print(f"Неожиданный код ответа: {response.status_code}")
                    
        except Exception as e:
            print(f"Ошибка теста: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ AZURE BATCH PRONUNCIATION ЭНДПОИНТА")
    print("=" * 60)
    
    asyncio.run(test_batch_pronunciation_endpoint())
    asyncio.run(test_batch_validation())
