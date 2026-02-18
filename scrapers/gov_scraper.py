from .base_scraper import BaseScraper
from typing import List, Dict
from bs4 import BeautifulSoup
from datetime import datetime
import json
import requests

class GOVScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__(base_url)
    
    def fetch_policies(self) -> List[Dict]:
        policies = []
        
        try:
            # 国务院网站使用JSON数据接口
            json_url = "https://www.gov.cn/zhengce/zuixin/ZUIXINZHENGCE.json"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(json_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"获取国务院JSON数据失败，状态码: {response.status_code}")
                return policies
            
            data = json.loads(response.text)
            
            if not isinstance(data, list):
                print(f"国务院JSON数据格式错误，期望list，实际: {type(data)}")
                return policies
            
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                title = item.get('TITLE', '')
                url = item.get('URL', '')
                date_str = item.get('DOCRELPUBTIME', '')
                
                if not title or not url or not date_str:
                    continue
                
                policy = {
                    'title': title,
                    'url': url,
                    'publish_date': date_str
                }
                policies.append(policy)
                
        except Exception as e:
            print(f"抓取国务院办公厅网站失败: {e}")
        
        return policies
    
    def parse_policy_detail(self, url: str) -> Dict:
        soup = self.get_page(url)
        
        if not soup:
            return {
                'title': '',
                'content': '',
                'publish_date': ''
            }
        
        # 查找标题和内容
        title_tag = soup.find('h1')
        content_tag = soup.find('div', class_='content')
        
        title = title_tag.get_text(strip=True) if title_tag else ''
        content = content_tag.get_text(strip=True) if content_tag else ''
        
        return {
            'title': title,
            'content': content,
            'publish_date': ''
        }