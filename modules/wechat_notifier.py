import requests
import json
from typing import Dict, Optional

class WeChatNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_message(self, title: str, interpretation: str, url: str, beneficiary: str = '', companies: list = None, benefit_level: str = '', benefit_reason: str = '') -> bool:
        companies_str = ''
        if companies:
            companies_str = '\n\n**相关公司：**' + '、'.join(companies[:5])
        
        beneficiary_str = ''
        if beneficiary:
            beneficiary_str = f'\n\n**受益行业：**{beneficiary}'
        
        level_str = ''
        if benefit_level:
            level_str = f'\n\n**利好等级：**{benefit_level}'
        
        reason_str = ''
        if benefit_reason:
            reason_str = f'\n\n**判断理由：**{benefit_reason}'
        
        message = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"### 【新政策提醒】\n\n**政策名称：**{title}{beneficiary_str}{level_str}{reason_str}{companies_str}\n\n**政策解读：**{interpretation}\n\n[查看原文]({url})"
            }
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(message),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            result = response.json()
            if result.get('errcode') == 0:
                return True
            else:
                print(f"企微推送失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            print(f"企微推送异常: {e}")
            return False
    
    def send_batch_messages(self, policies: list) -> int:
        success_count = 0
        for policy in policies:
            if self.send_message(
                policy.get('title', ''),
                policy.get('interpretation', ''),
                policy.get('url', ''),
                policy.get('beneficiary', ''),
                policy.get('companies', []),
                policy.get('benefit_level', ''),
                policy.get('benefit_reason', '')
            ):
                success_count += 1
        return success_count