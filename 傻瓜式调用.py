from Danmu_extraction import get_danmaku_from_url
from Video_download import download_video_from_url
import os
from Comment_extraction import get_comments_from_url
import time



def main():
    urls = [
        'https://www.bilibili.com/video/BV1gUQtYvEFC/?spm_id_from=333.1007.tianma.2-1-4.click&vd_source=5e8e3112db65d765dc1283bfc35d140a',
        'https://www.bilibili.com/video/BV1gUQtYvEFC/?spm_id_from=333.1007.tianma.2-1-4.click&vd_source=5e8e3112db65d765dc1283bfc35d140a'
    ]
    names = [
        'test1',
        'test2'
    ]
    num_pages = 1
    for url, name in zip(urls, names):
        get_danmaku_from_url(url, name)
        print(f"弹幕数据已保存到 {name}.csv")
        download_video_from_url(url, name)
        print(f"视频下载成功，保存路径为: {name}.mp4")
        get_comments_from_url(url, num_pages, name)
        print(f"评论数据已保存到 {name}.csv")
        



if __name__ == '__main__':
    main()

