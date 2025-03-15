import pandas as pd
from pypinyin import lazy_pinyin
import math
import json

# 读取Excel（强制所有字段为字符串）
df = pd.read_excel("scholarship_data.xlsx", dtype=str)


def safe_split(value, delimiter='/', default=('', '')):
    """安全分割可能为空的字段"""
    if pd.isna(value) or str(value).strip() == '':
        return default
    parts = str(value).split(delimiter, 1)
    return parts[0], (parts[1] if len(parts) > 1 else '')


def safe_strip(value, default=''):
    """安全处理字符串空值"""
    if pd.isna(value) or str(value).strip() == '':
        return default
    return str(value).strip()


processed_data = []
for _, row in df.iterrows():
    # 处理学号
    full_id, period = safe_split(row.get('完整学号', ''))
    base_id = safe_strip(row.get('学号', '')) or full_id

    # 处理姓名（兼容空值）
    raw_name = safe_strip(row.get('姓名', '未知名'))

    # 生成拼音全拼和首字母（关键新增部分）
    pinyin_list = lazy_pinyin(raw_name)
    pinyin_full = ''.join(pinyin_list)
    pinyin_initials = ''.join([p[0] for p in pinyin_list if p])  # 首字母缩写

    # 构建数据项
    item = {
        "name": raw_name,
        "full_id": f"{full_id}/{period}" if period else full_id,
        "base_id": base_id,
        "period": period,
        "year": safe_strip(row.get('获奖年份', '')),
        "school": safe_strip(row.get('获奖学校', '未知学校')),
        "pinyin": pinyin_full,  # 原有全拼字段
        "pinyin_initials": pinyin_initials,  # 新增首字母字段
        "is_valid": bool(full_id)
    }
    processed_data.append(item)

# 分片存储（每1000条一个文件）
chunk_size = 1000
for i in range(math.ceil(len(processed_data) / chunk_size)):
    chunk = processed_data[i * chunk_size: (i + 1) * chunk_size]
    with open(f'data/chunk_{i:03d}.json', 'w', encoding='utf-8') as f:
        json.dump(chunk, f, ensure_ascii=False, indent=2)