import os
import subprocess
import requests
import xml.etree.ElementTree as ET
import csv
import re
import time
from DrissionPage import ChromiumPage

# 从链接中提取BV号
def extract_bv_from_url(url):
    pattern = r'BV[0-9A-Za-z]{10}'
    match = re.search(pattern, url)
    return match.group(0) if match else None

# 根据BV号获取CID
def get_cid(bvid):
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
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

# 根据CID获取弹幕数据
def get_danmaku(cid):
    url = f"https://api.bilibili.com/x/v1/dm/list.so?oid={cid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        xml_data = response.text
        root = ET.fromstring(xml_data)
        danmaku_list = []
        for d in root.findall('d'):
            p = d.get('p')
            parts = p.split(',')
            time = float(parts[0])
            danmaku = d.text
            danmaku_list.append((time, danmaku))
        return danmaku_list
    except Exception as e:
        print(f"获取弹幕数据时出现错误: {e}")
        return []

# 将弹幕数据保存到CSV文件
def save_danmaku_to_csv(danmaku_list, file_path):
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['时间', '弹幕内容'])
        for time, danmaku in danmaku_list:
            writer.writerow([time, danmaku])

# 时间戳转换为日期时间
def timestamp_to_datetime(timestamp):
    try:
        if timestamp == 0:
            return "未知时间"
        dt = time.localtime(timestamp)
        return time.strftime("%Y-%m-%d %H:%M:%S", dt)
    except (OSError, ValueError):
        return "无效时间"

