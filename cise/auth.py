import requests as rq
import netifaces
from model import RequestParams

# 随意，只要包含有如下均可
# ("Android", "iPhone", "SymbianOS", "Windows Phone", "iPad", "iPod")
mobile_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'

# 随意，只要不包含Mobile包含的均可
pc_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

# 生成 Post 请求参数
rp_generator = RequestParams()

# 获取接口mac和ip
rq_url = "http://172.16.4.32/webauth.do?wlanuserip=${ip}&wlanacname=bras&wlanusermac=${mac}"