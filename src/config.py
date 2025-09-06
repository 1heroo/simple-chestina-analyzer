"""
Конфигурационный модуль для приложения анализа произношения.

Содержит настройки Azure, переменные окружения и конфигурацию приложения.
"""

import os
import json
from typing import Optional, List
from pydantic_settings import BaseSettings


class AzureConfig(BaseSettings):
    """
    Конфигурация для Azure Cognitive Services.
    
    Attributes:
        speech_key (str): Ключ API для Azure Speech Service.
        speech_region (str): Регион Azure для Speech Service.
        default_language (str): Язык по умолчанию для анализа.
        timeout (int): Таймаут для запросов к Azure API в секундах.
    """
    speech_key: str
    speech_region: str = "eastus"
    default_language: str = "cs-CZ"
    timeout: int = 30
    
    class Config:
        env_prefix = "AZURE_"
        case_sensitive = False


class AppConfig(BaseSettings):
    """
    Основная конфигурация приложения.
    
    Attributes:
        app_name (str): Название приложения.
        version (str): Версия приложения.
        debug (bool): Режим отладки.
        host (str): Хост для запуска сервера.
        port (int): Порт для запуска сервера.
        cors_origins (list): Разрешенные CORS origins для мобильного приложения.
    """
    app_name: str = "Pronunciation Assessment API"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = '["http://localhost:3000","http://localhost:8080","http://127.0.0.1:3000","http://127.0.0.1:8080","capacitor://localhost","ionic://localhost","http://localhost","https://localhost"]'
    
    class Config:
        env_prefix = "APP_"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Парсинг CORS origins из строки JSON."""
        try:
            return json.loads(self.cors_origins)
        except json.JSONDecodeError:
            return ["http://localhost:3000", "http://localhost:8080"]


# Глобальные экземпляры конфигурации
azure_config = AzureConfig()
app_config = AppConfig()


def get_azure_config() -> AzureConfig:
    """Получить конфигурацию Azure."""
    return azure_config


def get_app_config() -> AppConfig:
    """Получить конфигурацию приложения."""
    return app_config


def validate_azure_config() -> bool:
    """
    Проверить корректность конфигурации Azure.
    
    Returns:
        bool: True если конфигурация корректна, False иначе.
    """
    config = get_azure_config()
    
    if not config.speech_key:
        print("Ошибка: AZURE_SPEECH_KEY не настроен")
        return False
        
    if not config.speech_region:
        print("Ошибка: AZURE_SPEECH_REGION не настроен")
        return False
        
    return True
