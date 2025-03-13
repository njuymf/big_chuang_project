import requests
import re  

def extract_bv_from_url(url):  
    pattern = r'BV[0-9A-Za-z]{10}'  
    match = re.search(pattern, url)  
    return match.group(0) if match else None  


def get_cid(bvid):
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        print("响应内容:", response.text)  # 打印响应内容
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0:
                cid = data['data']['cid']
                return cid
            else:
                print(f"请求失败，错误码: {data['code']}，错误信息: {data['message']}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"请求出现错误: {e}")
    return None

