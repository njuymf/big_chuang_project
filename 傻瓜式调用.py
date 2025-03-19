from Danmu_extraction import get_danmaku_from_url
from Video_download import download_video_from_url
import os
from Comment_extraction import get_comments_from_url
import time



def main():
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
        get_danmaku_from_url(url, name)
        print(f"弹幕数据已保存到 {name}.csv")
        download_video_from_url(url, name)
        print(f"视频下载成功，保存路径为: {name}.mp4")
        get_comments_from_url(url, num_pages, name)
        print(f"评论数据已保存到 {name}.csv")
        



if __name__ == '__main__':
    main()

