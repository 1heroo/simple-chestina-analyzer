"""
Тест Azure эндпоинта /azure/health
"""

import httpx
import asyncio
import json


BASE_URL = "http://localhost:10000"


async def test_azure_health_endpoint():
    """Тест проверки здоровья Azure сервиса."""
    print("Тестирование /api/v1/azure/health")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/azure/health")
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("Успешный ответ:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Проверка структуры ответа
                required_fields = ["status", "provider", "connection"]
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
                    
                # Проверка подключения
                connection = data.get("connection")
                if connection == "connected":
                    print("Подключение к Azure активно")
                elif connection == "disconnected":
                    print("Подключение к Azure отсутствует")
                else:
                    print(f"Неизвестный статус подключения: {connection}")
                    
                # Проверка общего статуса
                status = data.get("status")
                if status == "healthy":
                    print("Состояние сервиса: healthy")
                elif status == "unhealthy":
                    print("Состояние сервиса: unhealthy")
                    if "error" in data:
                        print(f"Ошибка: {data['error']}")
                        
            else:
                print(f"Ошибка: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"Ошибка выполнения теста: {str(e)}")


if __name__ == "__main__":
    print("=" * 50)
    print("ТЕСТ AZURE HEALTH ЭНДПОИНТА")
    print("=" * 50)
    asyncio.run(test_azure_health_endpoint())
