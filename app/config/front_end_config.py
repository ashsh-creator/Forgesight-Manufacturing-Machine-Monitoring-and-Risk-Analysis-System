"""
Frontend configuration settings for the Manufacturing Predictive Maintenance application.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FrontendConfig:
    """Centralized frontend configuration management."""
    
    # Streamlit Page Configuration
    PAGE_TITLE = "Manufacturing AI"
    PAGE_ICON = "app/assets/Group 11.svg"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"
    
    # Service Configuration
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))
    
    # Dashboard Configuration
    DASHBOARD_TITLE = "Manufacturing Predictive Maintenance"
    DASHBOARD_ICON = "🔧"
    
    # Machine Status Colors
    STATUS_COLORS = {
        "Low": "#4caf50",
        "Medium": "#ff9800", 
        "High": "#f44336",
        "Unknown": "#757575"
    }
    
    # Chart Colors
    CHART_COLORS = {
        "Low": "#4caf50",
        "Medium": "#ff9800",
        "High": "#f44336"
    }
    
    
    # Layout Configuration
    LAYOUT_CONFIG = {
        "refresh_columns": [2, 2, 2, 2, 2, 2, 2, 1],
        "chart_columns": [3, 3],
        "metrics_columns": 2,
        "table_columns": [1, 2, 2, 2, 2, 2, 2, 2],
        "machine_buttons_max_columns": 4
    }
    
    # Alert Configuration
    ALERT_CONFIG = {
        "high_risk_icon": "🚨",
        "medium_risk_icon": "⚡",
        "low_risk_icon": "✅",
        "toast_high_risk_icon": "🚨",
        "toast_medium_risk_icon": "⚡"
    }
    
    # Chart Configuration
    CHART_CONFIG = {
        "pie_chart_height": 350,
        "subplot_height": 600,
        "subplot_rows": 2,
        "subplot_cols": 2,
        "vertical_spacing": 0.1
    }
    
    # Footer Configuration
    FOOTER_CONFIG = {
        "app_version": "v1.0.0",
        "powered_by": "Streamlit & AI Services"
    }
    
    # Asset Paths
    ASSET_PATHS = {
        "superwise_logo": "app/assets/superwise_logo.svg",
        "favicon": "app/assets/Group 11.svg"
    }
    
    
    @classmethod
    def get_chart_colors(cls) -> Dict[str, str]:
        """Get chart color mapping."""
        return cls.CHART_COLORS
    
    @classmethod
    def get_status_colors(cls) -> Dict[str, str]:
        """Get status color mapping."""
        return cls.STATUS_COLORS
    
    @classmethod
    def get_alert_config(cls) -> Dict[str, str]:
        """Get alert configuration."""
        return cls.ALERT_CONFIG
    
    @classmethod
    def get_layout_config(cls) -> Dict[str, Any]:
        """Get layout configuration."""
        return cls.LAYOUT_CONFIG
    
    @classmethod
    def get_chart_config(cls) -> Dict[str, Any]:
        """Get chart configuration."""
        return cls.CHART_CONFIG
    
    @classmethod
    def get_footer_config(cls) -> Dict[str, str]:
        """Get footer configuration."""
        return cls.FOOTER_CONFIG
    
    @classmethod
    def get_asset_path(cls, asset_name: str) -> str:
        """Get asset file path."""
        return cls.ASSET_PATHS.get(asset_name, "")

# Create global config instance
frontend_config = FrontendConfig()
