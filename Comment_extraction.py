import os  
import csv  
import time  
from DrissionPage import ChromiumPage  # pip install DrissionPage  



# 保存路径初始化  
def init_save_path():  
    save_path = os.path.join(os.getcwd(), 'comments')  
    if not os.path.exists(save_path):  
        os.makedirs(save_path)  
    return save_path  


# 时间戳转换为日期时间  
def timestamp_to_datetime(timestamp):  
    try:  
        if timestamp == 0:  
            return "未知时间"  
        dt = time.localtime(timestamp)  
        return time.strftime("%Y-%m-%d %H:%M:%S", dt)  
    except (OSError, ValueError):  
        return "无效时间"  


# 初始化CSV文件  
def init_csv(file_path):  
    with open(file_path, 'w', encoding='utf-8', newline='') as f:  
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)  # 设置quoting为QUOTE_ALL  
        writer.writerow([  
            '评论类型', '评论层级', '评论ID', '评论内容', '评论点赞数', '评论回复数', '评论状态',   
            '评论时间', '用户昵称', '用户性别', '用户签名', '用户等级', '会员类型',   
            '会员到期时间', '认证类型', 'UP主是否点赞', 'UP主是否回复', 'IP属地'  
        ])  


# 保存评论数据到CSV  
def save_comments_to_csv(file_path, comments):  
    with open(file_path, 'a', encoding='utf-8', newline='') as f:  
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)  # 设置quoting为QUOTE_ALL  
        writer.writerows(comments)  


# 提取评论数据  
def extract_comments(response):  
    comments = []  
    try:  
        if 'data' in response and 'replies' in response['data']:  
            for data in response['data']['replies']:  
                # 提取基础信息  
                comment_type = data.get('type', 0)  
                comment_id = data.get('rpid', 0)  
                comment_content = data.get('content', {}).get('message', '').replace('\n', ' ').strip()  # 替换换行符并去除多余空格  
                comment_count = data.get('like', 0)  
                reply_count = data.get('rcount', 0)  
                comment_state = data.get('state', 0)  
                create_time = data.get('ctime', 0)  

                # 提取用户信息  
                member = data.get('member', {})  
                uname = member.get('uname', '匿名用户')  
                sex = member.get('sex', '保密')  
                sign = member.get('sign', '').replace('\n', ' ').strip()  # 替换换行符并去除多余空格  
                level_info = member.get('level_info', {})  
                current_level = level_info.get('current_level', 0)  

                # 提取会员信息  
                vip_info = member.get('vip', {})  
                vip_type = vip_info.get('vipType', 0)  
                vip_due = vip_info.get('vipDueDate', 0)  

                # 提取认证信息  
                official_verify = member.get('official_verify', {})  
                verify_type = official_verify.get('type', -1)  

                # 提取UP主互动信息  
                up_action = data.get('up_action', {})  
                is_up_liked = up_action.get('like', False)  
                is_up_replied = up_action.get('reply', False)  

                # 提取IP属地  
                location = data.get('reply_control', {}).get('location', '未知')  

                # 判断评论层级  
                parent_id = data.get('parent', 0)  
                comment_level = '一级评论' if parent_id == 0 else '二级评论'  

                # 转换时间戳  
                create_time_str = timestamp_to_datetime(create_time)  
                vip_due_str = timestamp_to_datetime(vip_due)  

                # 添加到评论列表  
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

    # 设置监听
    page.listen.start(['https://api.bilibili.com/x/v2/reply/wbi/main?', 'https://api.bilibili.com/x/v2/reply/wbi/reply?'])  

    # 访问页面  
    page.get(url)  
    time.sleep(3)  

    # 模拟滚动加载  
    for _ in range(int(num_pages) + 1):  
        page.scroll.to_bottom()  
        time.sleep(2)  

    # 捕获响应数据  
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


# 主函数
def main():
    # 配置参数
    url = input('请输入视频评论区URL: ')

    num_pages = input('请输入需要爬取的评论页数: ')


    # 初始化保存路径和CSV文件
    save_path = init_save_path()
    name = input('请输入保存文件名: ')
    file_path = os.path.join(save_path, f"{name}.csv")  
    init_csv(file_path)

    # 爬取评论数据
    responses = crawl_comments(url, num_pages, save_path)

    # 处理评论数据并保存
    total_comments = 0
    all_comments = []
    for response in responses:
        comments = extract_comments(response)
        total_comments += len(comments)
        all_comments.extend(comments)

    save_comments_to_csv(file_path, all_comments)

    # 打印总评论数
    print(f"总评论数量: {total_comments}")


if __name__ == '__main__':
    main()
