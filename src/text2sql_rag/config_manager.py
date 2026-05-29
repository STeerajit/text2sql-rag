#!/usr/bin/env python3
"""
Configuration Manager for Text2SQL RAG System
Centralized configuration management with environment variables
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_file = config_file or "configs/config.json"
        self.env_file = ".env"
        
        # Load environment variables
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment"""
        config = self._get_default_config()
        
        # Load from config file if exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
        
        # Override with environment variables
        env_overrides = self._get_env_overrides()
        config.update(env_overrides)
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            # LLM Configuration
            "llm": {
                "default_model": "typhoon",
                "typhoon": {
                    "endpoint": "https://api.opentyphoon.ai/v1/chat/completions",
                    "model": "typhoon-v2.1-12b-instruct",
                    "max_tokens": 2000,
                    "temperature": 0.0,
                    "timeout": 30
                },
                "openai": {
                    "model": "gpt-4o-mini",
                    "max_tokens": 2000,
                    "temperature": 0.0,
                    "timeout": 30
                },
                "claude": {
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 2000,
                    "temperature": 0.0,
                    "timeout": 30
                },
                "gemini": {
                    "model": "gemini-pro",
                    "max_tokens": 2000,
                    "temperature": 0.0,
                    "timeout": 30
                }
            },
            
            # Embedding Configuration
            "embedding": {
                "default_model": "sentence-transformers/all-MiniLM-L6-v2",
                "models": {
                    "all-MiniLM-L6-v2": {
                        "type": "sentence_transformers",
                        "name": "sentence-transformers/all-MiniLM-L6-v2"
                    },
                    "multilingual-e5-base": {
                        "type": "huggingface_api",
                        "name": "intfloat/multilingual-e5-base"
                    }
                }
            },
            
            # Prompt Configuration
            "prompt": {
                "default_type": "ultimate",
                "max_length": 4000,
                "include_examples": True,
                "include_schema": True,
                "include_knowledge": True,
                "knowledge_top_k": 5
            },
            
            # Database Configuration
            "database": {
                "default_schema": {
                    "patients": [
                        "Name (TEXT): Patient name",
                        "Age (INTEGER): Patient age", 
                        "Hospital (TEXT): Hospital name",
                        "Medical_Condition (TEXT): Medical condition",
                        '"Billing Amount" (REAL): Billing amount',
                        "DoctorID (INTEGER): Doctor ID"
                    ]
                }
            },
            
            # Validation Configuration
            "validation": {
                "enabled": True,
                "check_syntax": True,
                "check_execution": True,
                "auto_correct": True
            },
            
            # Performance Configuration
            "performance": {
                "enable_caching": True,
                "cache_ttl": 3600,  # 1 hour
                "max_retries": 3,
                "retry_delay": 1.0
            },
            
            # Logging Configuration
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/text2sql_rag.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            
            # Web Interface Configuration
            "web": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False,
                "secret_key": "your-secret-key-here"
            }
        }
    
    def _get_env_overrides(self) -> Dict[str, Any]:
        """Get configuration overrides from environment variables"""
        overrides = {}
        
        # LLM API Keys
        if os.getenv("TYPHOON_API_KEY"):
            overrides.setdefault("api_keys", {})["typhoon"] = os.getenv("TYPHOON_API_KEY")
        
        if os.getenv("OPENAI_API_KEY"):
            overrides.setdefault("api_keys", {})["openai"] = os.getenv("OPENAI_API_KEY")
        
        if os.getenv("ANTHROPIC_API_KEY"):
            overrides.setdefault("api_keys", {})["anthropic"] = os.getenv("ANTHROPIC_API_KEY")
        
        if os.getenv("GOOGLE_API_KEY"):
            overrides.setdefault("api_keys", {})["google"] = os.getenv("GOOGLE_API_KEY")
        
        if os.getenv("HUGGINGFACE_API_KEY"):
            overrides.setdefault("api_keys", {})["huggingface"] = os.getenv("HUGGINGFACE_API_KEY")
        
        # LLM Model Override
        if os.getenv("DEFAULT_LLM_MODEL"):
            overrides.setdefault("llm", {})["default_model"] = os.getenv("DEFAULT_LLM_MODEL")
        
        # Embedding Model Override
        if os.getenv("DEFAULT_EMBEDDING_MODEL"):
            overrides.setdefault("embedding", {})["default_model"] = os.getenv("DEFAULT_EMBEDDING_MODEL")
        
        # Logging Level Override
        if os.getenv("LOG_LEVEL"):
            overrides.setdefault("logging", {})["level"] = os.getenv("LOG_LEVEL")
        
        # Web Configuration Overrides
        if os.getenv("WEB_HOST"):
            overrides.setdefault("web", {})["host"] = os.getenv("WEB_HOST")
        
        if os.getenv("WEB_PORT"):
            overrides.setdefault("web", {})["port"] = int(os.getenv("WEB_PORT"))
        
        if os.getenv("WEB_DEBUG"):
            overrides.setdefault("web", {})["debug"] = os.getenv("WEB_DEBUG").lower() == "true"
        
        return overrides
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot notation key"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_llm_config(self, model: str = None) -> Dict[str, Any]:
        """Get LLM configuration for specific model"""
        model = model or self.get("llm.default_model", "typhoon")
        llm_config = self.get(f"llm.{model}", {})
        
        # Add API key if available
        api_key = self.get(f"api_keys.{model}")
        if api_key:
            llm_config["api_key"] = api_key
        
        return llm_config
    
    def get_embedding_config(self, model: str = None) -> Dict[str, Any]:
        """Get embedding configuration for specific model"""
        model = model or self.get("embedding.default_model", "all-MiniLM-L6-v2")
        return self.get(f"embedding.models.{model}", {})
    
    def get_database_schema(self, table: str = "patients") -> List[str]:
        """Get database schema for specific table"""
        return self.get(f"database.default_schema.{table}", [])
    
    def is_api_key_configured(self, provider: str) -> bool:
        """Check if API key is configured for provider"""
        return bool(self.get(f"api_keys.{provider}"))
    
    def save_config(self, file_path: str = None) -> None:
        """Save current configuration to file"""
        file_path = file_path or self.config_file
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Remove sensitive information before saving
        config_to_save = self.config.copy()
        if "api_keys" in config_to_save:
            config_to_save["api_keys"] = {k: "***" for k in config_to_save["api_keys"]}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_to_save, f, indent=2, ensure_ascii=False)
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Check API keys
        required_keys = ["typhoon", "openai", "anthropic", "google"]
        configured_keys = []
        
        for key in required_keys:
            if self.is_api_key_configured(key):
                configured_keys.append(key)
        
        if not configured_keys:
            validation_result["errors"].append("No LLM API keys configured")
            validation_result["valid"] = False
        elif len(configured_keys) == 1:
            validation_result["warnings"].append("Only one LLM API key configured - consider adding more for redundancy")
        
        # Check required directories
        required_dirs = ["logs", "data", "results"]
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                validation_result["recommendations"].append(f"Create directory: {dir_name}")
        
        # Check configuration completeness
        critical_configs = [
            "llm.default_model",
            "embedding.default_model", 
            "prompt.default_type"
        ]
        
        for config_key in critical_configs:
            if not self.get(config_key):
                validation_result["errors"].append(f"Missing critical configuration: {config_key}")
                validation_result["valid"] = False
        
        return validation_result

# Global configuration instance
config = ConfigManager()

def get_config() -> ConfigManager:
    """Get global configuration instance"""
    return config

def main():
    """Test configuration manager"""
    config_mgr = ConfigManager()
    
    print("Configuration Manager Test")
    print("="*50)
    
    print("LLM Configuration:")
    print(f"  Default model: {config_mgr.get('llm.default_model')}")
    print(f"  Typhoon endpoint: {config_mgr.get('llm.typhoon.endpoint')}")
    print(f"  Max tokens: {config_mgr.get('llm.typhoon.max_tokens')}")
    
    print("\nAPI Keys Configured:")
    for provider in ["typhoon", "openai", "anthropic", "google"]:
        status = "✓" if config_mgr.is_api_key_configured(provider) else "✗"
        print(f"  {provider}: {status}")
    
    print("\nValidation Result:")
    validation = config_mgr.validate_config()
    print(f"  Valid: {validation['valid']}")
    if validation["errors"]:
        print(f"  Errors: {validation['errors']}")
    if validation["warnings"]:
        print(f"  Warnings: {validation['warnings']}")
    if validation["recommendations"]:
        print(f"  Recommendations: {validation['recommendations']}")

if __name__ == "__main__":
    main()


