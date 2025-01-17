import logging
import os
from urllib.parse import urlparse
import requests
import typer

logger = logging.getLogger(__name__)

headers={
    "Referer":"https://www.douyin.com/",
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

def main(url_file:str, out_dir:str):
    os.makedirs(out_dir, exist_ok=True)

    urls:list[str] = []
    with open(url_file, 'r') as file:
        for l in file:
            urls.append(l)
    for url in urls:
        try:
            file_name = url.split("=").pop().replace("\n","")
            file_name = file_name+".mp4"

            video_response = requests.get(url=url,headers=headers)
            print(video_response.status_code)
            if video_response.status_code > 300:
                raise Exception(f"视频文件下载失败, {url}, {video_response.status_code}")
            # return
            with open(os.path.join(out_dir, file_name), 'wb') as video_file:
                video_file.write(video_response.content)

        except Exception as e:
            logger.error(f'download {url} fail, {e}')
        # break

if __name__ == "__main__":
    typer.run(main)
