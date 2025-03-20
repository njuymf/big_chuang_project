import requests  
import time  
import csv  
import re  

def trans_date(v_timestamp):  
    """10位时间戳转换为时间字符串"""  
    v_timestamp = float(v_timestamp)  
    timeArray = time.localtime(v_timestamp)  
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)  
    return otherStyleTime  

def fetch_oid_from_bv(bv):  
    """通过BV号转换为视频的oid"""  
    table = {}  
    tr = 'fZodR9XQDSUmKibc37upEhqv2nBxyCWGtJHszL6M48wAe1jTkPYgFaVo5r'  
    for i, c in enumerate(tr):  
        table[c] = i  
    s = [11, 10, 3, 8, 4, 6]  
    xor = 177451812  
    add = 8728348608  
    r = 0  
    for i in range(6):  
        r += table[bv[s[i]]] * 58 ** i  
    return (r - add) ^ xor  

def fecth_everything(comment):  
    gender = comment["member"]["sex"]  
    # 评论的时间  
    time_un = comment["ctime"]  
    publish_time = trans_date(time_un)  
    # 评论的IP属地  
    if "location" in comment["reply_control"]:  
        IP = comment["reply_control"]["location"].replace("IP属地：", "")  
    else:  
        IP = "未知"  
    # 评论的内容  
    content = comment["content"]["message"]  
    # 评论的点赞数  
    num = comment["like"]  

    return gender, publish_time, IP, content, num  

def fetch_comments(video_bv, headers, max_pages, csv_write):  # 最大页面数量可调整  
    oid = fetch_oid_from_bv(video_bv)  # 将BV号转换为oid  
    for page in range(1, max_pages + 1):  
        url = f'https://api.bilibili.com/x/v2/reply/main?next={page}&type=1&oid={oid}&mode=3'  
        print(url)  
        try:  
            # 添加超时设置  
            response = requests.get(url, headers=headers)  
            if response.status_code == 200:  
                data = response.json()  
                print(f"第{page}页已获取，over！")  
                if data['data']['replies'] == None:  
                    break  
                if data and 'replies' in data['data']:  
                    for comment in data['data']['replies']:  
                        gender, publish_time, IP, content, num = fecth_everything(comment)  
                        csv_write.writerow([gender, publish_time, IP, content, num])  

                        if comment["replies"]:  
                            for child in comment["replies"]:  
                                gender, publish_time, IP, content, num = fecth_everything(child)  
                                csv_write.writerow([gender, publish_time, IP, content, num])  
            else:  
                print(f"请求失败，状态码：{response.status_code}")  
                break  
        except requests.RequestException as e:  
            print(f"请求出错: {e}")  
            break  
        # 控制请求频率  
        time.sleep(1)  
    return  

# 打开文件  
f = open("comments.csv", mode="a", encoding="utf-8-sig")  
csv_write = csv.writer(f)  

video_bv = input("请输入Bvid号：")  # video_bv  
user_agent = input("请输入 User-Agent：")  
cookie = input("请输入 Cookie：")  

# 清理 User-Agent 和 Cookie 中可能的非法字符  
user_agent = re.sub(r'[^\x00-\x7F]', '', user_agent)  
cookie = re.sub(r'[^\x00-\x7F]', '', cookie)  

headers = {  
    'User-Agent': user_agent,  
    'Cookie': cookie  
}  

fetch_comments(video_bv=video_bv, headers=headers, max_pages=40, csv_write=csv_write)  
f.close()  