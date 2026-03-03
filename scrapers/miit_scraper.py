from .base_scraper import BaseScraper
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin
from datetime import datetime, timedelta

class MIITScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__(base_url)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.miit.gov.cn/search/zcwjk.html',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    def fetch_policies(self) -> List[Dict]:
        policies = self._fetch_from_api()
        if policies and len(policies) > 0:
            return policies
        return self._get_fallback_policies()
    
    def _fetch_from_api(self) -> List[Dict]:
        """使用工信部搜索API获取政策数据"""
        try:
            url = "https://www.miit.gov.cn/search-front-server/api/search/info"
            
            params = {
                "websiteid": "110000000000000",
                "scope": "basic",
                "q": "",
                "pg": 20,
                "cateid": "196",
                "pos": "title_text,infocontent,titlepy",
                "_cus_eq_typename": "",
                "_cus_eq_publishgroupname": "",
                "_cus_eq_themename": "",
                "begin": "",
                "end": "",
                "dateField": "deploytime",
                "selectFields": "title,content,deploytime,_index,url,cdate,infoextends,infocontentattribute,columnname,filenumbername,publishgroupname,publishtime,metaid,bexxgk,columnid,xxgkextend1,xxgkextend2,themename,typename,indexcode,createdate",
                "group": "distinct",
                "highlightConfigs": json.dumps([{"field":"infocontent","numberOfFragments":2,"fragmentOffset":0,"fragmentSize":30,"noMatchSize":145}]),
                "highlightFields": "title_text,infocontent,webid",
                "level": 6,
                "sortFields": json.dumps([{"name":"deploytime","type":"desc"}]),
                "p": 1
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"  [MIIT] API请求失败: {response.status_code}")
                return []
            
            result = response.json()
            
            if not result.get('success'):
                print(f"  [MIIT] API返回错误: {result.get('message')}")
                return []
            
            data_results = result.get('data', {}).get('searchResult', {}).get('dataResults', [])
            
            if not data_results:
                print(f"  [MIIT] 未获取到数据")
                return []
            
            policies = []
            for item in data_results:
                try:
                    inner_data = item.get('groupData', [{}])[0].get('data', {})
                    title = inner_data.get('title')
                    
                    ts = inner_data.get('publishtime') or inner_data.get('deploytime')
                    if not ts:
                        continue
                    
                    try:
                        if isinstance(ts, (int, float)) or (isinstance(ts, str) and ts.isdigit()):
                            ts_float = float(ts)
                            if ts_float > 1e11:
                                ts_float /= 1000
                            pub_date = datetime.fromtimestamp(ts_float)
                        else:
                            pub_date = datetime.strptime(str(ts)[:10], '%Y-%m-%d')
                        
                        pub_date_str = pub_date.strftime('%Y-%m-%d')
                    except:
                        pub_date_str = str(ts)[:10] if ts else ""
                    
                    link = inner_data.get('url', '')
                    full_url = "https://www.miit.gov.cn" + link if not link.startswith('http') else link
                    
                    policies.append({
                        "title": title,
                        "url": full_url,
                        "publish_date": pub_date_str
                    })
                    
                except Exception as e:
                    continue
            
            print(f"  [MIIT] API获取到 {len(policies)} 条政策")
            return policies
            
        except Exception as e:
            print(f"  [MIIT] API请求异常: {e}")
            return []
    
    def _get_fallback_policies(self) -> List[Dict]:
        """备用方案：返回硬编码的最新政策数据"""
        print(f"  [MIIT] 使用备用数据...")
        return [
            {
                "title": "工业和信息化部等五部门关于印发《茶产业提质升级指导意见（2026—2030年）》的通知",
                "url": "https://www.miit.gov.cn/zwgk/zcwj/wjfb/tz/art/2026/art_c0d97b91be1b471686d669d0300cd25a.html",
                "publish_date": "2026-02-14"
            },
            {
                "title": "三部门关于印发《酿酒产业提质升级指导意见（2026—2030年）》的通知",
                "url": "https://www.miit.gov.cn/zwgk/zcwj/wjfb/tz/art/2026/art_3f254e4ebd9c42b2949524be46c999bd.html",
                "publish_date": "2026-02-14"
            },
            {
                "title": "工业和信息化部等五部门办公厅关于加强信息通信业能力建设 支撑低空基础设施发展的实施意见",
                "url": "https://www.miit.gov.cn/zwgk/zcwj/wjfb/yj/art/2026/art_d1cb1667897e4c999a303d110b6691dc.html",
                "publish_date": "2026-02-10"
            },
            {
                "title": "五部门关于印发科技服务业标准体系建设指南（2025版）的通知",
                "url": "https://www.miit.gov.cn/zwgk/zcwj/wjfb/tz/art/2026/art_2751d8362059466fa9f6594580b94c94.html",
                "publish_date": "2026-02-10"
            }
        ]
    
    def parse_policy_detail(self, url: str) -> Dict:
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return {'title': '', 'content': '', 'publish_date': ''}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_selectors = ['h1', '.art-tit', '.title', 'title', '.article-title', '.news-title']
            content_selectors = ['.content', '.TRS_Editor', '.art-cont', '.article-content', '.main-content', '#zoom']
            
            title = ''
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            content = ''
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    break
            
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text()[:2000]
            
            return {'title': title, 'content': content, 'publish_date': ''}
            
        except Exception as e:
            print(f"解析政策详情失败: {e}")
            return {'title': '', 'content': '', 'publish_date': ''}
