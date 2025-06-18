import os
import pandas as pd

def clean_file(input_filepath, output_filepath):
    """
    从指定路径读取文件，对于特定字段后仅保留一个制表符，删除多余制表符，并保存结果。
    
    :param input_filepath: str, 输入文件的路径
    :param output_filepath: str, 输出文件的路径
    """
    keywords = [
        '行政处罚决定书文号', '被处罚当事人', '主要违法违规事实',
        '行政处罚依据', '行政处罚决定', '作出处罚决定的机关名称',
        '作出处罚决定的日期'
    ]
    
    with open(input_filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    cleaned_lines = []
    for line in lines:
        parts = line.split('\t')
        new_line_parts = []
        for part in parts:
            if any(keyword in part for keyword in keywords):
                # 保留关键字及其后的第一个制表符
                new_line_parts.append(part + '\t')
            else:
                # 对于非关键字部分，直接添加而不加制表符
                new_line_parts.append(part)
        # 将处理过的部分重新组合成行
        cleaned_line = ''.join(new_line_parts).strip() + '\n'  # 去除末尾可能多出的空白字符
        cleaned_lines.append(cleaned_line)
    
    with open(output_filepath, 'w', encoding='utf-8') as file:
        file.writelines(cleaned_lines)

def process_files_in_directory(directory, output_directory):
    """
    遍历指定目录下的所有.txt文件，并对每个文件应用clean_file函数，将清理后的文件保存到output_directory。
    
    :param directory: str, 要处理的文件所在目录
    :param output_directory: str, 清理后的文件输出目录
    """
    # 确保输出目录存在
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            input_path = os.path.join(directory, filename)
            # 构建输出文件路径
            output_filename = f"cleaned_{filename}"
            output_path = os.path.join(output_directory, output_filename)
            clean_file(input_path, output_path)
            print(f"Processed and saved: {output_path}")

def create_excel_from_cleaned_files(directory, excel_path):
    """
    从指定目录下的所有cleaned .txt文件中读取数据，并创建一个Excel文件。
    
    :param directory: str, 包含cleaned .txt文件的目录
    :param excel_path: str, 生成的Excel文件路径
    """
    # 定义关键字列表作为表头
    keywords = [
        '行政处罚决定书文号', '被处罚当事人', '主要违法违规事实',
        '行政处罚依据', '行政处罚决定', '作出处罚决定的机关名称',
        '作出处罚决定的日期'
    ]
    
    # 创建一个空的数据框
    df = pd.DataFrame(columns=keywords)
    
    for filename in os.listdir(directory):
        if filename.startswith('cleaned_') and filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # 为每个文件创建一个新的行
            row_data = {keyword: '' for keyword in keywords}
            for line in lines:
                for keyword in keywords:
                    if keyword in line:
                        # 提取关键字后的值
                        value = line.split(keyword, 1)[1].strip()
                        row_data[keyword] = value
                        break  # 找到匹配的关键字后跳出内层循环
            
            # 将当前文件的数据添加到DataFrame
            df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
    
    # 写入Excel文件
    df.to_excel(excel_path, index=False, engine='openpyxl')

# 使用方法
input_directory = 'output'  # 设置你的输入文件夹路径
output_cleaned_directory = 'output\\cleaned'  # 设置清理后文件的输出文件夹路径
excel_output_path = 'output\\cleaned\\汇总信息.xlsx'  # 设置Excel输出文件路径

# 清理文件
process_files_in_directory(input_directory, output_cleaned_directory)

# 创建Excel
create_excel_from_cleaned_files(output_cleaned_directory, excel_output_path)