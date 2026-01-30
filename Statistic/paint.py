import os
import matplotlib.pyplot as plt
import numpy as np

# ================= 配置区 =================
BASE_DIR = 'Twin'            # 根目录
DISPLAY_MAX = 10              # X轴最大显示到多少次
# ==========================================

def plot_comparative_saturation():
    # 1. 获取子文件夹（Labels）
    if not os.path.exists(BASE_DIR):
        print(f"【错误】: 找不到目录 '{BASE_DIR}'")
        return
    
    labels = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    if len(labels) == 0:
        print(f"【错误】: '{BASE_DIR}' 文件夹中没有子文件夹。")
        return

    # 准备绘图数据
    plt.rcParams['font.sans-serif'] = ['Arial']
    plt.rcParams['axes.unicode_minus'] = False
    fig, ax = plt.subplots(figsize=(8, 7), dpi=120) # 维持正方形比例，增加坡度感
    
    colors = ['#1F618D', '#C0392B', '#27AE60', '#8E44AD'] # 预设对比色
    all_y_values = [] # 用于最后计算全局Y轴缩放

    # 2. 遍历每个文件夹进行绘图
    for idx, label_name in enumerate(labels):
        label_path = os.path.join(BASE_DIR, label_name)
        token_dir = os.path.join(label_path, 'token')
        counter_dir = os.path.join(label_path, 'counter')

        # 计算分母 (Token 数量)
        if not os.path.exists(token_dir):
            print(f"【跳过】: {label_name} 缺少 token 文件夹")
            continue
        total_samples = len([f for f in os.listdir(token_dir) if os.path.isfile(os.path.join(token_dir, f))])
        
        if total_samples == 0:
            print(f"【跳过】: {label_name} 的 token 数量为 0")
            continue

        # 读取分子数据 (Counter 数据)
        success_results = []
        if os.path.exists(counter_dir):
            for filename in os.listdir(counter_dir):
                file_path = os.path.join(counter_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        val = f.read().strip()
                        if val: success_results.append(int(val))
                except: continue

        # 计算累积准确率
        x_values = np.arange(1, DISPLAY_MAX + 1)
        y_values = []
        for i in x_values:
            count = sum(1 for val in success_results if val <= i)
            y_values.append((count / total_samples) * 100)
        
        all_y_values.extend(y_values) # 收集所有点用于缩放

        # 3. 绘制折线
        color = colors[idx % len(colors)]
        ax.plot(x_values, y_values, color=color, linewidth=3, marker='o', 
                markersize=6, mfc='white', mew=2, label=f'Label: {label_name}', zorder=3)
        
        # 填充
        ax.fill_between(x_values, y_values, color=color, alpha=0.05, zorder=2)

        # 标注各组的饱和点 (最高点)
        max_y = max(y_values)
        max_x = x_values[y_values.index(max_y)]
        ax.scatter(max_x, max_y, s=100, facecolors='none', edgecolors=color, linewidths=2, zorder=5)

    # 4. 【核心视觉优化】：强制缩放 Y 轴
    if all_y_values:
        y_min, y_max = min(all_y_values), max(all_y_values)
        # 极窄间距：上下仅留 0.3% 的间隙，强制拉伸曲线
        ax.set_ylim(y_min - 0.3, y_max + 0.3)
    
    # 5. 细节美化
    ax.yaxis.grid(True, linestyle='--', alpha=0.3, zorder=0)
    ax.set_title('Comparative Performance Saturation', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Number of Attempts', fontsize=12)
    ax.set_ylabel('Cumulative Accuracy (%)', fontsize=12)
    ax.set_xlim(0.8, DISPLAY_MAX + 0.2)
    ax.set_xticks(x_values)
    
    ax.legend(loc='best', frameon=True, shadow=True)

    # 移除冗余边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig('twin_comparison_result.png')
    print("【成功】: 对比图表已生成为 'twin_comparison_result.png'")
    plt.show()

if __name__ == "__main__":
    plot_comparative_saturation()