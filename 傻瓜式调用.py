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

# 提取评论数据
def extract_comments(response):
    comments = []
    try:
        if 'data' in response and 'replies' in response['data']:
            for data in response['data']['replies']:
                comment_type = data.get('type', 0)
                comment_id = data.get('rpid', 0)
                comment_content = data.get('content', {}).get('message', '').replace('\n', ' ').strip()
                comment_count = data.get('like', 0)
                reply_count = data.get('rcount', 0)
                comment_state = data.get('state', 0)
                create_time = data.get('ctime', 0)

                member = data.get('member', {})
                uname = member.get('uname', '匿名用户')
                sex = member.get('sex', '保密')
                sign = member.get('sign', '').replace('\n', ' ').strip()
                level_info = member.get('level_info', {})
                current_level = level_info.get('current_level', 0)

                vip_info = member.get('vip', {})
                vip_type = vip_info.get('vipType', 0)
                vip_due = vip_info.get('vipDueDate', 0)

                official_verify = member.get('official_verify', {})
                verify_type = official_verify.get('type', -1)

                up_action = data.get('up_action', {})
                is_up_liked = up_action.get('like', False)
                is_up_replied = up_action.get('reply', False)

                location = data.get('reply_control', {}).get('location', '未知')

                parent_id = data.get('parent', 0)
                comment_level = '一级评论' if parent_id == 0 else '二级评论'

                create_time_str = timestamp_to_datetime(create_time)
                vip_due_str = timestamp_to_datetime(vip_due)

                comments.append([
                    comment_type, comment_level, comment_id, comment_content, comment_count,
                    reply_count, comment_state, create_time_str, uname, sex, sign,
                    current_level, vip_type, vip_due_str, verify_type, is_up_liked,
                    is_up_replied, location
                ])
            for first_level_comment in response['data']['replies']:
                if 'replies' in first_level_comment:
                    for second_level_comment in first_level_comment['replies']:
                        comment_type = second_level_comment.get('type', 0)
                        comment_id = second_level_comment.get('rpid', 0)
                        comment_content = second_level_comment.get('content', {}).get('message', '').replace('\n', ' ').strip()
                        comment_count = second_level_comment.get('like', 0)
                        reply_count = second_level_comment.get('rcount', 0)
                        comment_state = second_level_comment.get('state', 0)
                        create_time = second_level_comment.get('ctime', 0)

                        member = second_level_comment.get('member', {})
                        uname = member.get('uname', '匿名用户')
                        sex = member.get('sex', '保密')
                        sign = member.get('sign', '').replace('\n', ' ').strip()
                        level_info = member.get('level_info', {})
                        current_level = level_info.get('current_level', 0)

                        vip_info = member.get('vip', {})
                        vip_type = vip_info.get('vipType', 0)
                        vip_due = vip_info.get('vipDueDate', 0)

                        official_verify = member.get('official_verify', {})
                        verify_type = official_verify.get('type', -1)

                        up_action = second_level_comment.get('up_action', {})
                        is_up_liked = up_action.get('like', False)
                        is_up_replied = up_action.get('reply', False)

                        location = second_level_comment.get('reply_control', {}).get('location', '未知')

                        parent_id = second_level_comment.get('parent', 0)
                        comment_level = '一级评论' if parent_id == 0 else '二级评论'

                        create_time_str = timestamp_to_datetime(create_time)
                        vip_due_str = timestamp_to_datetime(vip_due)

                        comments.append([
                            comment_type, comment_level, comment_id, comment_content, comment_count,
                            reply_count, comment_state, create_time_str, uname, sex, sign,
                            current_level, vip_type, vip_due_str, verify_type, is_up_liked,
                            is_up_replied, location
                        ])
    except KeyError as e:
        print(f"处理响应时出现错误: {e}")
    return comments

# 爬取评论数据
def crawl_comments(url, num_pages, save_path):
    page = ChromiumPage()
    page.set.load_mode.none()

    page.listen.start([
        'https://api.bilibili.com/x/v2/reply/wbi/main?',
        'https://api.bilibili.com/x/v2/reply/wbi/reply?'
    ])

    page.get(url)
    time.sleep(3)

    for _ in range(int(num_pages) + 1):
        page.scroll.to_bottom()
        time.sleep(2)

    responses = []
    try:
        for _ in range(int(num_pages)):
            packet = page.listen.wait()
            page.stop_loading()
            responses.append(packet.response.body)
            time.sleep(1)
    except Exception as e:
        print(f"监听或解析出现错误: {e}")

    page.close()
    return responses

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
def main():
    url = input('请输入B站视频链接: ')
    num_pages = input('请输入需要爬取的评论页数: ')
    name = input('请输入保存的文件名: ')
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
    main()
