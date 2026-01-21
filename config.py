"""
Configuration management for Email Gateway
Loads settings from environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""
    
    # Flask Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # API Security
    API_KEY = os.getenv('API_KEY', 'CHANGE-THIS-TO-SECURE-KEY')
    
    # SMTP Configuration
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM = os.getenv('SMTP_FROM', os.getenv('SMTP_USER', ''))
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '100'))
    
    # Email Limits
    MAX_SUBJECT_LENGTH = int(os.getenv('MAX_SUBJECT_LENGTH', '200'))
    MAX_BODY_LENGTH = int(os.getenv('MAX_BODY_LENGTH', '10000'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'email_gateway.log')
    
    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        errors = []
        
        if not cls.SMTP_USER:
            errors.append('SMTP_USER not configured')
        
        if not cls.SMTP_PASSWORD:
            errors.append('SMTP_PASSWORD not configured')
        
        if cls.API_KEY == 'CHANGE-THIS-TO-SECURE-KEY':
            errors.append('API_KEY must be changed from default')
        
        return errors