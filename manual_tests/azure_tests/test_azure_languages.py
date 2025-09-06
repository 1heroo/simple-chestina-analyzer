"""
Тест Azure эндпоинта /azure/languages
"""

import httpx
import asyncio
import json


BASE_URL = "http://localhost:10000"


async def test_azure_languages_endpoint():
    """Тест получения поддерживаемых языков Azure."""
    print("Тестирование /api/v1/azure/languages")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/azure/languages")
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("Успешный ответ:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Проверка структуры ответа
                required_fields = ["provider", "languages", "default", "total"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"Отсутствуют поля: {missing_fields}")
                else:
                    print("Все обязательные поля присутствуют")
                    
                # Проверка провайдера
                if data.get("provider") == "Azure Cognitive Services":
                    print("Провайдер соответствует ожиданиям")
                else:
                    print(f"Неожиданный провайдер: {data.get('provider')}")
                    
                # Проверка языков
                languages = data.get("languages", [])
                if len(languages) > 0:
                    print(f"Найдено языков: {len(languages)}")
                    
                    # Проверка структуры языков
                    if languages:
                        first_lang = languages[0]
                        lang_fields = ["code", "name", "region"]
                        missing_lang_fields = [field for field in lang_fields if field not in first_lang]
                        
                        if missing_lang_fields:
                            print(f"В описании языков отсутствуют поля: {missing_lang_fields}")
                        else:
                            print("Структура языков корректна")
                            
                    # Проверка чешского языка (по умолчанию)
                    czech_found = any(lang.get("code") == "cs-CZ" for lang in languages)
                    if czech_found:
                        print("Чешский язык (cs-CZ) найден")
                    else:
                        print("Чешский язык (cs-CZ) не найден")
                        
                else:
                    print("Список языков пуст или отсутствует")
                    
                # Проверка общего количества
                total = data.get("total", 0)
                actual_count = len(languages)
                if total == actual_count:
                    print(f"Количество языков соответствует значению в поле total: {total}")
                else:
                    print(f"Несоответствие количества: заявлено {total}, фактически {actual_count}")
                    
            else:
                print(f"Ошибка: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"Ошибка выполнения теста: {str(e)}")


if __name__ == "__main__":
    print("=" * 50)
    print("ТЕСТ AZURE LANGUAGES ЭНДПОИНТА")
    print("=" * 50)
    asyncio.run(test_azure_languages_endpoint())
