import os
import sys
from pathlib import Path
from dotenv import load_dotenv

class Config:
    DEEPSEEK_API_KEY = None
    WECHAT_WEBHOOK_URL = None
    POLICY_DAYS = 5
    MONITOR_SITES = []
    
    @classmethod
    def load(cls):
        env_path = Path(__file__).parent / '.env'
        
        if env_path.exists():
            load_dotenv(env_path)
        
        cls.DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
        cls.WECHAT_WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
        
        policy_days = os.getenv('POLICY_DAYS')
        if policy_days:
            try:
                cls.POLICY_DAYS = int(policy_days)
            except ValueError:
                cls.POLICY_DAYS = 5
        
        cls.MONITOR_SITES = []
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('MONITOR_SITES='):
                        url = line.split('=', 1)[1].strip()
                        if url and not url.startswith('#'):
                            cls.MONITOR_SITES.append(url)
        
        return cls
    
    @classmethod
    def get_monitor_sites_from_env(cls):
        return cls.MONITOR_SITES