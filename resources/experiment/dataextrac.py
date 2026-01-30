import os
import re

def parse_all_metrics():
    # 1. 用户设定根目录
    root_path = input("请输入数据文件夹的根路径: ").strip()
    if not os.path.exists(root_path):
        print("路径不存在。")
        return

    # 定义显示顺序与对应的真实总数 (用于内部计算，不输出)
    order_config = [
        ("Sequential3", 63),
        ("Branched3", 151),
        ("Single-path-Loop3", 21),
        ("Multi-path-Loop3", 31),
        ("Nested-Loop3", 35)
    ]
    
    categories = [item[0] for item in order_config]
    true_totals = {item[0]: item[1] for item in order_config}
    true_totals["Overall"] = 301

    # 数据容器
    results = {cat: {"success_total": 0, "retry_list": [], "retry_1_success": 0} for cat in categories}

    # 2. 读取各分类 summary.txt 获取总成功数
    for cat in categories:
        summary_path = os.path.join(root_path, cat, "summary.txt")
        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r"success number:\s*(\d+)", content)
                if match:
                    results[cat]["success_total"] = int(match.group(1))

    # 3. 跨目录匹配 Counter 逻辑
    base_counter_dir = os.path.join(root_path, "Multi-path-Loop3", "counter")
    all_retries_combined = [] 

    if os.path.exists(base_counter_dir):
        for filename in os.listdir(base_counter_dir):
            if filename.endswith(".java"):
                try:
                    with open(os.path.join(base_counter_dir, filename), 'r') as f:
                        retry_val = int(f.read().strip())
                except:
                    continue

                for cat in categories:
                    # 检查文件物理归属
                    is_in_cat = any(os.path.exists(os.path.join(root_path, cat, d, filename)) 
                                   for d in ["succDataset", "failedDataset", "exceptionDataset"])
                    
                    if is_in_cat:
                        results[cat]["retry_list"].append(retry_val)
                        all_retries_combined.append(retry_val)
                        
                        # 统计维度：Retry=1 且成功的
                        if retry_val == 1:
                            if os.path.exists(os.path.join(root_path, cat, "succDataset", filename)):
                                results[cat]["retry_1_success"] += 1
                        break

    # 4. 打印最终报表 (移除 True Total 列)
    print("\n" + "="*95)
    header = f"{'Category':<20} | {'Success':<8} | {'Real Acc':<12} | {'Avg Retry':<12} | {'R1-Succ':<10} | {'R1-Acc'}"
    print(header)
    print("-" * 95)

    total_success = 0
    total_r1_success = 0

    for cat in categories:
        d = results[cat]
        gt = true_totals[cat]
        
        acc = (d["success_total"] / gt) * 100 if gt > 0 else 0
        avg_r = sum(d["retry_list"]) / len(d["retry_list"]) if d["retry_list"] else 0
        r1_acc = (d["retry_1_success"] / gt) * 100 if gt > 0 else 0
        
        total_success += d["success_total"]
        total_r1_success += d["retry_1_success"]

        print(f"{cat:<20} | {d['success_total']:<8} | {acc:>10.2f}% | {avg_r:>12.2f} | {d['retry_1_success']:<10} | {r1_acc:>7.2f}%")

    # 5. 计算并打印 Overall
    overall_gt = true_totals["Overall"]
    overall_acc = (total_success / overall_gt) * 100
    overall_r1_acc = (total_r1_success / overall_gt) * 100
    overall_avg_retry = sum(all_retries_combined) / len(all_retries_combined) if all_retries_combined else 0

    print("-" * 95)
    print(f"{'OVERALL':<20} | {total_success:<8} | {overall_acc:>10.2f}% | {overall_avg_retry:>12.2f} | {total_r1_success:<10} | {overall_r1_acc:>7.2f}%")
    print("=" * 95)

if __name__ == "__main__":
    parse_all_metrics()