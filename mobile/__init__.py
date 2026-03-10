"""
服务层模块
"""
from .api_client import APIClient, APIError, api_client

__all__ = ['APIClient', 'APIError', 'api_client']