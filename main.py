import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config import Config
from modules import WeChatNotifier, DeepSeekAnalyzer, DateFilter
from scrapers import MOFScraper, MIITScraper, PBScraper, NDRCScraper, MOFCOMScraper, GOVScraper

class PolicyMonitor:
    def __init__(self):
        Config.load()
        self.wechat_notifier = WeChatNotifier(Config.WECHAT_WEBHOOK_URL)
        self.deepseek_analyzer = DeepSeekAnalyzer(Config.DEEPSEEK_API_KEY)
        self.date_filter = DateFilter()
        self.scrapers = []
        
        # URL到爬虫类的映射
        self.scraper_map = {
            'mof.gov.cn': MOFScraper,
            'miit.gov.cn': MIITScraper,
            'pbc.gov.cn': PBScraper,
            'ndrc.gov.cn': NDRCScraper,
            'mofcom.gov.cn': MOFCOMScraper,
            'gov.cn': GOVScraper
        }
    
    def add_scraper(self, scraper):
        self.scrapers.append(scraper)
    
    def auto_add_scrapers(self):
        for site_url in Config.MONITOR_SITES:
            for domain, scraper_class in self.scraper_map.items():
                if domain in site_url:
                    self.add_scraper(scraper_class(site_url))
                    break
    
    def process_policies(self):
        all_beneficial_policies = []
        
        for scraper in self.scrapers:
            print(f"正在抓取 {scraper.base_url} 的政策...")
            policies = scraper.fetch_policies()
            
            for policy in policies:
                publish_date = policy.get('publish_date', '')
                
                if not self.date_filter.is_within_days(publish_date, Config.POLICY_DAYS):
                    print(f"  跳过过期政策: {policy.get('title', '')} ({publish_date})")
                    continue
                
                print(f"  分析政策: {policy.get('title', '')}")
                detail = scraper.parse_policy_detail(policy.get('url', ''))
                content = detail.get('content', '') or policy.get('title', '')
                
                is_beneficial, beneficiary, interpretation, companies, benefit_level, benefit_reason = self.deepseek_analyzer.is_policy_beneficial(
                    policy.get('title', ''),
                    content
                )
                
                if is_beneficial:
                    beneficial_policy = {
                        'title': policy.get('title', ''),
                        'interpretation': interpretation,
                        'url': policy.get('url', ''),
                        'beneficiary': beneficiary,
                        'companies': companies,
                        'publish_date': publish_date,
                        'benefit_level': benefit_level,
                        'benefit_reason': benefit_reason
                    }
                    all_beneficial_policies.append(beneficial_policy)
                    print(f"    ✓ 发现利好政策: {beneficiary}")
                    if benefit_level:
                        print(f"      利好等级: {benefit_level}")
                    if benefit_reason:
                        print(f"      判断理由: {benefit_reason}")
                    if companies:
                        print(f"      相关公司: {', '.join(companies[:3])}")
                else:
                    print(f"    ✗ 无明显利好")
        
        return all_beneficial_policies
    
    def run(self):
        print("=" * 50)
        print("政策监控程序启动")
        print("=" * 50)
        
        beneficial_policies = self.process_policies()
        
        print(f"\n共发现 {len(beneficial_policies)} 条利好政策")
        
        if beneficial_policies:
            print("开始推送消息...")
            success_count = self.wechat_notifier.send_batch_messages(beneficial_policies)
            print(f"成功推送 {success_count}/{len(beneficial_policies)} 条消息")
        else:
            print("没有需要推送的政策")
        
        print("=" * 50)
        print("监控程序执行完成")
        print("=" * 50)

def main():
    monitor = PolicyMonitor()
    
    # 自动从配置文件添加监控网站
    monitor.auto_add_scrapers()
    
    monitor.run()

if __name__ == "__main__":
    main()