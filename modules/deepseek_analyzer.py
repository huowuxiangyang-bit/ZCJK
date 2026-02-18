import requests
import json
from typing import Optional, Dict

class DeepSeekAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def analyze_policy(self, policy_title: str, policy_content: str) -> Optional[Dict]:
        content_preview = policy_content[:300] if policy_content else policy_title
        
        prompt = f"""你是专业的政策投研分析师，需要对政策文件进行投资价值分析。

政策标题：{policy_title}
政策内容摘要：{content_preview}

请严格按照以下标准判断利好等级（必须满足以下全部条件）：

【特大利好】必须同时满足：
1. 政策力度：国家级重大战略/规划，或大规模财政补贴/税收优惠
2. 市场规模：涉及千亿级以上市场
3. 营收影响：核心公司营收预期提升15%以上
4. 行业影响：彻底改变行业竞争格局，催生新赛道

【大利好】必须同时满足：
1. 政策力度：部委级重要政策/指导意见，或明确资金支持
2. 市场规模：涉及百亿级以上市场
3. 营收影响：核心公司营收预期提升8%-15%
4. 行业影响：显著提升行业景气度，龙头公司受益明显

【中利好】必须同时满足：
1. 政策力度：部委级一般性政策/通知，或行业规范文件
2. 市场规模：涉及十亿级以上市场
3. 营收影响：核心公司营收预期提升3%-8%
4. 行业影响：对行业有积极影响，但不影响竞争格局

【小利好】满足以下任一条件：
1. 政策力度较弱，更多是原则性/方向性文件
2. 市场规模较小，或影响范围有限
3. 营收影响：核心公司营收预期提升1%-3%
4. 仅为短期事件性利好，无持续性

【无明显利好】：政策对行业公司无实质影响，或为中性/负面政策

请按以下格式返回JSON：
{{
    "is_beneficial": true或false,
    "beneficiary": "受益行业",
    "companies": ["公司1", "公司2", "公司3"],
    "interpretation": "简要解读（50字以内）",
    "benefit_level": "特大利好/大利好/中利好/小利好/无明显利好",
    "benefit_reason": "判断理由（从政策力度、市场规模、营收影响、行业影响四个维度说明为什么判断为此等级）"
}}"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个专业的政策投研分析师。判断利好等级必须同时满足政策力度、市场规模、营收影响、行业影响四个维度的条件，不能仅凭单一维度判断。返回JSON时必须包含benefit_reason字段说明判断理由。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            
            try:
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                analysis = json.loads(content)
                return analysis
            except json.JSONDecodeError:
                print(f"DeepSeek返回的不是有效JSON: {content[:200]}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"DeepSeek API调用失败: {e}")
            return None
    
    def is_policy_beneficial(self, policy_title: str, policy_content: str) -> tuple[bool, str, str, list, str, str]:
        analysis = self.analyze_policy(policy_title, policy_content)
        
        if analysis is None:
            return False, "", "", [], "", ""
        
        is_beneficial = analysis.get('is_beneficial', False)
        beneficiary = analysis.get('beneficiary', '')
        companies = analysis.get('companies', [])
        interpretation = analysis.get('interpretation', '')
        benefit_level = analysis.get('benefit_level', '')
        benefit_reason = analysis.get('benefit_reason', '')
        
        return is_beneficial, beneficiary, interpretation, companies, benefit_level, benefit_reason