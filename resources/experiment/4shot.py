import os

def calculate_single_retry_success():
    # 1. 用户手动指定根目录
    root_path = input("请输入数据文件夹的根路径 (例如: ./data): ").strip()
    if not os.path.exists(root_path):
        print("路径不存在。")
        return

    # 2. 真实样本总数 (Ground Truth)
    true_totals = {
        "Sequential3": 63,
        "Branched3": 151,
        "Single-path-Loop3": 21,
        "Multi-path-Loop3": 31,
        "Nested-Loop3": 35,
        "Overall": 301
    }

    # 初始化统计字典
    # single_retry_success: 重试次数为1且出现在 succDataset 中的数量
    categories = ["Branched3", "Multi-path-Loop3", "Nested-Loop3", "Sequential3", "Single-path-Loop3"]
    stats = {cat: {"single_retry_success": 0} for cat in categories}

    # 3. 扫描最全的 counter 文件夹
    base_counter_dir = os.path.join(root_path, "Multi-path-Loop3", "counter")
    
    if not os.path.exists(base_counter_dir):
        print(f"错误: 找不到基准 counter 文件夹: {base_counter_dir}")
        return

    print("正在处理数据，请稍候...")

    for filename in os.listdir(base_counter_dir):
        if filename.endswith(".java"):
            file_path = os.path.join(base_counter_dir, filename)
            
            # 读取重试次数
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    retry_val = int(f.read().strip())
            except (ValueError, IOError):
                continue

            # 只有当 retry 次数为 1 时才进行后续判断
            if retry_val == 1:
                # 寻找这个文件归属于哪个类别的 succDataset
                for cat in categories:
                    # 关键判断：文件必须在对应类别的成功数据集里
                    succ_path = os.path.join(root_path, cat, "succDataset", filename)
                    
                    if os.path.exists(succ_path):
                        stats[cat]["single_retry_success"] += 1
                        break # 找到归属后跳出当前文件的类别匹配

    # 4. 打印统计报表
    print("\n" + "="*85)
    print(f"{'Category':<20} | {'Retry=1 Success':<15} | {'True Total':<10} | {'Single-Try Acc'}")
    print("-"*85)

    total_single_success = 0
    for cat in categories:
        single_success = stats[cat]["single_retry_success"]
        ground_truth = true_totals[cat]
        acc = (single_success / ground_truth) * 100
        total_single_success += single_success
        
        print(f"{cat:<20} | {single_success:<15} | {ground_truth:<10} | {acc:.2f}%")

    # 5. 计算 Overall
    overall_gt = true_totals["Overall"]
    overall_acc = (total_single_success / overall_gt) * 100
    print("-"*85)
    print(f"{'OVERALL':<20} | {total_single_success:<15} | {overall_gt:<10} | {overall_acc:.2f}%")
    print("="*85)

if __name__ == "__main__":
    calculate_single_retry_success()