# 初始化保存路径
def init_save_path(folder_name):
    save_path = os.path.join(os.getcwd(), folder_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    return save_path

# 初始化CSV文件
def init_csv(file_path):
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow([
            '评论类型', '评论层级', '评论ID', '评论内容', '评论点赞数', '评论回复数', '评论状态',
            '评论时间', '用户昵称', '用户性别', '用户签名', '用户等级', '会员类型',
            '会员到期时间', '认证类型', 'UP主是否点赞', 'UP主是否回复', 'IP属地'
        ])

# 保存评论数据到CSV
def save_comments_to_csv(file_path, comments):
    with open(file_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(comments)

# 爬取评论数据
def crawl_comments(url, num_pages, save_path):
    page = ChromiumPage()
    page.set.load_mode.none()  # 禁用图片等加载加速

    # 监听评论API（主评论+回复）
    page.listen.start([
        'https://api.bilibili.com/x/v2/reply/wbi/main?',  # 主评论
        'https://api.bilibili.com/x/v2/reply/wbi/reply?'  # 回复
    ])

    page.get(url)
    time.sleep(3)  # 等待初始加载

    # 滚动加载评论（初始1页 + 滚动num_pages页 = 共num_pages+1页）
    for _ in range(num_pages):
        page.scroll.to_bottom()  # 滚动到底部加载下一页
        time.sleep(1.5)  # 优化等待时间

    responses = []
    try:
        # 捕获主评论请求（初始1页 + 滚动加载的num_pages页）
        for _ in range(num_pages + 1):
            # 增加超时控制（5秒内未捕获请求则跳过）
            packet = page.listen.wait(timeout=5)  
            if packet:
                responses.append(packet.response.json())
            page.stop_loading()  # 停止加载减少资源占用
            time.sleep(0.5)
    except Exception as e:
        print(f"监听错误: {e}")
    finally:
        page.close()
    return responses

# 提取评论数据（优化去重）
def extract_comments(response):
    comments = []
    try:
        if 'data' not in response or 'replies' not in response['data']:
            return comments
        
        for comment in response['data']['replies']:
            # 解析一级评论
            parse_comment(comments, comment, '一级评论')
            # 解析二级评论（直接通过replies字段获取，无需重复遍历）
            if 'replies' in comment:
                for reply in comment['replies']:
                    parse_comment(comments, reply, '二级评论')
    except KeyError as e:
        print(f"解析错误: {e}")
    return comments

# 独立评论解析函数
def parse_comment(comments, data, level):
    comment_type = data.get('type', 0)
    comment_id = data.get('rpid', 0)
    content = data.get('content', {}).get('message', '').replace('\n', ' ').strip()
    like = data.get('like', 0)
    reply_count = data.get('rcount', 0)
    state = data.get('state', 0)
    ctime = timestamp_to_datetime(data.get('ctime', 0))
    
    member = data.get('member', {})
    uname = member.get('uname', '匿名用户')
    sex = member.get('sex', '保密')
    sign = member.get('sign', '').replace('\n', ' ').strip()
    level = member.get('level_info', {}).get('current_level', 0)
    vip_type = member.get('vip', {}).get('vipType', 0)
    vip_due = timestamp_to_datetime(member.get('vip', {}).get('vipDueDate', 0))
    verify = member.get('official_verify', {}).get('type', -1)
    
    up_liked = data.get('up_action', {}).get('like', False)
    up_replied = data.get('up_action', {}).get('reply', False)
    location = data.get('reply_control', {}).get('location', '未知')
    
    comments.append([
        comment_type, level, comment_id, content, like, reply_count, state,
        ctime, uname, sex, sign, level, vip_type, vip_due, verify,
        up_liked, up_replied, location
    ])

# 下载B站视频
def download_bilibili_video(url, save_path):
    try:
        command = f'you-get -o {save_path} {url}'
        subprocess.run(command, shell=True, check=True)
        print(f"视频下载成功，保存路径为: {save_path}")
    except subprocess.CalledProcessError as e:
        print(f"下载过程中出现错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

# 主函数
def main(url, num_pages, name):

    # 提取BV号和CID
    bvid = extract_bv_from_url(url)
    cid = get_cid(bvid)
    if not cid:
        print("获取视频cid失败")
        return

    # 提取弹幕数据
    danmaku_save_path = init_save_path('danmaku')
    danmaku_file_path = os.path.join(danmaku_save_path, f"{name}.csv")
    danmaku_list = get_danmaku(cid)
    save_danmaku_to_csv(danmaku_list, danmaku_file_path)
    print(f"弹幕数据已保存到 {danmaku_file_path}")

    # 提取评论数据
    comment_save_path = init_save_path('comments')
    comment_file_path = os.path.join(comment_save_path, f"{name}.csv")
    init_csv(comment_file_path)
    responses = crawl_comments(url, num_pages, comment_save_path)
    total_comments = 0
    all_comments = []
    for response in responses:
        comments = extract_comments(response)
        total_comments += len(comments)
        all_comments.extend(comments)
    save_comments_to_csv(comment_file_path, all_comments)
    print(f"总评论数量: {total_comments}，评论数据已保存到 {comment_file_path}")

    # 下载视频
    video_save_path = init_save_path('videos')
    download_bilibili_video(url, video_save_path)

if __name__ == '__main__':

    urls = [
        'https://www.bilibili.com/video/BV1BVB9YEEW4/?spm_id_from=333.337.search-card.all.click&vd_source=cc29f8cdcfb9702b54c8a897374488a2',
        'https://www.bilibili.com/video/BV1rbzMYYExk/?spm_id_from=333.337.search-card.all.click&vd_source=cc29f8cdcfb9702b54c8a897374488a2',
        'https://www.bilibili.com/video/BV1x6BWY7Eft/?spm_id_from=333.337.search-card.all.click&vd_source=cc29f8cdcfb9702b54c8a897374488a2',
        'https://www.bilibili.com/video/BV1sBB9YcEAF/?spm_id_from=333.337.search-card.all.click&vd_source=cc29f8cdcfb9702b54c8a897374488a2',
        'https://www.bilibili.com/video/BV1giB2YJEuu/?spm_id_from=333.337.search-card.all.click&vd_source=cc29f8cdcfb9702b54c8a897374488a2',
        'https://www.bilibili.com/video/BV1CFzzY9EU6/?spm_id_from=333.337.search-card.all.click&vd_source=cc29f8cdcfb9702b54c8a897374488a2',
        'https://bilibili.com/video/BV1nSB9YXENE/?spm_id_from=333.337.search-card.all.click&vd_source=cc29f8cdcfb9702b54c8a897374488a2',
        'https://www.bilibili.com/video/BV1NbzgYGEDz/?spm_id_from=333.337.search-card.all.click&vd_source=567fe6f146ff0eb55bd447b9bb79d383',
        'https://www.bilibili.com/video/BV1PbzYY6EGG/?spm_id_from=333.337.search-card.all.click&vd_source=567fe6f146ff0eb55bd447b9bb79d383'
    ]
    num_pages = 420
    names = ['北大博士', '央财硕士', '羊毛月删除视频道歉','晓艳教英语','取关了好恶心','二本自媒体','都别放过这个羊毛月','北大学霸人设','老梁不郁闷']
    for url, name in zip(urls, names):
        main(url, num_pages, name)