import os
import re
import difflib

def load_tags_data(txt_file):
    data = {}
    if not os.path.exists(txt_file):
        print(f"❌ 找不到标签文件：{txt_file}")
        print("请确保【批量标签结果.txt】和本脚本在同一个文件夹内！")
        return data
        
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_title = ""
    for line in lines:
        if line.startswith("▶️ 视频标题:"):
            current_title = line.replace("▶️ 视频标题:", "").strip()
        elif line.startswith("🏷️ 复制标签:") and current_title:
            # 去掉空格和换行符
            tags = line.replace("🏷️ 复制标签:", "").strip().replace(" ", "")
            data[current_title] = tags
            current_title = ""
            
    return data

def sanitize_for_match(title):
    """用于匹配时，过滤特殊字符"""
    return re.sub(r'[\\/:*?"<>|]', '', title)

def sanitize_for_filename(text):
    """用于生成文件名时，将 Windows 不允许的特殊字符替换为下划线"""
    # 把 \ / : * ? " < > | 替换成下划线 _
    return re.sub(r'[\\/:*?"<>|]', '_', text)

def main():
    print("🤖 启动 AI 视频标签跨区匹配系统 (自动过滤非法字符版)")
    print("="*60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    txt_file = os.path.join(script_dir, "批量标签结果.txt")
    
    title_tag_map = load_tags_data(txt_file)
    if not title_tag_map:
        input("\n按回车键退出...")
        return
        
    print(f"📄 成功读取了 {len(title_tag_map)} 个视频的标签数据。")
    
    target_dir = input("\n📁 请粘贴视频所在的真实文件夹路径并回车：\n").strip()
    target_dir = target_dir.strip('"').strip("'")
    
    if not os.path.exists(target_dir):
        print(f"\n❌ 找不到你输入的文件夹：{target_dir}")
        input("按回车键退出...")
        return
        
    videos = [f for f in os.listdir(target_dir) if f.lower().endswith(('.mp4', '.mov', '.mkv', '.avi', '.flv'))]
    
    planned_renames = []
    unmatched_files = []
    skipped_files = []

    for filename in videos:
        if '#' in filename:
            skipped_files.append(filename)
            continue

        base_name, ext = os.path.splitext(filename)
        best_tags = None
        best_ratio = 0.0
        
        for title, tags in title_tag_map.items():
            clean_title = sanitize_for_match(title)
            if base_name in clean_title or clean_title in base_name:
                best_tags = tags
                break
                
            ratio = difflib.SequenceMatcher(None, base_name, clean_title).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                if ratio > 0.4:
                    best_tags = tags

        if best_tags:
            # 💡 关键修复点：将标签里 Windows 不允许的 / 和 : 等符号清洗掉
            safe_tags = sanitize_for_filename(best_tags)
            
            new_name = f"{base_name}{safe_tags}{ext}"
            old_path = os.path.join(target_dir, filename)
            new_path = os.path.join(target_dir, new_name)
            planned_renames.append((old_path, new_path, filename, new_name))
        else:
            unmatched_files.append(filename)

    # ================= 预览环节 =================
    print("\n" + "="*60)
    print("🔍 【重命名操作预览】 请仔细核对匹配是否正确：\n")
    
    if planned_renames:
        for old_path, new_path, f_old, f_new in planned_renames:
            print(f" 🎬 {f_old}\n    -------> {f_new}\n")
    else:
        print(" （没有找到需要打标签的视频）")

    if unmatched_files:
        print("\n⚠️ 以下视频【未能匹配】到标签，将保持原样：")
        for f in unmatched_files:
            print(f"  - {f}")
            
    if skipped_files:
        print(f"\n⏩ 另有 {len(skipped_files)} 个视频因名字中已有 '#' 被跳过。")
    print("="*60)

    # ================= 确认环节 =================
    if not planned_renames:
        print("\n由于没有可执行的改名操作，程序结束。")
        input("按回车键退出...")
        return

    confirm = input(f"\n❓ 确认要对以上 {len(planned_renames)} 个视频执行改名操作吗？\n(输入 yes 确认执行，直接回车取消)：").strip().lower()

    if confirm == 'yes':
        success_count = 0
        print("\n🚀 开始执行贴标签操作...")
        for old_path, new_path, f_old, f_new in planned_renames:
            try:
                os.rename(old_path, new_path)
                success_count += 1
            except Exception as e:
                print(f"❌ 失败: {f_old} (原因: {e})")
        print(f"\n🎉 全部搞定！共成功为 {success_count} 个视频贴上了标签。")
    else:
        print("\n🛑 已取消操作，文件未做任何修改，安全退出。")

    input("\n按回车键关闭窗口...")

if __name__ == "__main__":
    main()
