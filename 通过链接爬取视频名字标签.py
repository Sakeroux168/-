import requests
import re
import time

def get_bvid(url):
    """从链接中提取真正的 BV 号，支持短链接解析"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 如果是手机端 b23.tv 短链接，先请求获取真实长链接
    if "b23.tv" in url:
        try:
            res = requests.get(url, headers=headers, allow_redirects=False)
            url = res.headers.get('Location', url)
        except:
            pass
            
    # 用正则抓取 BV 号
    match = re.search(r'(BV[a-zA-Z0-9]{10})', url)
    return match.group(1) if match else None

def fetch_video_info(bvid):
    """调用 B站官方 API 获取标题和标签"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 1. 获取视频标题
    info_api = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    title = "未知标题"
    try:
        info_res = requests.get(info_api, headers=headers).json()
        if info_res.get('code') == 0:
            title = info_res['data']['title']
    except:
        pass

    # 2. 获取视频标签
    tag_api = f"https://api.bilibili.com/x/tag/archive/tags?bvid={bvid}"
    formatted_tags = ""
    try:
        tag_res = requests.get(tag_api, headers=headers).json()
        if tag_res.get('code') == 0:
            # 提取所有标签名，并在前面加上 '#'，用空格隔开
            tags_list = [f"#{tag['tag_name']}" for tag in tag_res['data']]
            formatted_tags = " ".join(tags_list)
    except:
        pass
        
    return title, formatted_tags

if __name__ == "__main__":
    input_file = "bilibili_links.txt"
    output_file = "批量标签结果.txt"
    
    import os
    if not os.path.exists(input_file):
        print(f"❌ 找不到 {input_file}，请先创建这个文件并放入B站链接！")
    else:
        print("🚀 开始批量提取 B站标签...")
        with open(input_file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
            
        with open(output_file, "w", encoding="utf-8") as out_f:
            out_f.write("📊 B站视频标签批量提取结果\n")
            out_f.write("===========================================\n\n")
            
            for url in urls:
                bvid = get_bvid(url)
                if not bvid:
                    print(f"⚠️ 无法识别此链接的BV号: {url}")
                    continue
                    
                print(f"正在抓取: {bvid} ...")
                title, tags = fetch_video_info(bvid)
                
                # 写入文件
                out_f.write(f"▶️ 视频标题: {title}\n")
                out_f.write(f"🔗 视频链接: {url}\n")
                out_f.write(f"🏷️ 复制标签: {tags}\n")
                out_f.write("-" * 40 + "\n\n")
                
                # 礼貌延时，防止被B站封IP
                time.sleep(1)
                
        print(f"\n🎉 提取完毕！所有标签已完美排版，保存在 '{output_file}' 中。")
