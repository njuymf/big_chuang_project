
from DrissionPage import ChromiumPage  #  pip install DrissionPage
import time


def timestamp_to_datetime(timestamp):
    if timestamp == 0:
        return "未知时间"
    dt = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", dt)




# URL = input("请输入B站视频链接:")
URL = 'https://www.bilibili.com/video/BV1J4y5YoEkY/?spm_id_from=333.337.search-card.all.click&vd_source=5e8e3112db65d765dc1283bfc35d140a'
# num = int(input("请输入要爬取的页面次数:"))
num = 2

page = ChromiumPage()
page.set.load_mode.none()

# 监听一级和二级评论的网络流
page.listen.start(['https://api.bilibili.com/x/v2/reply/wbi/main?', 'https://api.bilibili.com/x/v2/reply/wbi/reply?'])

# 访问B站页面
page.get(f'{URL}')
time.sleep(3)

for _ in range(num + 1):
    page.scroll.to_bottom()
    time.sleep(2)

# 用于存储所有捕获的响应数据
responses = []

try:
    # 循环监听直到达到所需数量或超时
    for _ in range(num):
        # 等待网络请求包到达
        packet = page.listen.wait()

        # 停止加载页面（这步可以根据需求调整）
        page.stop_loading()

        # 接收 HTTP 响应内容
        response_body = packet.response.body

        # 将响应内容存储到列表中
        responses.append(response_body)

        time.sleep(1)

except Exception as e:
    print(f"解析出现错误: {e}")

# 处理和打印捕获到的所有响应
total_comments = 0
for response in responses:
    try:
        if 'data' in response:
            if 'replies' in response['data']:
                datas = response['data']['replies']
                total_comments += len(datas)
                for data in datas:
                    # 提取基础信息
                    comment_type = data.get('type', 0)
                    parent_id = data.get('parent', 0)
                    comment_count = data.get('count', 0)
                    reply_count = data.get('rcount', 0)
                    comment_state = data.get('state', 0)
                    create_time = data.get('ctime', 0)
                    
                    # 提取用户信息
                    member = data.get('member', {})
                    uname = member.get('uname', '匿名用户')
                    sex = member.get('sex', '保密')
                    sign = member.get('sign', '')
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
                    comment_level = '一级评论' if parent_id == 0 else '二级评论'
                    
                    # 格式化输出
                    print(f"【评论信息】")
                    print(f"评论内容: {data.get('content', {}).get('message', '')}")
                    print(f"用户名: {uname}")
                    print(f"评论类型: {comment_type}（1=视频，3=动态，11=专栏）")
                    print(f"评论层级: {comment_level}")
                    print(f"IP属地: {location}")
                    print(f"字数统计: {comment_count}字")
                    print(f"回复数量: {reply_count}条")
                    print(f"发布时间: {timestamp_to_datetime(create_time)}")
                    print(f"评论状态: {comment_state}（0=正常，1=置顶，2=删除）")
                    
                    print("\n【用户信息】")
                    print(f"性别: {sex}")
                    print(f"个性签名: {sign}")
                    print(f"用户等级: {current_level}级")
                    print(f"会员类型: {vip_type}（1=月度，2=年度）")
                    print(f"会员到期: {vip_due}（毫秒级时间戳）")
                    print(f"认证类型: {verify_type}（-1=未认证）")
                    
                    print("\n【互动信息】")
                    print(f"被UP点赞: {is_up_liked}")
                    print(f"被UP回复: {is_up_replied}")
                    
                    print("\n" + "="*50 + "\n")
                    
    except KeyError as e:
        print(f"处理响应时出现错误: {e}")
        continue
page.close()

# 最后打印总评论数量
print(f"总评论数量: {total_comments}")
