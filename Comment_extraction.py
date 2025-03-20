import json
import requests
import os
import time
import pandas as pd

# 请求头
headers = {
    'authority': 'api.bilibili.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    # 需定期更换cookie，否则location爬不到
    'cookie': "buvid3=49F8377F-B0DF-54E1-02AD-6C78EF6B0DAD53407infoc; b_nut=1741857453; _uuid=3EF53A1B-29410-573A-6FF8-5DA2142A837F53772infoc; enable_web_push=DISABLE; enable_feed_channel=ENABLE; buvid4=5BB30908-589F-E7FC-C504-2292E41EF69854018-025031309-vlq9QL6MN%2BQSSB5ycKFSHA%3D%3D; buvid_fp=4f2cb5380de1021242d1d42090b0f193; header_theme_version=CLOSE; DedeUserID=662009067; DedeUserID__ckMd5=73a61d5667bbbf0d; CURRENT_FNVAL=2000; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDI2MzAxMjcsImlhdCI6MTc0MjM3MDg2NywicGx0IjotMX0.F3N0a9o_RS03LeVeW9hCHhPcTLlOQj3aEWnYZoQBDMU; bili_ticket_expires=1742630067; SESSDATA=e502c7ad%2C1757922928%2Cf3532%2A32CjB9tDUv-gRBVg1EuxYPPYV4GatI28PIvLHYNGr7q7kkNw-BsSsHkmrenesM8V4z2ywSVlpral90OUtNZHkxR0JQaTNxcjRuRjhxejVVaC1nQWRQTE5BMDhUa19wYXpRcW9EU1hOR0J1dHZDemktU3JsMTVaTURrUUM0WFVYcWh6SmJzNlgyY0R3IIEC; bili_jct=7266f204dbdf49a075a9b50d76ef54bc; sid=867jfmg6; bp_t_offset_662009067=1045964324876582912; b_lsid=4E914C10A_195AE34662C; home_feed_column=4; browser_resolution=885-731",
    'origin': 'https://www.bilibili.com',
    'referer': 'https://www.bilibili.com/video/BV1FG4y1Z7po/?spm_id_from=333.337.search-card.all.click&vd_source=69a50ad969074af9e79ad13b34b1a548',
    'sec-ch-ua': '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.47'
}

# 定义全局变量
urls = []
reply_id = []
replies = []
reply_time = []
user_names = []
user_id = []
reply_like = []
root_reply_id = []
parent_reply_id = []
is_root = []
up_likeds = []
up_replieds = []
ip_locations = []
vip_types = []
vip_due_dates = []
verify_types = []
comment_levels = []  # 评论层级


