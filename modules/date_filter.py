from datetime import datetime, timedelta
from typing import Optional
import re

class DateFilter:
    @staticmethod
    def is_within_days(publish_date_str: str, days: int = 4) -> bool:
        today = datetime.now()
        cutoff_date = today - timedelta(days=days-1)
        
        # 将 cutoff_date 的时间部分设置为 00:00:00，以便进行纯日期比较
        cutoff_date = cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        parsed_date = DateFilter.parse_date(publish_date_str)
        
        if parsed_date is None:
            return False
        
        return parsed_date >= cutoff_date
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        date_str = date_str.strip()
        
        date_patterns = [
            (r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日号]?', '%Y-%m-%d'),
            (r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日号]?', '%Y/%m/%d'),
            (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', '%Y.%m.%d'),
            (r'(\d{4})(\d{2})(\d{2})', '%Y%m%d'),
            (r'(\d{1,2})[-/月](\d{1,2})[日号]', '%m-%d'),
        ]
        
        for pattern, fmt in date_patterns:
            match = re.match(pattern, date_str)
            if match:
                try:
                    if len(match.groups()) == 2:
                        month, day = match.groups()
                        year = datetime.now().year
                        date_obj = datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d')
                    else:
                        year, month, day = match.groups()
                        date_obj = datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d')
                    return date_obj
                except ValueError:
                    continue
        
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            pass
        
        try:
            return datetime.strptime(date_str, '%Y/%m/%d')
        except ValueError:
            pass
        
        return None