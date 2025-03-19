# %%
import json
import requests
import os
import time
import pandas as pd

# %%
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

# %%
def trans_date(v_timestamp):
    """10位时间戳转换为时间字符串"""
    timeArray = time.localtime(v_timestamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime

def get_top(url,headers):
    bv = url.replace("https://www.bilibili.com/video/","")
    index = 1

    urls=[]
    reply_id=[]
    replies=[]
    reply_time = []
    user_names=[]
    user_id=[]
    reply_like = []
    root_reply_id=[]
    parent_reply_id=[]
    is_root=[]

    requests.adapters.DEFAULT_RETRIES = 5 
    time.sleep(2)
    top_reply_url = r"https://api.bilibili.com/x/v2/reply?pn={index}&type=1&oid={bv}&sort=2".format(index=index,bv=bv)
    print(top_reply_url)
    response = requests.get(top_reply_url, headers=headers, )

    top_data = response.json()['data']['upper']['top']

    if top_data is not None and len(top_data)>0:
        top_reply_id = str(top_data['rpid_str'])
        top_reply = top_data['content']['message']
        top_reply_time = trans_date(top_data['ctime'])
        top_reply_user_name = top_data['member']['uname']
        top_user_id=top_data['member']['mid']
        top_reply_like = top_data['like']
        top_root_id = str(top_data['root_str'])
        top_parent_id = str(top_data['parent_str'])
        is_root_flag=1

        top_replies = response.json()['data']['top_replies']
        for top in top_replies:
            label=[]
            try:
                l = top['card_label']
                for lab in l:
                    label.append(lab['text_content'])
            except KeyError:
                pass


        urls.append(url)
        reply_id.append(top_reply_id)
        replies.append(top_reply)
        reply_time.append(top_reply_time)
        user_names.append(top_reply_user_name)
        user_id.append(top_user_id)
        reply_like.append(top_reply_like)
        root_reply_id.append(top_root_id)
        parent_reply_id.append(top_parent_id)
        is_root.append(is_root_flag)

        index1=1
        while True:
            requests.adapters.DEFAULT_RETRIES = 5 
            time.sleep(2)
            sub_reply_url = r"https://api.bilibili.com/x/v2/reply/reply?csrf=d3fd8d24eff948f61abff206eabc8de2&oid={bv}&pn={index1}&root={root}&type=1&sort=2".format(bv=bv,index1=index1,root=top_reply_id)
            print(sub_reply_url)
            response = requests.get(sub_reply_url, headers=headers, )
            sub = response.json()['data']['replies']
            index1 = index1 + 1
            if sub is not None and len(sub)>0:
                for subi in sub:
                    rpid=str(subi['rpid_str'])
                    sub_reply = subi['content']['message']
                    sub_reply_time = trans_date(subi['ctime'])
                    sub_reply_user_name = subi['member']['uname']
                    sub_user_id = subi['member']['mid']
                    sub_reply_like = subi['like']
                    sub_root_id = str(subi['root_str'])
                    sub_parent_id = str(subi['parent_str'])
                    is_root_flag = 0

                    urls.append(url)
                    reply_id.append(rpid)
                    replies.append(sub_reply)
                    reply_time.append(sub_reply_time)
                    user_names.append(sub_reply_user_name)
                    user_id.append(sub_user_id)
                    reply_like.append(sub_reply_like)
                    root_reply_id.append(sub_root_id)
                    parent_reply_id.append(sub_parent_id)
                    is_root.append(is_root_flag)
            else:
                break
    else:
        print("There is no top reply.")
    
    data = {
        'url':urls,
        'reply_id':reply_id,
        'reply_content':replies,
        'reply_time':reply_time,
        'user_name':user_names,
        'user_id':user_id,
        'reply_like':reply_like,
        "root_reply_id":root_reply_id,
        "parent_reply_id":parent_reply_id,
        'is_root':is_root,
    }

    df = pd.DataFrame(data)
    response.close()
    return df


def get_root(url,headers):
    bv = url.replace("https://www.bilibili.com/video/","")
    index = 1
    
    urls=[]
    reply_id=[]
    replies=[]
    reply_time = []
    user_names=[]
    user_id=[]
    reply_like = []
    root_reply_id=[]
    parent_reply_id=[]
    is_root=[]

    while True:
        requests.adapters.DEFAULT_RETRIES = 5 
        time.sleep(2)
        root_reply_url = r"https://api.bilibili.com/x/v2/reply?pn={index}&type=1&oid={bv}&sort=2".format(index=index,bv=bv)
        print(root_reply_url)
        response = requests.get(root_reply_url, headers=headers, )

        root_reply_data = response.json()['data']['replies']
        index = index + 1
        if root_reply_data is not None and len(root_reply_data)>0:
            for reply in root_reply_data:
                rpid=str(reply['rpid_str'])
                root_reply = reply['content']['message']
                root_reply_submit_time = trans_date(reply['ctime'])
                root_reply_user_name = reply['member']['uname']
                root_reply_user_id=reply['member']['mid']
                root_reply_like = reply['like']
                root_root_id = str(reply['root_str'])
                root_parent_id = str(reply['parent_str'])
                is_root_flag=1

                try:
                    l = reply['card_label']
                    for lab in l:
                        label.append(lab['text_content'])

                except KeyError:
                    pass
                    #print("there is no label.")

                urls.append(url)
                reply_id.append(rpid)
                replies.append(root_reply)
                reply_time.append(root_reply_submit_time)
                user_names.append(root_reply_user_name)
                user_id.append(root_reply_user_id)
                reply_like.append(root_reply_like)
                root_reply_id.append(root_root_id)
                parent_reply_id.append(root_parent_id)
                is_root.append(is_root_flag)


                #sub-reply
                try:
    
                    reply_count = reply['reply_control']['sub_reply_entry_text']
                    reply_count = reply_count.replace("共","")
                    reply_count = reply_count.replace("条回复","")
                    if int(reply_count)>0:
                        rpid_str = reply['rpid_str']
                        index1=1
                        while True:
                            requests.adapters.DEFAULT_RETRIES = 5 
                            time.sleep(2)
                            sub_reply_url = r"https://api.bilibili.com/x/v2/reply/reply?csrf=d3fd8d24eff948f61abff206eabc8de2&oid={bv}&pn={index1}&root={root}&type=1&sort=2".format(bv=bv,index1=index1,root=rpid_str)
                            print(sub_reply_url)
                            response = requests.get(sub_reply_url, headers=headers, )
                            sub = response.json()['data']['replies']
                            index1 = index1 + 1
                            if sub is not None and len(sub)>0:
                                for subi in sub:
                                    rpid = str(subi['rpid_str'])
                                    sub_reply = subi['content']['message']
                                    sub_reply_time = trans_date(subi['ctime'])
                                    sub_reply_user_name = subi['member']['uname']
                                    sub_reply_user_id=subi['member']['mid']
                                    sub_reply_like = subi['like']
                                    sub_root_id = str(subi['root_str'])
                                    sub_parent_id = str(subi['parent_str'])
                                    is_root_flag=0
                                    label = []

                                    urls.append(url)
                                    reply_id.append(rpid)
                                    replies.append(sub_reply)
                                    reply_time.append(sub_reply_time)
                                    user_names.append(sub_reply_user_name)
                                    user_id.append(sub_reply_user_id)
                                    reply_like.append(sub_reply_like)
                                    root_reply_id.append(sub_root_id)
                                    parent_reply_id.append(sub_parent_id)
                                    is_root.append(is_root_flag)
                            else:
                                break
                    else:
                        print("there is something wrong.")
                except KeyError:
                    pass

        else:
            print("There is no root reply.")
            break
        
    data = {
        'url':urls,
        'reply_id':reply_id,
        'reply_content':replies,
        'reply_time':reply_time,
        'user_name':user_names,
        'user_id':user_id,
        'reply_like':reply_like,
        "root_reply_id":root_reply_id,
        "parent_reply_id":parent_reply_id,
        'is_root':is_root,
    }

    df = pd.DataFrame(data)
    response.close()
    return df


# %%
if __name__ == "__main__":

    url_list = ["BV1BVB9YEEW4","BV1rbzMYYExk","BV1x6BWY7Eft","BV1sBB9YcEAF","BV1giB2YJEuu","BV1CFzzY9EU6","BV1nSB9YXENE","BV1NbzgYGEDz","BV1PbzYY6EGG"]
    num = 1
    for url in url_list:
        bv = url.replace("https://www.bilibili.com/video/","")
        print("the url of this video is "+url)
        requests.adapters.DEFAULT_RETRIES = 5 
        time.sleep(3)
        video_url = r"https://api.bilibili.com/x/v2/reply?pn=1&type=1&oid={bv}&sort=2".format(bv=bv)
        response = requests.get(video_url, headers=headers)
        if len(response.json()) == 3:
            num += 1
            print("此链接已失效")
            continue
        data1 = get_top(url,headers)
        data2 = get_root(url,headers)
        data0 = pd.concat([data1, data2], ignore_index=True)

        # 为每个视频创建一个独立的 CSV 文件
        file_name = f"comment_{bv}.csv"
        data0.to_csv(file_name)

        print(f"已爬完第 {num} 条视频，评论数据已保存到 {file_name}")
        num += 1