def trans_date(v_timestamp):
    """10位时间戳转换为时间字符串"""
    timeArray = time.localtime(v_timestamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


def parse_comment(url, bv, is_top=False, root_id=None):
    """通用评论解析函数"""
    global urls, reply_id, replies, reply_time, user_names, user_id, reply_like, root_reply_id, parent_reply_id, is_root
    global comment_levels
    index = 1 if is_top else 1  # 置顶评论只取第一页

    def clean_text(text):
        """删除换行符、回车符、制表符"""
        return text.replace('\n', '').replace('\r', '').replace('\t', '').strip()  # 或用正则：re.sub(r'[\n\r\t]', '', text).strip()

    while True:
        # 构造不同类型的URL
        if is_top:
            comment_url = f"https://api.bilibili.com/x/v2/reply?pn={index}&type=1&oid={bv}&sort=2"
        else:
            comment_url = f"https://api.bilibili.com/x/v2/reply?pn={index}&type=1&oid={bv}&sort=2"

        print(f"正在请求{comment_url}")
        response = requests.get(comment_url, headers=headers)
        data = response.json().get('data', {})

        # 获取主评论列表
        main_replies = data.get('upper', {}).get('top', []) if is_top else data.get('replies', [])

        if not main_replies:
            if is_top or index > 1:
                break
            print("There is no root reply.")
            break

        for reply in main_replies if is_top else main_replies:
            # 解析主评论
            rpid = str(reply.get('rpid_str', ''))
            content = reply.get('content', {}).get('message', '')
            
            content = clean_text(content)
            ctime = trans_date(reply.get('ctime', 0))
            member = reply.get('member', {})
            uname = member.get('uname', '')
            mid = member.get('mid', 0)
            like = reply.get('like', 0)
            root = str(reply.get('root_str', ''))
            parent = str(reply.get('parent_str', ''))
            is_root_flag = 1 if (is_top or root == rpid) else 0
            # 提取UP主是否点赞
            up_liked = reply['up_action']['like']
            # 提取UP主是否回复
            up_replied = reply['up_action']['reply']
            # 提取IP属地
            reply_control = reply.get('reply_control', {})
            ip_location = reply_control.get('location', '未知').replace('IP属地：', '')
            # 提取会员类型
            vip_type = reply['member']['vip']['vipType']
            if vip_type == 0:
                vip_type_str = "非会员"
            elif vip_type == 1:
                vip_type_str = "月度大会员"
            elif vip_type == 2:
                vip_type_str = "年度大会员"
            else:
                vip_type_str = "未知类型"

            # 提取会员到期时间
            vip_due_date = reply['member']['vip']['vipDueDate']
            if vip_due_date:
                vip_due_date_str = trans_date(vip_due_date // 1000)  # 注意时间戳可能是毫秒级，需要转换为秒
            else:
                vip_due_date_str = "无到期时间"

            # 提取认证类型
            verify_type = reply['member']['official_verify']['type']
            if verify_type == -1:
                verify_type_str = "未认证"
            elif verify_type == 0:
                verify_type_str = "个人认证"
            elif verify_type == 1:
                verify_type_str = "企业认证"
            else:
                verify_type_str = "未知认证类型"

            # 判断评论层级
            parent_id = data.get('parent', 0)
            comment_level = '一级评论' if parent_id == 0 else '二级评论'
            # 收集主评论数据
            urls.append(url)
            reply_id.append(rpid)
            replies.append(content)
            reply_time.append(ctime)
            user_names.append(uname)
            user_id.append(mid)
            reply_like.append(like)
            root_reply_id.append(root)
            parent_reply_id.append(parent)
            is_root.append(is_root_flag)
            up_likeds.append(up_liked)
            up_replieds.append(up_replied)
            ip_locations.append(ip_location)
            vip_types.append(vip_type_str)
            vip_due_dates.append(vip_due_date_str)
            verify_types.append(verify_type_str)
            comment_levels.append(comment_level)



            # 处理子评论
            if not is_top:
                sub_reply_count = reply.get('reply_control', {}).get('sub_reply_entry_text', '0条回复')
                sub_count = int(sub_reply_count.replace('共', '').replace('条回复', ''))
                if sub_count > 0:
                    parse_sub_comment(url, bv, rpid)

        if not is_top:
            index += 1
        else:
            break  # 置顶评论只取第一页

    response.close()
    return {
        'url': urls,
        'reply_id': reply_id,
        'reply_content': replies,
        'reply_time': reply_time,
        'user_name': user_names,
        'user_id': user_id,
        'reply_like': reply_like,
        "root_reply_id": root_reply_id,
        "parent_reply_id": parent_reply_id,
        'is_root': is_root,
        'up_liked': up_likeds,
        'up_replied': up_replieds,
        'ip_location': ip_locations,
        'vip_type': vip_types,
        'vip_due_date': vip_due_dates,
        'verify_type': verify_types,
        'comment_level': comment_levels
    }


def parse_sub_comment(url, bv, root_id):
    """子评论解析函数"""
    global urls, reply_id, replies, reply_time, user_names, user_id, reply_like, root_reply_id, parent_reply_id, is_root
    global comment_levels

    index1 = 1

    def clean_text(text):   
        """删除换行符、回车符、制表符"""
        return text.replace('\n', '').replace('\r', '').replace('\t', '').strip()
    while True:
        sub_url = f"https://api.bilibili.com/x/v2/reply/reply?csrf=d3fd8d24eff948f61abff206eabc8de2&oid={bv}&pn={index1}&root={root_id}&type=1&sort=2"
        print(f"正在请求子评论页{index1}: {sub_url}")

        response = requests.get(sub_url, headers=headers)
        sub_data = response.json().get('data', {}).get('replies', [])

        if not sub_data:
            break

        for sub in sub_data:
            rpid = str(sub.get('rpid_str', ''))
            content = sub.get('content', {}).get('message', '')
            content = clean_text(content)
            ctime = trans_date(sub.get('ctime', 0))
            member = sub.get('member', {})
            uname = member.get('uname', '')
            mid = member.get('mid', 0)
            like = sub.get('like', 0)
            root = str(sub.get('root_str', ''))
            parent = str(sub.get('parent_str', ''))
            # 提取UP主是否点赞
            up_liked = sub['up_action']['like']
            # 提取UP主是否回复
            up_replied = sub['up_action']['reply']
            # 提取IP属地
            reply_control = sub.get('reply_control', {})
            ip_location = reply_control.get('location', '未知').replace('IP属地：', '')
            # 提取会员类型
            vip_type = sub['member']['vip']['vipType']
            if vip_type == 0:
                vip_type_str = "非会员"
            elif vip_type == 1:
                vip_type_str = "月度大会员"
            elif vip_type == 2:
                vip_type_str = "年度大会员"
            else:
                vip_type_str = "未知类型"

            # 提取会员到期时间
            vip_due_date = sub['member']['vip']['vipDueDate']
            if vip_due_date:
                vip_due_date_str = trans_date(vip_due_date // 1000)  # 注意时间戳可能是毫秒级，需要转换为秒
            else:
                vip_due_date_str = "无到期时间"

            # 提取认证类型
            verify_type = sub['member']['official_verify']['type']
            if verify_type == -1:
                verify_type_str = "未认证"
            elif verify_type == 0:
                verify_type_str = "个人认证"
            elif verify_type == 1:
                verify_type_str = "企业认证"
            else:
                verify_type_str = "未知认证类型"
            # 判断评论层级
            parent_id = sub.get('parent', 0)
            comment_level = '一级评论' if parent_id == 0 else '二级评论'

            urls.append(url)
            reply_id.append(rpid)
            replies.append(content)
            reply_time.append(ctime)
            user_names.append(uname)
            user_id.append(mid)
            reply_like.append(like)
            root_reply_id.append(root)
            parent_reply_id.append(parent)
            is_root.append(0)
            up_likeds.append(up_liked)
            up_replieds.append(up_replied)
            ip_locations.append(ip_location)
            vip_types.append(vip_type_str)
            vip_due_dates.append(vip_due_date_str)
            verify_types.append(verify_type_str)
            comment_levels.append(comment_level)

        index1 += 1
    response.close()

def initialize():
    """初始化全局变量"""
    global urls, reply_id, replies, reply_time, user_names
    global user_id, reply_like, root_reply_id, parent_reply_id, is_root
    global comment_levels

    global up_likeds, up_replieds, ip_locations, vip_types, vip_due_dates, verify_types
    urls = []
    reply_id = []
    replies = []
    reply_time = []
    user_names = []
    user_id = []
    reply_like = []
    root_reply_id = []
    parent_reply_id = []
    is_root = []
    up_likeds = []
    up_replieds = []
    ip_locations = []
    vip_types = []
    vip_due_dates = []
    verify_types = []
    comment_levels = []  # 评论层级

def get_top(url, headers):
    """获取置顶评论（简化后）"""
    global comment_levels

    global urls, reply_id, replies, reply_time, user_names, user_id, reply_like, root_reply_id, parent_reply_id, is_root
    initialize()  # 初始化全局变量
    bv = url.replace("https://www.bilibili.com/video/", "")
    data = parse_comment(url, bv, is_top=True)
    return pd.DataFrame(data)


def get_root(url, headers):
    """获取根评论（简化后）"""
    global urls, reply_id, replies, reply_time, user_names, user_id, reply_like, root_reply_id, parent_reply_id, is_root
    global comment_levels

    initialize()  # 初始化全局变量
    bv = url.replace("https://www.bilibili.com/video/", "")
    data = parse_comment(url, bv)
    return pd.DataFrame(data)


if __name__ == "__main__":

    url_list = ["BV1LvXFYeEkX","BV1ukKGesEhD", "BV1BVB9YEEW4", "BV1rbzMYYExk","BV1x6BWY7Eft", "BV1sBB9YcEAF", "BV1giB2YJEuu",
                "BV1CFzzY9EU6", "BV1nSB9YXENE", "BV1NbzgYGEDz", "BV1PbzYY6EGG"]
    num = 1
    for url in url_list:
        bv = url.replace("https://www.bilibili.com/video/", "")
        print("the url of this video is " + url)
        requests.adapters.DEFAULT_RETRIES = 5
        # time.sleep(0.1)
        video_url = r"https://api.bilibili.com/x/v2/reply?pn=1&type=1&oid={bv}&sort=2".format(bv=bv)
        response = requests.get(video_url, headers=headers)
        if len(response.json()) == 3:
            num += 1
            print("此链接已失效")
            continue
        data1 = get_top(url, headers)
        data2 = get_root(url, headers)
        data0 = pd.concat([data1, data2], ignore_index=True)

        # 为每个视频创建一个独立的 CSV 文件
        file_name = f"comment_{bv}.csv"
        data0.to_csv(file_name)

        print(f"已爬完第 {num} 条视频，评论数据已保存到 {file_name}")
        num += 1

    print("所有视频评论爬取完成！")

from Get_cid import extract_bv_from_url, get_cid
