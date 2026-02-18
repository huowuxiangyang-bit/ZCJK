from .base_scraper import BaseScraper
from typing import List, Dict
from bs4 import BeautifulSoup
from datetime import datetime

class PBScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__(base_url)
    
    def fetch_policies(self) -> List[Dict]:
        policies = []
        seen_urls = set()
        
        try:
            soup = self.get_page(self.base_url)
            if not soup:
                return policies
            
            # 找到所有span标签，筛选日期标签
            date_spans = soup.find_all('span', class_='hui12')
            
            for date_span in date_spans:
                # 获取日期文本
                date_str = date_span.get_text(strip=True)
                if not date_str:
                    continue
                
                # 解析日期
                try:
                    publish_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
                except ValueError:
                    continue
                
                # 找到父td标签
                td = date_span.find_parent('td')
                if not td:
                    continue
                
                # 找到标题和链接
                title_tag = td.find('a')
                if not title_tag:
                    continue
                
                title = title_tag.get_text(strip=True)
                url = title_tag.get('href')
                
                if not url or not title:
                    continue
                
                # 构建完整的URL
                if not url.startswith('http'):
                    if url.startswith('/'):
                        url = 'https://www.pbc.gov.cn' + url
                    else:
                        url = self.base_url + url
                
                # 去重
                if url not in seen_urls:
                    seen_urls.add(url)
                    policies.append({
                        'title': title,
                        'url': url,
                        'publish_date': publish_date
                    })
                    
        except Exception as e:
            print(f"抓取人民银行网站失败: {e}")
        
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
        title_tag = soup.find('h1') or soup.find('title')
        content_tag = soup.find('div', class_='content') or soup.find('div', class_='article')
        
        title = title_tag.get_text(strip=True) if title_tag else ''
        content = content_tag.get_text(strip=True) if content_tag else ''
        
        return {
            'title': title,
            'content': content,
            'publish_date': ''
        }