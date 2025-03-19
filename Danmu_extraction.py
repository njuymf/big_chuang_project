import requests
import xml.etree.ElementTree as ET
import os
import csv
from Get_cid import get_cid
import requests
from Get_cid import extract_bv_from_url


def get_danmaku(cid):
    """
    根据视频的cid获取弹幕数据
    :param cid: 视频的cid
    :return: 包含弹幕内容和发送时间的列表
    """
    url = f"https://api.bilibili.com/x/v1/dm/list.so?oid={cid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        xml_data = response.text
        root = ET.fromstring(xml_data)
        danmaku_list = []
        for d in root.findall('d'):
            # 提取弹幕发送时间
            p = d.get('p')
            parts = p.split(',')
            time = float(parts[0])
            danmaku = d.text
            danmaku_list.append((time, danmaku))
        return danmaku_list
    except Exception as e:
        print(f"获取弹幕数据时出现错误: {e}")
        return []


def save_danmaku_to_csv(danmaku_list, file_path):
    """
    将包含弹幕内容和发送时间的列表保存到 CSV 文件中
    :param danmaku_list: 包含弹幕内容和发送时间的列表
    :param file_path: 保存文件的路径
    """
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # 写入 CSV 文件的表头
        writer.writerow(['时间', '弹幕内容'])
        for time, danmaku in danmaku_list:
            writer.writerow([time, danmaku])


def main():
    url = input('请输入视频链接: ')
    # 提取视频的cid
    bvid = extract_bv_from_url(url)
    cid = get_cid(bvid)
    if not cid:
        print("获取视频cid失败")
        return

    # 输入视频的cid
    # cid = input('请输入视频的cid: ')
    # 初始化保存路径
    save_path = os.path.join(os.getcwd(), 'danmaku')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    file_path = os.path.join(save_path, f"{cid}.csv")
    # 获取弹幕数据
    danmaku_list = get_danmaku(cid)
    # 保存弹幕数据到 CSV 文件
    save_danmaku_to_csv(danmaku_list, file_path)
    print(f"弹幕数据已保存到 {file_path}")


if __name__ == '__main__':
    main()
    
# 外部调用接口
def get_danmaku_from_url(url,save_name=None):
    # 提取视频的cid
    bvid = extract_bv_from_url(url)
    cid = get_cid(bvid)
    if not cid:
        print("获取视频cid失败")
        return

    # 输入视频的cid
    # cid = input('请输入视频的cid: ')
    # 初始化保存路径
    save_path = os.path.join(os.getcwd(), 'danmaku')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    file_path = os.path.join(save_path, f"{save_name}.csv")
    # 获取弹幕数据
    danmaku_list = get_danmaku(cid)
    # 保存弹幕数据到 CSV 文件
    save_danmaku_to_csv(danmaku_list, file_path)
    print(f"弹幕数据已保存到 {file_path}")