import logging
import os
from urllib.parse import urlparse
import requests
import typer

logger = logging.getLogger(__name__)

headers={
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Cookie':'clientid=3; did=web_b582502c39f84565e87cc1a2591bd6e9; client_key=65890b29; kpn=GAME_ZONE; _did=web_6331593AFB407B; did=web_d5ac1f0563f2507f89bf6c64bb3d5379208d; kuaishou.live.bfb1s=3e261140b0cf7444a0ba411c6f227d88; userId=1767658279; userId=1767658279; kuaishou.live.web_st=ChRrdWFpc2hvdS5saXZlLndlYi5zdBKgATLFByGhJF0nozYkeH-xz8gmwgUv6Re9gWh226YtdV3SmgvRwxm-crhOcLCsOB-qmmkQX7EbebGMdRAW4orXe2WazVhBS141M2BFeTlrEi0EaYUHf6waJHBulLAtCgAt8fcHxkaeeOU9tqUjnB6ccj02Uspxm2BHAtV6Azh-yImmCrIznooE4P4flEHeQhY0PxkdDn1BQVuAClojeXEsEycaEgL1c1j1KEeWrOe8x-vTC5n9jyIgvJmGs_wYPUnMQ1Sx3I5l2yWeEkSW6VuFPFKl51kXyB0oBTAB; kuaishou.live.web_ph=ca8dc941f56f17a3d09a524b4fd72eebc525',
}

def main(url_file:str, out_dir:str):
    os.makedirs(out_dir, exist_ok=True)

    urls:set[str] = set()
    with open(url_file, 'r') as file:
        urls.update([v.strip() for v in file.read().split("\n") if v.strip() != ""])

    for url in urls:
        try:
            paly_url = get_play_url(url)
            u = urlparse(paly_url)
            file_name = u.path.split("/").pop()
            if file_name == "":
                raise Exception(f"无法解析视频文件名, {paly_url}")

            video_response = requests.get(paly_url)
            if video_response.status_code != 200:
                raise Exception(f"视频文件下载失败, {paly_url}")
            
            with open(os.path.join(out_dir, file_name), 'wb') as video_file:
                video_file.write(video_response.content)

        except Exception as e:
            logger.error(f'download {url} fail, {e}')

def get_play_url(url: str)-> str:
    response = requests.get(url, allow_redirects=False, headers=headers)
    redirect_url:str = ""
    if 300 <= response.status_code < 400:
        redirect_url = response.headers['Location']

    if redirect_url == "":
        raise Exception(f"获取播放地址失败，状态码：{response.status_code}")

    u = urlparse(redirect_url)
    parts = u.path.split("/")
    if len(parts) < 5 or parts[1] != "live.kuaishou.com" or parts[2] != 'u':
        raise Exception(f"不支持该地址, {redirect_url}")

    principal_id, photo_id = parts[3:]
    if photo_id =="" or principal_id =="":
        raise Exception(f"播放地址缺少必要参数, {redirect_url}")
   
    url = f'https://live.kuaishou.com/live_api/profile/feedbyid?photoId={photo_id}&principalId={principal_id}'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"获取视频地址失败，状态码：{response.status_code}")
    r = response.json()
    
    play_url = r.get("data", {}).get("currentWork", {}).get("playUrl", "")
    if play_url == "":
        raise Exception(f"视频地址获取失败, {r}")

    return play_url

if __name__ == "__main__":
    typer.run(main)
