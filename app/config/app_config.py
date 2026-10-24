"""
Application configuration settings for the Manufacturing Predictive Maintenance application.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AppConfig:
    """Centralized application configuration management."""
    
    # Application Configuration
    APP_TITLE = "Manufacturing Predictive Maintenance"
    APP_DESCRIPTION = "AI-powered predictive maintenance for manufacturing equipment"
    APP_VERSION = "1.0.0"
    
    # Superwise AI Configuration
    SUPERWISE_BASE_URL = os.getenv("SUPERWISE_BASE_URL", "https://api.superwise.ai/v1")
    SUPERWISE_APP_ID = os.getenv("SUPERWISE_APP_ID", "")
    SUPERWISE_AUTH_TOKEN = os.getenv("SUPERWISE_AUTH_TOKEN", "")
    SUPERWISE_TIMEOUT = int(os.getenv("SUPERWISE_TIMEOUT", "10"))
    
    # Construct full Superwise URL
    SUPERWISE_FULL_URL = f"{SUPERWISE_BASE_URL}/app-worker/{SUPERWISE_APP_ID}/v1"
    
    # API Headers
    SUPERWISE_HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {SUPERWISE_AUTH_TOKEN}" if SUPERWISE_AUTH_TOKEN else ""
    }
    
    # Data Configuration
    DATA_DIR = os.getenv("DATA_DIR", "synthetic-data")
    SENSOR_DATA_FILE = "synthetic_sensor_data.csv"
    MAINTENANCE_DATA_FILE = "synthetic_maintenance_records.csv"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", None)
    
    # Dashboard Configuration
    DASHBOARD_TITLE = "Manufacturing Predictive Maintenance"
    DASHBOARD_ICON = "🔧"
    
    # Request Timeouts
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))
    
    # Machine Status Colors
    STATUS_COLORS = {
        "Low": "#4caf50",
        "Medium": "#ff9800", 
        "High": "#f44336",
        "Unknown": "#757575"
    }
    
    # Risk Assessment Thresholds
    RISK_THRESHOLDS = {
        'vibration': {'low': 1.0, 'medium': 1.5, 'high': 2.0},
        'temperature': {'low': 70, 'medium': 80, 'high': 90},
        'current': {'low': 12, 'medium': 14, 'high': 16},
        'pressure': {'low': 2.0, 'medium': 2.5, 'high': 3.0}
    }
    
    @classmethod
    def get_superwise_config(cls) -> Dict[str, Any]:
        """Get Superwise AI configuration."""
        return {
            "base_url": cls.SUPERWISE_FULL_URL,
            "headers": cls.SUPERWISE_HEADERS,
            "timeout": cls.SUPERWISE_TIMEOUT
        }
    
    @classmethod
    def get_data_paths(cls) -> Dict[str, str]:
        """Get data file paths."""
        return {
            "data_dir": cls.DATA_DIR,
            "sensor_data": os.path.join(cls.DATA_DIR, cls.SENSOR_DATA_FILE),
            "maintenance_data": os.path.join(cls.DATA_DIR, cls.MAINTENANCE_DATA_FILE)
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings."""
        required_env_vars = ["SUPERWISE_AUTH_TOKEN"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        return True

# Create global config instance
config = AppConfig()