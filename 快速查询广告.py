import os
import subprocess
from faster_whisper import WhisperModel

# 1. 初始化模型：开启 GPU (CUDA) 加速和 FP16 半精度（专为 RTX 2060 优化）
print("🚀 正在加载高精度 AI 语音识别模型 (启动 RTX 2060 GPU 加速)...")
try:
    model = WhisperModel("small", device="cuda", compute_type="float16")
    print("✅ GPU 加速开启成功！")
except Exception as e:
    print(f"⚠️ GPU 启动失败，错误信息: {e}")
    print("将自动降级为 CPU 模式运行...")
    model = WhisperModel("small", device="cpu", compute_type="int8")

# 2. 👑 全网最全视频广告/恰饭高频词库
ad_keywords = [
    # 【恰饭/赞助明示类】
    "恰饭", "赞助", "金主", "甲方", "品牌方", "商单", "感谢本期", "由...提供",
    "感谢...的大力支持", "感谢...对本期视频", "本期视频由", "商业推广", "特约赞助",

    # 【引导点击/位置指引类】
    "专属链接", "评论区置顶", "置顶评论", "右下角", "左下角", "购买链接", "链接放在",
    "视频下方", "简介区", "小黄车", "购物车", "橱窗", "点击下方", "扫码", "看底端",
    "绿泡泡", "卓威", "小程序"

    # 【优惠/福利/转化类】
    "优惠码", "专属福利", "粉丝福利", "体验装", "试用装", "报我的名字", "提我的名字",
    "专属暗号", "报暗号", "内部价", "优惠券", "立减", "百亿补贴", "下单", "薅羊毛",
    "限时优惠", "买一送", "活动价", "折扣",

    # 【高频带货口头禅】
    "种草", "强烈推荐", "亲测有效", "闭眼入", "宝藏好物", "实力安利", "无限回购",
    "真的很好用", "绝对不亏", "绝绝子", "神仙好物", "早买早享受",

    # 【常见电商平台】
    "拼多多", "淘宝", "京东", "天猫", "得物", "某宝", "某东", "某多多"
]


def extract_audio(video_path, audio_path):
    """调用本地 FFmpeg 极速提取适合语音识别的单声道音频"""
    cmd = [
        'ffmpeg', '-y', '-i', video_path, '-vn',
        '-acodec', 'libmp3lame', '-ac', '1', '-ar', '16000', '-b:a', '32k', audio_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def find_ads_in_video(video_path, report_file):
    print(f"\n===========================================")
    print(f"🎬 正在极速处理视频: {video_path}")
    audio_path = video_path + ".mp3"

    extract_audio(video_path, audio_path)
    print("🎵 音频提取完毕，正在使用 RTX 2060 扫描广告内容...")

    # beam_size=5 保证准确率，language="zh" 强制中文
    segments, info = model.transcribe(audio_path, beam_size=5, language="zh")

    found_ads = False
    with open(report_file, "a", encoding="utf-8") as f:
        f.write(f"\n===========================================\n")
        f.write(f"视频文件名: {video_path}\n")

        for segment in segments:
            # 检测是否命中词库中的任何一个词
            hit_keywords = [kw for kw in ad_keywords if kw in segment.text]
            if hit_keywords:
                start_m, start_s = divmod(int(segment.start), 60)
                time_str = f"{start_m:02d}:{start_s:02d}"
                # 打印并记录具体的命中时间和命中了哪些词
                log_msg = f"🚨 [疑似广告] 时间点 {time_str} | 命中词: {hit_keywords} | 原文: {segment.text}"

                print(log_msg)
                f.write(log_msg + "\n")
                found_ads = True

        if not found_ads:
            success_msg = "✅ 未发现明显的口播广告内容。"
            print(success_msg)
            f.write(success_msg + "\n")

    if os.path.exists(audio_path):
        os.remove(audio_path)


if __name__ == "__main__":
    video_extensions = ('.mp4', '.mov', '.mkv', '.avi', '.flv')  # 加了 B 站早期的 flv 格式
    videos = [f for f in os.listdir('.') if f.lower().endswith(video_extensions)]
    report_file = "广告排查报告.txt"

    if not videos:
        print("❌ 当前文件夹下没有找到视频文件。")
    else:
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("📊 视频广告自动排查报告 (RTX 2060 极速版)\n")

        for video_file in videos:
            find_ads_in_video(video_file, report_file)

        print(f"\n🎉 所有视频排查完毕！结果已保存到 '{report_file}'。")
