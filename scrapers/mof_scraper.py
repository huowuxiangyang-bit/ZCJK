from .base_scraper import BaseScraper
from typing import List, Dict
from bs4 import BeautifulSoup

class MOFScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__(base_url)
    
    def fetch_policies(self) -> List[Dict]:
        policies = []
        soup = self.get_page(self.base_url)
        
        if not soup:
            return policies
        
        # 查找包含政策列表的liBox ul
        libox = soup.find('ul', class_='liBox')
        if not libox:
            return policies
        
        # 遍历每个政策项
        for li_item in libox.find_all('li'):
            link_tag = li_item.find('a')
            date_span = li_item.find('span')
            
            if link_tag and date_span:
                title = link_tag.get_text(strip=True)
                url = link_tag.get('href')
                publish_date = date_span.get_text(strip=True)
                
                # 过滤出政策相关的链接
                if not title or len(title) < 10:
                    continue
                
                if not url:
                    continue
                
                # 构建完整的URL
                if url.startswith('./'):
                    url = self.base_url + url[2:]
                
                policy = {
                    'title': title,
                    'url': url,
                    'publish_date': publish_date
                }
                policies.append(policy)
        
        return policies
    
    def parse_policy_detail(self, url: str) -> Dict:
        soup = self.get_page(url)
        
        if not soup:
            return {
                'title': '',
                'content': '',
                'publish_date': ''
            }
        
        title_tag = soup.find('h1')
        content_tag = soup.find('div', class_='content')
        
        title = title_tag.get_text(strip=True) if title_tag else ''
        content = content_tag.get_text(strip=True) if content_tag else ''
        
        return {
            'title': title,
            'content': content,
            'publish_date': ''
        }