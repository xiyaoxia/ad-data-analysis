# Joox 广告数据独立清洗脚本（简化版本，修复日期丢失问题）
import pandas as pd
import numpy as np

# 配置项
joox_path = "D:\下载\周报\gitDate\print\sql_joox.csv"
save_path = "D:\下载\周报\gitDate\print\清洗后_Joox广告数据.xlsx"

print("开始读取Joox原始数据...")
# 读取数据
try:
    df = pd.read_csv(joox_path, encoding='utf-8-sig', index_col=False)
except:
    df = pd.read_csv(joox_path, encoding='gbk', index_col=False)

print(f"原始数据形状: {df.shape}")
print(f"原始列名: {df.columns.tolist()}")

# 清理列名
df.columns = df.columns.str.strip()

# 1. 处理日期列
print("\n=== 处理日期列 ===")

# 检查是否有日期列
if '日期' not in df.columns:
    print("错误：未找到'日期'列")
    print(f"可用列: {df.columns.tolist()}")
    exit()

print(f"原始日期列数据类型: {df['日期'].dtype}")
print(f"前5个日期值: {df['日期'].head().tolist()}")

# 将日期列转换为字符串，清理并转换为datetime
df['日期'] = df['日期'].astype(str).str.strip().str.replace(',', '')

print(f"清理后的前5个日期值: {df['日期'].head().tolist()}")

# 转换为datetime
try:
    # 尝试 %Y%m%d 格式
    df['日期'] = pd.to_datetime(df['日期'], format='%Y%m%d')
    print("✅ 日期转换成功 (格式: %Y%m%d)")
except Exception as e:
    print(f"格式 %Y%m%d 转换失败: {e}")
    # 尝试自动转换
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    print("尝试自动转换日期")

# 检查转换结果
print(f"转换后的日期数据类型: {df['日期'].dtype}")
print(f"前5个转换后日期: {df['日期'].head().tolist()}")
print(f"日期范围: {df['日期'].min()} 到 {df['日期'].max()}")

# 过滤无效日期
before_len = len(df)
df = df[df['日期'].notna()]
after_len = len(df)
print(f"过滤无效日期: {before_len} -> {after_len} 行")

if len(df) == 0:
    print("错误：所有日期都无效！")
    exit()

# 2. 将日期列置顶
print("\n=== 重新排列列顺序 ===")
cols = df.columns.tolist()
# 确保日期列在第一列
if '日期' in cols:
    cols.remove('日期')
    cols = ['日期'] + cols
    df = df[cols]
    print("✅ 日期列已置顶")
else:
    print("错误：日期列丢失！")

print(f"最终列顺序: {df.columns.tolist()}")
print(f"前3行数据预览:")
print(df.head(3))

# 3. 处理缺失值
print("\n=== 处理缺失值 ===")
num_cols = [
    "dau", "大盘广告收益￥", "大盘ecpm-￥", "大盘广告曝光总次数",
    "免模收入", "免模ecpm", "网赚收入", "网赚ecpm", "原生收入", "原生ecpm"
]

# 只处理实际存在的列
existing_num_cols = [col for col in num_cols if col in df.columns]
if existing_num_cols:
    df[existing_num_cols] = df[existing_num_cols].fillna(0)
    print(f"已填充缺失值: {existing_num_cols}")

# 4. 处理异常值
print("\n=== 处理异常值 ===")
if 'dau' in df.columns:
    df = df[df['dau'] > 0]
    print(f"过滤 dau <= 0 的行")

if '大盘广告曝光总次数' in df.columns:
    df = df[df['大盘广告曝光总次数'] >= 0]
    print(f"过滤大盘广告曝光总次数 < 0 的行")

if '大盘广告收益￥' in df.columns:
    q99 = df['大盘广告收益￥'].quantile(0.99)
    df = df[df['大盘广告收益￥'] <= q99]
    print(f"过滤大盘广告收益 > 99%分位数 ({q99:.2f}) 的行")

print(f"处理后数据量: {len(df)} 行")

# 5. 计算衍生指标
print("\n=== 计算衍生指标 ===")

# 大盘单曝光收益
if all(col in df.columns for col in ['大盘广告收益￥', '大盘广告曝光总次数']):
    df['大盘单曝光收益_￥'] = np.where(
        df['大盘广告曝光总次数'] > 0,
        df['大盘广告收益￥'] / df['大盘广告曝光总次数'],
        0
    ).round(6)
    print("✅ 计算: 大盘单曝光收益_￥")

# 网赚收益占比
if all(col in df.columns for col in ['大盘广告收益￥', '网赚收入']):
    df['网赚收益占比'] = np.where(
        df['大盘广告收益￥'] > 0,
        df['网赚收入'] / df['大盘广告收益￥'],
        0
    ).round(4)
    print("✅ 计算: 网赚收益占比")

# 免模收益占比
if all(col in df.columns for col in ['大盘广告收益￥', '免模收入']):
    df['免模收益占比'] = np.where(
        df['大盘广告收益￥'] > 0,
        df['免模收入'] / df['大盘广告收益￥'],
        0
    ).round(4)
    print("✅ 计算: 免模收益占比")

# 原生收益占比
if all(col in df.columns for col in ['大盘广告收益￥', '原生收入']):
    df['原生收益占比'] = np.where(
        df['大盘广告收益￥'] > 0,
        df['原生收入'] / df['大盘广告收益￥'],
        0
    ).round(4)
    print("✅ 计算: 原生收益占比")

# 6. 保存数据
print("\n=== 保存数据 ===")
# 确保日期以合适的格式保存
df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
df.to_excel(save_path, index=False, engine='openpyxl')

# 7. 输出总结
print("\n" + "="*50)
print("📊 JOOX 广告数据清洗完成！")
print("="*50)
print(f"📈 总数据行数: {len(df)}")
print(f"📅 日期范围: {df['日期'].min()} 到 {df['日期'].max()}")
print(f"📋 总列数: {len(df.columns)}")
print(f"💾 保存路径: {save_path}")
print("\n前5行数据预览:")
print(df.head())
print("\n✅ 清洗完成！")