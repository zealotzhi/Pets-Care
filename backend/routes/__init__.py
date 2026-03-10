"""
路由模块
"""
from .pet_routes import pet_bp
from .checkup_routes import checkup_bp
from .care_routes import care_bp

__all__ = ['pet_bp', 'checkup_bp', 'care_bp']
