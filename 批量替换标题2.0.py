import os
import re

# ==================== 用户配置区域 ====================
source_dir = r"C:\Users\31100\Desktop\新建文件夹 (2)"  # 原视频的总目录（对应图中的 新建文件夹(2) ）
target_dir = r"C:\Users\31100\Desktop\新建文件夹 (3)"  # 剪辑视频的独立文件夹（对应图中的 新建文件夹(3) ）
file_extension = ".mp4"  # 视频扩展名
# --- 关键新配置：需要排除的源文件夹内的子文件夹路径 ---
folder_to_exclude = os.path.join(source_dir, "剪辑后")  # 请修改“剪辑后”为你的子文件夹名


# =====================================================

def extract_leading_number(filename):
    """从原始文件名开头提取数字用于排序（例如从 '1.标题.mp4' 提取 1）"""
    match = re.match(r'^(\d+)', filename)
    return int(match.group(1)) if match else 99999


def get_filtered_source_files(src_dir, exclude_folder):
    """获取源文件夹中需要参与配对的文件列表，自动排除指定的子文件夹。"""
    valid_files = []
    for item in os.listdir(src_dir):
        item_path = os.path.join(src_dir, item)
        if os.path.normpath(item_path) == os.path.normpath(exclude_folder):
            print(f"信息：已排除子文件夹 '{exclude_folder}'")
            continue
        if not os.path.isfile(item_path):
            continue
        if item.endswith(file_extension):
            valid_files.append(item)
    return sorted(valid_files, key=extract_leading_number)


def get_filtered_target_files(tgt_dir):
    """获取目标文件夹中需要参与配对的文件列表。"""
    valid_files = []
    for item in os.listdir(tgt_dir):
        item_path = os.path.join(tgt_dir, item)
        if not os.path.isfile(item_path):
            continue
        if item.endswith(file_extension):
            valid_files.append(item)

    # 【修复重点】：先去掉扩展名，再提取数字，避免把 .mp4 里的 4 当作排序依据
    def extract_target_number(filename):
        name_without_ext = os.path.splitext(filename)[0]  # 去掉 .mp4
        nums = re.findall(r'\d+', name_without_ext)  # 找剩下的数字
        return int(nums[-1]) if nums else 99999  # 提取最后一个数字

    return sorted(valid_files, key=extract_target_number)


def main():
    print("=== 批量应用标题脚本（智能排除干扰版） ===\n")
    print(f"源文件夹（原视频）: {source_dir}")
    print(f"目标文件夹（剪辑视频）: {target_dir}")
    print(f"排除的源子文件夹: {folder_to_exclude}\n")

    try:
        source_files_sorted = get_filtered_source_files(source_dir, folder_to_exclude)
        target_files_sorted = get_filtered_target_files(target_dir)
    except Exception as e:
        print(f"错误：读取文件夹时发生异常。\n{e}")
        return

    print(f"找到 {len(source_files_sorted)} 个源文件（已排除干扰）。")
    print(f"找到 {len(target_files_sorted)} 个目标文件。\n")

    if len(source_files_sorted) != len(target_files_sorted):
        print(f"错误：核心文件数量仍然不一致！无法安全配对。")
        print("\n源文件列表:")
        for idx, f in enumerate(source_files_sorted[:10]):
            print(f"  [{idx + 1}] {f}")
        print("\n目标文件列表:")
        for idx, f in enumerate(target_files_sorted[:10]):
            print(f"  [{idx + 1}] {f}")
        print("\n请清理不一致的文件后再运行脚本。")
        return

    pair_count = len(source_files_sorted)
    print("【重命名预览】")
    print("-" * 80)
    for i in range(pair_count):
        src = source_files_sorted[i]
        tgt = target_files_sorted[i]
        new_name = src
        print(f"配对 {i + 1:03d}: {tgt:35} -> {new_name}")

    print("\n" + "!" * 60)
    confirm = input("请仔细核对以上配对。\n确认无误后输入 'YES' 开始重命名 (输入其他内容取消): ")
    if confirm.upper() != 'YES':
        print("操作已取消。")
        return

    print("\n【开始重命名】")
    success_count = 0
    for i in range(pair_count):
        try:
            src = source_files_sorted[i]
            tgt = target_files_sorted[i]
            new_name = src
            old_path = os.path.join(target_dir, tgt)
            new_path = os.path.join(target_dir, new_name)
            os.rename(old_path, new_path)
            print(f"成功: {tgt:35} -> {new_name}")
            success_count += 1
        except Exception as e:
            print(f"错误处理 {tgt}: {e}")

    print("\n" + "=" * 80)
    print(f"操作完成！成功重命名 {success_count} 个文件。")


if __name__ == "__main__":
    main()
