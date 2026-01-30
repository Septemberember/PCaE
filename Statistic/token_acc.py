import os
import matplotlib.pyplot as plt
import numpy as np

# ================= 配置区 =================
BASE_DIR = 'Twin'            # 根目录
DISPLAY_MAX = 10              # X轴最大尝试次数
SAVE_NAME = 'comparison_paper_style.png'
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

    # 获取所有子文件夹
    labels = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))])
    
    # 定义模型颜色映射
    model_colors = {
        'Deepseek': '#1f77b4', # 蓝色
        'GPT5.2': '#ff7f0e',   # 橙色
        'Gemini': '#2ca02c',    # 绿色
        'Gemini3': '#2ca02c'
    }
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    all_y_vals = []

    # 准备文本输出
    print("\n" + "="*60)
    print(f"{'Method(Model)':<25} | {'Step':<4} | {'Tokens (X)':<10} | {'Acc (Y)%':<8}")
    print("-" * 60)

    for label_name in labels:
        label_path = os.path.join(BASE_DIR, label_name)
        token_dir = os.path.join(label_path, 'token')
        counter_dir = os.path.join(label_path, 'counter')

        if not os.path.exists(token_dir) or not os.path.exists(counter_dir):
            continue

        # --- 核心逻辑：计算数据点 ---
        token_files = [f for f in os.listdir(token_dir) if os.path.isfile(os.path.join(token_dir, f))]
        num_samples = len(token_files)
        if num_samples == 0: continue

        total_tokens_sum = sum(parse_token_file(os.path.join(token_dir, f)) for f in token_files)
        avg_total_token = total_tokens_sum / num_samples
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

        # --- 分类逻辑：判定方法和模型 ---
        is_ours = "Ours" in label_name
        # 提取模型名称 (Deepseek, GPT, Gemini)
        current_model = "Unknown"
        for m_name in model_colors.keys():
            if m_name in label_name:
                current_model = m_name
                break
        
        color = model_colors.get(current_model, '#7f7f7f')

        # --- 打印坐标 ---
        for i in range(len(x_points)):
            print(f"{label_name:<25} | {i+1:<4} | {x_points[i]:<10.1f} | {y_points[i]:<8.2f}")

        # --- 绘图效果定制 ---
        if is_ours:
            ax.plot(x_points, y_points, label=label_name, color=color,
                    linewidth=2.5, linestyle='-', marker='o', markersize=6, zorder=10)
            # 终点标注 - 向上偏移
            ax.annotate(f'{y_points[-1]:.1f}%', xy=(x_points[-1], y_points[-1]),
                        xytext=(5, 5), textcoords='offset points', fontsize=9, 
                        fontweight='bold', color=color)
        else:
            ax.plot(x_points, y_points, label=label_name, color=color,
                    linewidth=1.5, linestyle='--', marker='s', markersize=5, 
                    mfc='white', alpha=0.8, zorder=5)
            # 终点标注 - 向下偏移避免重叠
            ax.annotate(f'{y_points[-1]:.1f}%', xy=(x_points[-1], y_points[-1]),
                        xytext=(5, -12), textcoords='offset points', fontsize=9, 
                        color=color)

    # 轴缩放：聚焦数据差异
    if all_y_vals:
        ymin, ymax = min(all_y_vals), max(all_y_vals)
        ax.set_ylim(ymin - 5, ymax + 10)

    # 图表细节美化
    ax.set_xlabel('Average Cumulative Tokens per Sample', fontsize=12, labelpad=10)
    ax.set_ylabel('Cumulative Accuracy (%)', fontsize=12, labelpad=10)
    ax.grid(True, linestyle=':', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 图例：放在右下角，白底半透明
    ax.legend(loc='lower right', frameon=True, edgecolor='none', fontsize=9)

    plt.tight_layout()
    plt.savefig(SAVE_NAME, bbox_inches='tight')
    print(f"\n[完成] 图像已保存至: {SAVE_NAME}")
    plt.show()

if __name__ == "__main__":
    plot_complete_comparison()