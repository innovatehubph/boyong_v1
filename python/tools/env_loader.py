import os
from pathlib import Path
from typing import Optional, Dict, Any

class EnvLoader:
    """
    Environment variable loader for Pareng Boyong
    Ensures consistent .env file loading across all Python tools
    """
    
    def __init__(self, env_path: Optional[str] = None):
        if env_path is None:
            # Default to Pareng Boyong root .env file
            # Use actual container path directly
            env_path = "/root/projects/pareng-boyong/.env"
        
        self.env_path = Path(env_path)
        self._loaded_vars = {}
        self._load_env_file()
    
    def _load_env_file(self):
        """Load environment variables from .env file"""
        if not self.env_path.exists():
            print(f"Warning: .env file not found at {self.env_path}")
            return
        
        try:
            with open(self.env_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=VALUE format
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # Set environment variable
                        os.environ[key] = value
                        self._loaded_vars[key] = value
            
            print(f"✅ Loaded {len(self._loaded_vars)} environment variables from {self.env_path}")
            
        except Exception as e:
            print(f"❌ Error loading .env file: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with fallback to default"""
        return os.getenv(key, default)
    
    def get_required(self, key: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set or empty")
        return value
    
    def is_set(self, key: str) -> bool:
        """Check if environment variable is set and not empty"""
        value = os.getenv(key)
        return value is not None and value.strip() != ""
    
    def get_loaded_vars(self) -> Dict[str, str]:
        """Get all loaded variables (for debugging)"""
        return self._loaded_vars.copy()
    
    def reload(self):
        """Reload environment variables from file"""
        self._loaded_vars.clear()
        self._load_env_file()


# Global instance for easy importing
env_loader = EnvLoader()

# Convenience functions
def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable"""
    return env_loader.get(key, default)

def get_required_env(key: str) -> str:
    """Get required environment variable"""
    return env_loader.get_required(key)

def is_env_set(key: str) -> bool:
    """Check if environment variable is set"""
    return env_loader.is_set(key)

def reload_env():
    """Reload environment variables"""
    env_loader.reload()


def check_api_keys() -> Dict[str, Any]:
    """Check status of all API keys"""
    api_keys = {
        # AI Models
        'ANTHROPIC': 'API_KEY_ANTHROPIC',
        'OPENAI': 'API_KEY_OPENAI', 
        'GEMINI': 'API_KEY_GEMINI',
        'GROQ': 'API_KEY_GROQ',
        'HUGGINGFACE': 'API_KEY_HUGGINGFACE',
        'OPENROUTER': 'API_KEY_OPENROUTER',
        'DEEPSEEK': 'API_KEY_DEEPSEEK',
        'MISTRAL': 'API_KEY_MISTRAL',
        'AZURE': 'API_KEY_AZURE',
        'SAMBANOVA': 'API_KEY_SAMBANOVA',
        
        # External Services
        'ELEVENLABS': 'ELEVENLABS_API_KEY',
        'REPLICATE': 'REPLICATE_API_TOKEN',
        'GITHUB': 'GITHUB_PERSONAL_ACCESS_TOKEN',
        'UPSTASH_URL': 'UPSTASH_REDIS_REST_URL',
        'UPSTASH_TOKEN': 'UPSTASH_REDIS_REST_TOKEN',
    }
    
    status = {
        'active': {},
        'missing': {},
        'total_configured': 0,
        'total_missing': 0
    }
    
    for service, env_var in api_keys.items():
        if is_env_set(env_var):
            value = get_env(env_var)
            # Mask the key for security
            masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else value[:4] + '...'
            status['active'][service] = {
                'env_var': env_var,
                'masked_value': masked_value,
                'length': len(value)
            }
            status['total_configured'] += 1
        else:
            status['missing'][service] = env_var
            status['total_missing'] += 1
    
    return status


if __name__ == "__main__":
    # Test the env loader
    print("🔧 Testing Environment Variable Loader")
    print(f"📁 Loading from: {env_loader.env_path}")
    
    # Check API keys
    status = check_api_keys()
    
    print(f"\n✅ **Active API Keys** ({status['total_configured']}):")
    for service, info in status['active'].items():
        print(f"  - {service}: {info['masked_value']} ({info['length']} chars)")
    
    print(f"\n❌ **Missing API Keys** ({status['total_missing']}):")
    for service, env_var in status['missing'].items():
        print(f"  - {service}: {env_var}")
    
    # Test specific key
    replicate_token = get_env('REPLICATE_API_TOKEN')
    print(f"\n🎨 **Replicate Token**: {'✅ Set' if replicate_token else '❌ Not Set'}")
    if replicate_token:
        print(f"   Value: {replicate_token[:8]}...{replicate_token[-4:]}")