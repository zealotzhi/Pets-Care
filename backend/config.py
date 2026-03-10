"""
配置文件
"""
import os

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = 'data'
    
    # AI服务配置 - Trend Micro AI Endpoint
    AI_API_URL = os.environ.get('AI_API_URL') or 'https://api.rdsec.trendmicro.com/prod/aiendpoint/v1'
    AI_API_KEY = os.environ.get('AI_API_KEY') or 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiQUktMTc2ODgxMDA1NzM4OCIsInJvbGVzIjpbIjM1Il0sInVzZXJfaWQiOjY4NCwidXNlcm5hbWUiOiJaaGlfWmhhbmciLCJyb2xlX25hbWVzIjpbIlJPUC1haWVuZHBvaW50LVVzZXIiXSwidG9rZW5fdHlwZSI6ImFjY2VzcyIsImV4cCI6MTc3NjU4NjA2MSwianRpIjoiZWQ1NDc2ZjItZjUwZC0xMWYwLTg2ZjYtZWExZWRhODUzNjJmIiwidmVyc2lvbiI6IjIwMjQtMTEtMDEifQ.VMbTPyYn6CBWggI-n00qkJKWQ0TE7NWTqkp7Y8tOBXE'
    AI_MODEL = 'gpt-4o'  # 使用GPT-4o模型
    AI_TIMEOUT = 30  # seconds
    
    # 速率限制
    RATE_LIMIT_PER_MINUTE = 60
    AI_RATE_LIMIT_PER_MINUTE = 10

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 生产环境中应该从环境变量获取敏感信息
    AI_API_KEY = os.environ.get('AI_API_KEY')  # 生产环境必须设置

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
