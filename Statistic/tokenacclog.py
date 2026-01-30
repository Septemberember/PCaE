import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter  # 用于保持对数轴上的数字格式

# ================= 配置区 =================
BASE_DIR = 'Twin'            # 根目录
DISPLAY_MAX = 10              # X轴最大尝试次数
SAVE_NAME = 'comparison_log_style.png'
# ==========================================

def parse_token_file(file_path):
    """解析单个文件中的 token 使用量"""
    total = 0
    if not os.path.exists(file_path): return 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if 'total_tokens=' in line:
                    total = int(line.split('=')[-1])
                    break
    except: pass
    return total

def plot_complete_comparison():
    # 1. 论文风格全局设置
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    plt.rcParams['axes.linewidth'] = 1.2
    
    if not os.path.exists(BASE_DIR):
        print(f"错误：找不到目录 {BASE_DIR}")
        return

    labels = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))])
    
    model_colors = {
        'Deepseek': '#1f77b4', # 蓝色
        'GPT5.2': '#ff7f0e',   # 橙色
        'Gemini': '#2ca02c',    # 绿色
        'Gemini3': '#2ca02c'
    }
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    
    # --- 核心修改：设置 X 轴为对数坐标 ---
    ax.set_xscale('log') 
    
    all_y_vals = []
    all_x_vals = []

    print("\n" + "="*60)
    print(f"{'Method(Model)':<25} | {'Step':<4} | {'Tokens (Log X)':<12} | {'Acc (Y)%':<8}")
    print("-" * 60)

    for label_name in labels:
        label_path = os.path.join(BASE_DIR, label_name)
        token_dir = os.path.join(label_path, 'token')
        counter_dir = os.path.join(label_path, 'counter')

        if not os.path.exists(token_dir) or not os.path.exists(counter_dir):
            continue

        token_files = [f for f in os.listdir(token_dir) if os.path.isfile(os.path.join(token_dir, f))]
        num_samples = len(token_files)
        if num_samples == 0: continue

        total_tokens_sum = sum(parse_token_file(os.path.join(token_dir, f)) for f in token_files)
        avg_total_token = total_tokens_sum / num_samples
        
        # 为了让对数轴起点有意义，避开 0。这里假设 step 1 至少消耗 1/10 的总量
        token_per_step = avg_total_token / DISPLAY_MAX

        success_results = []
        for f in os.listdir(counter_dir):
            try:
                with open(os.path.join(counter_dir, f), 'r') as cf:
                    val = cf.read().strip()
                    if val: success_results.append(int(val))
            except: continue

        x_points = [token_per_step * i for i in range(1, DISPLAY_MAX + 1)]
        y_points = [(sum(1 for val in success_results if val <= i) / num_samples) * 100 
                    for i in range(1, DISPLAY_MAX + 1)]
        
        all_y_vals.extend(y_points)
        all_x_vals.extend(x_points)

        is_ours = "Ours" in label_name
        current_model = "Unknown"
        for m_name in model_colors.keys():
            if m_name in label_name:
                current_model = m_name
                break
        
        color = model_colors.get(current_model, '#7f7f7f')

        for i in range(len(x_points)):
            print(f"{label_name:<25} | {i+1:<4} | {x_points[i]:<12.1f} | {y_points[i]:<8.2f}")

        # 绘图定制
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

    # 轴格式美化
    if all_y_vals:
        ax.set_ylim(min(all_y_vals) - 5, max(all_y_vals) + 10)
    
    # 强制让 X 轴刻度显示正常数字（如 100, 1000）而不是科学计数法（10^2, 10^3）
    ax.xaxis.set_major_formatter(ScalarFormatter())
    
    ax.set_xlabel('Average Cumulative Tokens per Sample (Log Scale)', fontsize=12, labelpad=10)
    ax.set_ylabel('Cumulative Accuracy (%)', fontsize=12, labelpad=10)
    
    # 对数坐标下，使用 minor grid（次网格）会更美观
    ax.grid(True, which="both", linestyle=':', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.legend(loc='lower right', frameon=True, edgecolor='none', fontsize=9)

    plt.tight_layout()
    plt.savefig(SAVE_NAME, bbox_inches='tight')
    print(f"\n[完成] 对数轴图像已保存至: {SAVE_NAME}")
    plt.show()

if __name__ == "__main__":
    plot_complete_comparison()