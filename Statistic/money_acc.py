import os
import matplotlib.pyplot as plt
import numpy as np
import re

# ================= 配置区 =================
BASE_DIR = 'Twin'            # 根目录
DISPLAY_MAX = 10              # X轴最大尝试次数
SAVE_NAME = 'money_acc_comparison.png'

# 价格配置 (每百万 Token 的美元单价)
PRICING = {
    'Deepseek': {'input': 0.25, 'output': 0.38},
    'GPT5.2':   {'input': 1.75, 'output': 14.0},
    'Gemini':   {'input': 0.50, 'output': 3.0},
    'Gemini3':  {'input': 0.50, 'output': 3.0}
}
# ==========================================

def parse_token_file_for_money(file_path, model_name):
    """解析单个文件中的 token 使用量并转换为美元成本"""
    input_tokens = 0
    total_tokens = 0
    if not os.path.exists(file_path): return 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 匹配 input/prompt tokens
            in_match = re.search(r'(?:prompt_tokens|input_tokens)=(\d+)', content)
            if in_match: input_tokens = int(in_match.group(1))
            
            # 匹配 total tokens
            total_match = re.search(r'total_tokens=(\d+)', content)
            if total_match: total_tokens = int(total_match.group(1))
            
        # 计算输出 token
        output_tokens = max(0, total_tokens - input_tokens)
        
        # 获取对应定价
        price = PRICING.get(model_name, {'input': 0, 'output': 0})
        
        # 计算成本: (输入/1M * 输入价) + (输出/1M * 输出价)
        cost = (input_tokens / 1_000_000 * price['input']) + (output_tokens / 1_000_000 * price['output'])
        return cost
    except:
        return 0

def plot_complete_comparison():
    # 1. 论文风格全局设置
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    plt.rcParams['axes.linewidth'] = 1.2
    
    if not os.path.exists(BASE_DIR):
        print(f"错误：找不到目录 {BASE_DIR}")
        return

    # 获取所有子文件夹
    labels = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))])
    
    # 定义模型颜色映射
    model_colors = {
        'Deepseek': '#1f77b4', # 蓝色
        'GPT5.2': '#ff7f0e',   # 橙色
        'Gemini': '#2ca02c',    # 绿色
        'Gemini3': '#2ca02c'
    }
    
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    all_y_vals = []

    # 准备文本输出
    print("\n" + "="*70)
    print(f"{'Method(Model)':<25} | {'Step':<4} | {'Cost (USD)':<12} | {'Acc (Y)%':<8}")
    print("-" * 70)

    for label_name in labels:
        label_path = os.path.join(BASE_DIR, label_name)
        token_dir = os.path.join(label_path, 'token')
        counter_dir = os.path.join(label_path, 'counter')

        if not os.path.exists(token_dir) or not os.path.exists(counter_dir):
            continue

        # 判定当前模型以获取定价
        current_model = "Unknown"
        for m_name in PRICING.keys():
            if m_name in label_name:
                current_model = m_name
                break

        # --- 核心逻辑：计算 Cost 数据点 ---
        token_files = [f for f in os.listdir(token_dir) if os.path.isfile(os.path.join(token_dir, f))]
        num_samples = len(token_files)
        if num_samples == 0: continue

        # 计算该目录下所有样本的总成本均值
        total_cost_sum = sum(parse_token_file_for_money(os.path.join(token_dir, f), current_model) for f in token_files)
        avg_total_cost = total_cost_sum / num_samples
        
        # 模拟每步累积成本 (假设成本随步骤线性增长)
        cost_per_step = avg_total_cost / DISPLAY_MAX

        success_results = []
        for f in os.listdir(counter_dir):
            try:
                with open(os.path.join(counter_dir, f), 'r') as cf:
                    val = cf.read().strip()
                    if val: success_results.append(int(val))
            except: continue

        # X轴为累积美元成本，Y轴为准确率
        x_points = [cost_per_step * i for i in range(1, DISPLAY_MAX + 1)]
        y_points = [(sum(1 for val in success_results if val <= i) / num_samples) * 100 
                    for i in range(1, DISPLAY_MAX + 1)]
        all_y_vals.extend(y_points)

        color = model_colors.get(current_model, '#7f7f7f')
        is_ours = "Ours" in label_name

        # --- 打印坐标 ---
        for i in range(len(x_points)):
            print(f"{label_name:<25} | {i+1:<4} | {x_points[i]:<12.6f} | {y_points[i]:<8.2f}")

        # --- 绘图效果定制 ---
        if is_ours:
            ax.plot(x_points, y_points, label=label_name, color=color,
                    linewidth=2.5, linestyle='-', marker='o', markersize=6, zorder=10)
            ax.annotate(f'{y_points[-1]:.1f}%', xy=(x_points[-1], y_points[-1]),
                        xytext=(5, 5), textcoords='offset points', fontsize=9, 
                        fontweight='bold', color=color)
        else:
            ax.plot(x_points, y_points, label=label_name, color=color,
                    linewidth=1.5, linestyle='--', marker='s', markersize=5, 
                    mfc='white', alpha=0.8, zorder=5)
            ax.annotate(f'{y_points[-1]:.1f}%', xy=(x_points[-1], y_points[-1]),
                        xytext=(5, -12), textcoords='offset points', fontsize=9, 
                        color=color)

    # 轴缩放
    if all_y_vals:
        ymin, ymax = min(all_y_vals), max(all_y_vals)
        ax.set_ylim(ymin - 5, 105)

    # 图表细节美化
    ax.set_xlabel('Average Cumulative Cost per Sample (USD)', fontsize=12, labelpad=10)
    ax.set_ylabel('Cumulative Accuracy (%)', fontsize=12, labelpad=10)
    ax.grid(True, linestyle=':', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.legend(loc='lower right', frameon=True, edgecolor='none', fontsize=9)

    plt.tight_layout()
    plt.savefig(SAVE_NAME, bbox_inches='tight')
    print(f"\n[完成] 图像已保存至: {SAVE_NAME}")
    plt.show()

if __name__ == "__main__":
    plot_complete_comparison()