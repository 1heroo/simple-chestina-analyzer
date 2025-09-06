"""
Запуск всех ручных тестов
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path


def run_test_file(test_file):
    """Запуск отдельного тестового файла."""
    print(f"\n{'='*60}")
    print(f"Запуск: {test_file}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=False, 
                              text=True, 
                              cwd=Path(test_file).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"Ошибка запуска {test_file}: {str(e)}")
        return False


def main():
    """Основная функция запуска всех тестов."""
    print("ЗАПУСК ВСЕХ РУЧНЫХ ТЕСТОВ")
    print("=" * 60)
    
    # Проверка, что сервер запущен
    print("Внимание: убедитесь, что сервер запущен на http://localhost:8000")
    print("Запустите: python main.py")
    input("Нажмите Enter для продолжения...")
    
    # Список всех тестов
    tests = [
        # Системные тесты
        "system_tests/test_health.py",
        "system_tests/test_info.py",
        
        # Azure тесты
        "azure_tests/test_azure_health.py",
        "azure_tests/test_azure_languages.py",
        "azure_tests/test_pronunciation.py",
        "azure_tests/test_batch_pronunciation.py",
    ]
    
    # Получение базового пути
    base_path = Path(__file__).parent
    
    # Запуск тестов
    results = {}
    for test in tests:
        test_path = base_path / test
        if test_path.exists():
            success = run_test_file(str(test_path))
            results[test] = success
        else:
            print(f"Тест не найден: {test_path}")
            results[test] = False
    
    # Сводка результатов
    print(f"\n{'='*60}")
    print("СВОДКА РЕЗУЛЬТАТОВ")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for test, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"{status} - {test}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nИтоги:")
    print(f"  Пройдено: {passed}")
    print(f"  Не пройдено: {failed}")
    print(f"  Всего: {len(results)}")
    
    if failed == 0:
        print("\nВсе тесты завершены успешно.")
    else:
        print(f"\n{failed} тест(ов) завершились с ошибками. Подробности см. в логах выше.")


if __name__ == "__main__":
    main()
