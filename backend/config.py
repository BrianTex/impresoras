"""
Configuración centralizada del backend.
 
Todos los valores se leen de variables de entorno (con valores por defecto
razonables para que el proyecto siga funcionando "out of the box" si no
existe un archivo .env). Ver .env.example para la lista completa.
"""
import os
from dotenv import load_dotenv
 
# Carga el archivo .env si existe (no falla si no existe).
load_dotenv()
 
 
def _get_list(env_var: str, default: str) -> list[str]:
    raw = os.getenv(env_var, default)
    return [item.strip() for item in raw.split(",") if item.strip()]
 
 
class Settings:
    # Nombre de la aplicación (branding). Cada hospital puede personalizarlo.
    APP_NAME: str = os.getenv("APP_NAME", "Panel de Impresoras")
 
    # Servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
 
    # Scraping periódico
    SCRAPE_INTERVAL_SECONDS: int = int(os.getenv("SCRAPE_INTERVAL_SECONDS", "3600"))
    MAX_CONCURRENT_SCRAPES: int = int(os.getenv("MAX_CONCURRENT_SCRAPES", "5"))

    # Umbral (%) a partir del cual se considera "tóner bajo" en logs/alertas del backend
    LOW_TONER_THRESHOLD: int = int(os.getenv("LOW_TONER_THRESHOLD", "15"))
 
    # CORS: lista separada por comas, o "*" para permitir cualquier origen
    CORS_ORIGINS: list[str] = _get_list("CORS_ORIGINS", "*")
 
    # Nivel de logging: DEBUG, INFO, WARNING, ERROR
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
 
    # Cadena de conexión a la base de datos (por defecto, SQLite local)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./printers.db")
 
 
settings = Settings()
