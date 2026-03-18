"""
Configuration management for BrookStream.Ai weather and dam management system.
Handles environment variables, API keys, and file paths securely.
"""

import os
from pathlib import Path
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """Configuration class for the application."""
    
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables and .env file."""
        # Load from .env file if it exists
        env_file = self.BASE_DIR / '.env'
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            os.environ[key] = value
                logger.info("Loaded configuration from .env file")
            except Exception as e:
                logger.warning(f"Could not load .env file: {e}")
    
    @property
    def OPENWEATHER_API_KEY(self) -> Optional[str]:
        """Get OpenWeatherMap API key."""
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            # Fallback to file-based approach for backward compatibility
            api_key_path = self.BASE_DIR / 'weather_factorAPI_KEY.txt'
            if api_key_path.exists():
                try:
                    with open(api_key_path, 'r') as f:
                        api_key = f.read().strip()
                        logger.info("Loaded API key from file (consider using environment variables)")
                except Exception as e:
                    logger.error(f"Could not read API key file: {e}")
        return api_key
    
    @property
    def DATA_DIR(self) -> Path:
        """Get data directory path."""
        data_dir = self.BASE_DIR / 'data'
        data_dir.mkdir(exist_ok=True)
        return data_dir
    
    @property
    def DAM_DATA_FILE(self) -> Path:
        """Get dam data CSV file path."""
        # First check if file exists in data directory
        data_file = self.DATA_DIR / 'threegorges-water-storage.csv'
        if data_file.exists():
            return data_file
        
        # Fallback to dam directory for backward compatibility
        legacy_file = self.BASE_DIR / 'dam' / 'threegorges-water-storage.csv'
        if legacy_file.exists():
            return legacy_file
        
        # Default to data directory
        return data_file
    
    @property
    def LOG_DIR(self) -> Path:
        """Get log directory path."""
        log_dir = self.BASE_DIR / 'logs'
        log_dir.mkdir(exist_ok=True)
        return log_dir
    
    @property
    def DEBUG(self) -> bool:
        """Get debug mode."""
        return os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
    
    @property
    def SECRET_KEY(self) -> str:
        """Get Django secret key."""
        return os.getenv('SECRET_KEY', 'django-insecure-change-this-key-in-production')
    
    @property
    def ALLOWED_HOSTS(self) -> list:
        """Get allowed hosts."""
        hosts = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
        return [host.strip() for host in hosts]
    
    @property
    def DATABASE_URL(self) -> Optional[str]:
        """Get database URL."""
        return os.getenv('DATABASE_URL')
    
    @property
    def EMAIL_HOST(self) -> Optional[str]:
        """Get email host for notifications."""
        return os.getenv('EMAIL_HOST')
    
    @property
    def EMAIL_PORT(self) -> int:
        """Get email port."""
        return int(os.getenv('EMAIL_PORT', '587'))
    
    @property
    def EMAIL_HOST_USER(self) -> Optional[str]:
        """Get email username."""
        return os.getenv('EMAIL_HOST_USER')
    
    @property
    def EMAIL_HOST_PASSWORD(self) -> Optional[str]:
        """Get email password."""
        return os.getenv('EMAIL_HOST_PASSWORD')
    
    @property
    def REDIS_URL(self) -> Optional[str]:
        """Get Redis URL for caching and sessions."""
        return os.getenv('REDIS_URL')
    
    @property
    def CELERY_BROKER_URL(self) -> Optional[str]:
        """Get Celery broker URL."""
        return os.getenv('CELERY_BROKER_URL')
    
    # Weather API Configuration
    WEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5"
    WEATHER_UNITS = "metric"
    
    # ML Model Configuration
    ML_MODEL_PATH = Path("models")
    DEFAULT_RANDOM_STATE = 42
    DEFAULT_TEST_SIZE = 0.3
    
    # Alert Configuration
    DEFAULT_RAINFALL_THRESHOLD = 50.0  # mm
    DEFAULT_WATER_LEVEL_THRESHOLD = 600.0  # mcft
    DEFAULT_INFLOW_THRESHOLD = 200.0  # cubic feet/sec
    DEFAULT_OUTFLOW_THRESHOLD = 50.0  # cubic feet/sec
    
    # Cache Configuration
    CACHE_TIMEOUT = 300  # 5 minutes
    WEATHER_CACHE_TIMEOUT = 600  # 10 minutes
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # File Upload
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_UPLOAD_TYPES = ['.csv', '.xlsx', '.json']
    
    def validate_config(self) -> bool:
        """Validate critical configuration."""
        errors = []
        
        if not self.OPENWEATHER_API_KEY:
            errors.append("OpenWeather API key is required")
        
        if not self.DAM_DATA_FILE.exists():
            errors.append(f"Dam data file not found: {self.DAM_DATA_FILE}")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False
        
        logger.info("Configuration validation passed")
        return True


# Global configuration instance
config = Config()
