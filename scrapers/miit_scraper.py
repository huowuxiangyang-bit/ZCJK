from .base_scraper import BaseScraper
from typing import List, Dict

class MIITScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__(base_url)
    
    def fetch_policies(self) -> List[Dict]:
        return self._get_fallback_policies()
    
    def _get_fallback_policies(self) -> List[Dict]:
        """
        备用方案：返回工信部最新的政策数据
        
        注意：由于工信部网站使用JavaScript动态加载数据，当前环境无法自动抓取。
        如需更新政策数据，请按以下步骤操作：
        
        1. 访问工信部政策文件库：https://www.miit.gov.cn/zwgk/zcwj/index.html
        2. 找到最新的政策（通常是前几条），获取：
           - 政策标题（title）
           - 政策详情页链接（url）
           - 发布日期（publish_date）
        3. 在下方列表中添加或替换对应的政策数据
        
        数据格式：
        {
            "title": "政策标题",
            "url": "https://www.miit.gov.cn/zwgk/zcwj/...",
            "publish_date": "2026-02-14"
        }
        
        当前数据（2026年2月17日）：
        """
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
        soup = self.get_page(url)
        
        if not soup:
            return {'title': '', 'content': '', 'publish_date': ''}
        
        title_tag = soup.find('h1')
        content_tag = soup.find('div', class_='content')
        
        title = title_tag.get_text(strip=True) if title_tag else ''
        content = content_tag.get_text(strip=True) if content_tag else ''
        
        return {'title': title, 'content': content, 'publish_date': ''}