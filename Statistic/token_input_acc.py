import os
import matplotlib.pyplot as plt
import numpy as np

# ================= 配置区 =================
BASE_DIR = 'Twin'            # 根目录，内含多个 Label 文件夹
DISPLAY_MAX = 10             # X轴最大尝试次数 (Retry 1-10)
# ==========================================

def parse_token_file(file_path):
    """
    核心修改：只解析 prompt_tokens (用户输入成本)
    基于你提供的 key=value 格式
    """
    prompt_val = 0
    if not os.path.exists(file_path):
        return 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                # 仅匹配 prompt_tokens 这一行
                if 'prompt_tokens=' in line:
                    prompt_val = int(line.split('=')[-1])
                    break # 找到即返回，忽略 total 和 reasoning
    except Exception:
        pass
    return prompt_val

def plot_multi_label_token_efficiency():
    if not os.path.exists(BASE_DIR):
        print(f"【错误】: 找不到目录 '{BASE_DIR}'")
        return
    
    # 自动获取所有子文件夹作为 Label
    labels = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))])
    
    if not labels:
        print(f"【错误】: '{BASE_DIR}' 文件夹中没有发现任何 Label 子目录。")
        return

    # 绘图初始化
    plt.rcParams['font.sans-serif'] = ['Arial']
    plt.rcParams['axes.unicode_minus'] = False
    fig, ax = plt.subplots(figsize=(9, 8), dpi=120)
    
    cmap = plt.get_cmap('tab10') 
    all_y_vals = []
    
    print(f"正在分析 {len(labels)} 个标签，仅统计 Input Tokens...")

    for idx, label_name in enumerate(labels):
        label_path = os.path.join(BASE_DIR, label_name)
        token_dir = os.path.join(label_path, 'token')
        counter_dir = os.path.join(label_path, 'counter')

        if not os.path.exists(token_dir) or not os.path.exists(counter_dir):
            continue

        # 1. 统计分母 (文件总数)
        token_files = [f for f in os.listdir(token_dir) if os.path.isfile(os.path.join(token_dir, f))]
        num_samples = len(token_files)
        if num_samples == 0: continue

        # 2. 计算平均单次尝试的 Input Token 消耗
        # 修改：这里求和的是 prompt_tokens
        total_input_tokens = sum(parse_token_file(os.path.join(token_dir, f)) for f in token_files)
        avg_input_token = total_input_tokens / num_samples
        input_token_per_step = avg_input_token / DISPLAY_MAX

        # 3. 读取成功记录 (Counter)
        success_results = []
        for f in os.listdir(counter_dir):
            try:
                with open(os.path.join(counter_dir, f), 'r') as cf:
                    val = cf.read().strip()
                    if val: success_results.append(int(val))
            except: continue

        # 4. 计算趋势数据点
        x_avg_input_tokens = [] # X轴：平均累积 Input Token
        y_accuracies = []       # Y轴：累积准确率
        
        for i in range(1, DISPLAY_MAX + 1):
            acc = (sum(1 for val in success_results if val <= i) / num_samples) * 100
            y_accuracies.append(acc)
            x_avg_input_tokens.append(input_token_per_step * i)

        all_y_vals.extend(y_accuracies)

        # 5. 绘图
        current_color = cmap(idx % 10)
        ax.plot(x_avg_input_tokens, y_accuracies, label=f'{label_name}', 
                color=current_color, linewidth=2.5, marker='o', markersize=5, 
                mfc='white', mew=1.5, alpha=0.9)
        
        # 标注终点数值
        ax.text(x_avg_input_tokens[-1], y_accuracies[-1], f' {y_accuracies[-1]:.1f}%', 
                color=current_color, fontsize=9, fontweight='bold', va='center')

    # 6. 强制 Y 轴拉伸
    if all_y_vals:
        ymin, ymax = min(all_y_vals), max(all_y_vals)
        ax.set_ylim(ymin - 0.5, ymax + 0.5)

    # 7. 美化与标签修正
    ax.set_title('Input Efficiency Analysis: User Tokens vs. Accuracy', fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('Average Cumulative Input (Prompt) Tokens per Sample', fontsize=12, labelpad=10)
    ax.set_ylabel('Cumulative Accuracy (%)', fontsize=12, labelpad=10)
    
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    ax.xaxis.grid(True, linestyle=':', alpha=0.2)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), title="Models", frameon=True, shadow=True)

    plt.tight_layout()
    plt.savefig('input_efficiency_analysis.png', bbox_inches='tight')
    print("【完成】: 图表已保存为 'input_efficiency_analysis.png'，本次仅统计 Input Token。")
    plt.show()

if __name__ == "__main__":
    plot_multi_label_token_efficiency()