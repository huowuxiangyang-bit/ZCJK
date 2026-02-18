from .base_scraper import BaseScraper
from typing import List, Dict
from bs4 import BeautifulSoup
from datetime import datetime

class NDRCScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__(base_url)
    
    def fetch_policies(self) -> List[Dict]:
        policies = []
        
        try:
            soup = self.get_page(self.base_url)
            if not soup:
                return policies
            
            # 查找政策列表
            policy_items = soup.find_all('li')
            
            for item in policy_items:
                # 查找标题和链接
                title_tag = item.find('a')
                date_tag = item.find('span')
                
                if not title_tag or not date_tag:
                    continue
                
                title = title_tag.get_text(strip=True)
                url = title_tag.get('href')
                date_str = date_tag.get_text(strip=True)
                
                if not url or not date_str or not title:
                    continue
                
                # 构建完整的URL
                if not url.startswith('http'):
                    if url.startswith('/'):
                        url = 'https://www.ndrc.gov.cn' + url
                    else:
                        url = self.base_url + url
                
                policy = {
                    'title': title,
                    'url': url,
                    'publish_date': date_str
                }
                policies.append(policy)
                
        except Exception as e:
            print(f"抓取发改委网站失败: {e}")
        
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