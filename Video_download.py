import os
import subprocess


def download_bilibili_video(url, save_path):
    try:
        # 构建 you-get 命令
        command = f'you-get -o {save_path} {url}'
        # 执行命令
        subprocess.run(command, shell=True, check=True)
        print(f"视频下载成功，保存路径为: {save_path}")
    except subprocess.CalledProcessError as e:
        print(f"下载过程中出现错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")


if __name__ == "__main__":
    # 输入 B 站视频的 URL
    video_url = input("请输入 B 站视频的 URL: ")
    # 初始化保存路径
    save_path = os.path.join(os.getcwd(), 'videos')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # 调用下载函数
    download_bilibili_video(video_url, save_path)
    
# 外部调用接口
def download_video_from_url(url, save_name=None):
    # 初始化保存路径
    save_path = os.path.join(os.getcwd(), 'videos')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # 调用下载函数
    download_bilibili_video(url, save_path)