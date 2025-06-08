import os
import pandas as pd
from glob import glob
from tqdm import tqdm

# 数据目录（请根据实际路径修改）
data_dir = "./data"
all_files = sorted(glob(os.path.join(data_dir, "*.csv")))

# 初始化列表用于收集每个文件的数据
df_list = []

for file in tqdm(all_files, desc="读取中"):
    try:
        df = pd.read_csv(file, encoding='utf-8', engine='python', on_bad_lines='skip')
        # 检查字段数量是否一致
        if df.shape[1] == 7:
            df.columns = ['md5', 'content', 'phone', 'conntime', 'recitime', 'lng', 'lat']
            df_list.append(df)
    except Exception as e:
        print(f"文件 {file} 读取失败：{e}")

# 合并所有数据
df_all = pd.concat(df_list, ignore_index=True)

# 时间戳转换（ms -> datetime）
df_all['conntime'] = pd.to_datetime(df_all['conntime'], unit='ms', errors='coerce')
df_all['recitime'] = pd.to_datetime(df_all['recitime'], unit='ms', errors='coerce')

# 清洗无效值（可选）
df_all = df_all.dropna(subset=['content', 'lng', 'lat', 'recitime'])
df_all = df_all[(df_all['lng'].between(115, 118)) & (df_all['lat'].between(39, 42))]

# 保存处理后的数据
df_all.to_csv("cleaned_sms_dataset.csv", index=False)
print(f"合并后的记录数：{len(df_all)}")
