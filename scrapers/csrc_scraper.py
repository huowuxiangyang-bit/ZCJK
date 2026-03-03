from .base_scraper import BaseScraper
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from datetime import datetime, timedelta

class CSRCScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__(base_url)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        self.base_url = 'https://www.csrc.gov.cn'
    
    def fetch_policies(self) -> List[Dict]:
        try:
            print(f"  [CSRC] 正在抓取首页...")
            response = self.session.get(self.base_url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"  [CSRC] 首页请求失败: {response.status_code}")
                return self._get_fallback_policies()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            policies = []
            links = soup.find_all('a', href=re.compile(r'^/csrc/c\d+/c\d+/content\.shtml'))
            
            print(f"  [CSRC] 找到 {len(links)} 个链接，获取前10条的日期...")
            
            for i, a in enumerate(links[:10]):
                title = a.get_text(strip=True)
                if not title or len(title) < 5:
                    continue
                
                href = a.get('href', '')
                full_url = self.base_url + href
                
                pub_date = self._get_publish_date(full_url)
                
                if pub_date:
                    policies.append({
                        "title": title,
                        "url": full_url,
                        "publish_date": pub_date
                    })
                print(f"    [{i+1}] {pub_date}: {title[:30]}...")
            
            print(f"  [CSRC] 获取到 {len(policies)} 条政策")
            return policies
            
        except Exception as e:
            print(f"  [CSRC] 抓取异常: {e}")
            return self._get_fallback_policies()
    
    def _get_publish_date(self, url: str) -> str:
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            meta_pubdate = soup.find('meta', attrs={'name': 'PubDate'})
            if meta_pubdate and meta_pubdate.get('content'):
                pub_date_str = meta_pubdate.get('content')[:10]
                return pub_date_str
            
            date_patterns = soup.find_all(string=re.compile(r'\d{4}-\d{2}-\d{2}'))
            for d in date_patterns:
                match = re.search(r'\d{4}-\d{2}-\d{2}', d)
                if match:
                    return match.group()
            
            return None
            
        except:
            return None
    
    def _get_fallback_policies(self) -> List[Dict]:
        print(f"  [CSRC] 使用备用数据...")
        return [
            {
                "title": "中国证监会党委部署启动树立和践行正确政绩观学习教育",
                "url": "https://www.csrc.gov.cn/csrc/c100028/c7617175/content.shtml",
                "publish_date": "2026-02-28"
            },
            {
                "title": "证监会高质量完成2025年全国两会建议提案办理工作",
                "url": "https://www.csrc.gov.cn/csrc/c100028/c7617074/content.shtml",
                "publish_date": "2026-02-27"
            },
            {
                "title": "证监会召开资本市场\"十五五\"规划外资机构座谈会",
                "url": "https://www.csrc.gov.cn/csrc/c100028/c7616952/content.shtml",
                "publish_date": "2026-02-26"
            },
            {
                "title": "中国证监会发布《私募投资基金信息披露监督管理办法》",
                "url": "https://www.csrc.gov.cn/csrc/c100028/c7616846/content.shtml",
                "publish_date": "2026-02-25"
            }
        ]
    
    def parse_policy_detail(self, url: str) -> Dict:
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return {'title': '', 'content': '', 'publish_date': ''}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = ''
            title_tag = soup.find('meta', attrs={'name': 'ArticleTitle'})
            if title_tag:
                title = title_tag.get('content', '')
            
            if not title:
                h1 = soup.find('h1')
                if h1:
                    title = h1.get_text(strip=True)
            
            content = ''
            content_div = soup.find('div', class_='content')
            if content_div:
                content = content_div.get_text(strip=True)[:2000]
            
            if not content:
                article = soup.find('article')
                if article:
                    content = article.get_text(strip=True)[:2000]
            
            return {'title': title, 'content': content, 'publish_date': ''}
            
        except Exception as e:
            return {'title': '', 'content': '', 'publish_date': ''}
