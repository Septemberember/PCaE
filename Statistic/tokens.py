import os
import re

# ================= 配置区 =================
TOKEN_DIR = 'token'  # 存放 token 记录文件的文件夹
# ==========================================

def calculate_token_stats():
    total_prompt_sum = 0
    total_output_sum = 0
    file_count = 0

    if not os.path.exists(TOKEN_DIR):
        print(f"错误: 找不到目录 '{TOKEN_DIR}'")
        return

    # 遍历文件夹
    for filename in os.listdir(TOKEN_DIR):
        file_path = os.path.join(TOKEN_DIR, filename)
        
        if os.path.isfile(file_path):
            file_count += 1
            current_total = 0
            current_prompt = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # 使用正则匹配 key=value 格式
                    line = line.strip()
                    if not line:
                        continue
                        
                    if 'total_tokens=' in line:
                        val = line.split('=')[-1]
                        current_total += int(val)
                    elif 'prompt_tokens=' in line:
                        val = line.split('=')[-1]
                        current_prompt += int(val)
            
            # 累加到全局
            total_prompt_sum += current_prompt
            # Output = Total - Prompt
            total_output_sum += (current_total - current_prompt)

    # 打印结果
    print("=" * 30)
    print(f"统计报告")
    print("-" * 30)
    print(f"读取文件总数: {file_count}")
    print(f"总 Prompt Tokens: {total_prompt_sum:,}")
    print(f"总 Output Tokens: {total_output_sum:,}")
    print(f"总 Total  Tokens: {total_prompt_sum + total_output_sum:,}")
    print("=" * 30)

if __name__ == "__main__":
    calculate_token_stats()