# Joox 广告数据独立清洗脚本（修复日期列处理问题）
import pandas as pd
import numpy as np

# 配置项（无需修改）
joox_path = "D:\下载\周报\gitDate\print\sql_joox.csv"
save_path = "D:\下载\周报\gitDate\print\清洗后_Joox广告数据.xlsx"

# 1. 读取数据（处理BOM问题）
print("开始读取Joox原始数据...")
try:
    df = pd.read_csv(joox_path, encoding='utf-8-sig', index_col=False)
except:
    df = pd.read_csv(joox_path, encoding='gbk', index_col=False)

# 检查列名，去除可能的BOM和空白字符
print("原始列名：", df.columns.tolist())
df.columns = df.columns.str.strip()
print("清理后列名：", df.columns.tolist())

df = df.reset_index(drop=True)

# 2. 日期标准化处理
print("统一日期格式（仅保留年月日，删除原始日期列）...")

# 找到原始的日期列名
original_date_col = None
for col in df.columns:
    if "日期" in col:
        original_date_col = col
        print(f"找到原始日期列：'{original_date_col}'")
        break

if original_date_col is None:
    raise ValueError("未找到日期列！")

# 处理日期：将原始日期转换为标准日期格式
df[original_date_col] = df[original_date_col].astype(str).str.replace(",", "").str.strip()

# 尝试不同的日期格式
try:
    df["日期"] = pd.to_datetime(df[original_date_col], format="%Y%m%d").dt.date
except:
    # 如果格式不对，尝试其他方式
    df["日期"] = pd.to_datetime(df[original_date_col], errors='coerce').dt.date

# 过滤空值行
print(f"处理前数据量：{len(df)} 行")
df = df[df["日期"].notna()]
print(f"处理后数据量：{len(df)} 行")

# 删除原始日期列（现在我们有新的"日期"列）
if original_date_col in df.columns:
    df = df.drop(columns=[original_date_col])

df = df.reset_index(drop=True)

# 调试：显示当前列名
print("当前列名：", df.columns.tolist())
print("数据预览：")
print(df[["日期"]].head() if "日期" in df.columns else "日期列不存在！")

# 3. 日期列置顶
print("日期列置顶...")
if "日期" in df.columns:
    date_col = "日期"
    other_cols = [col for col in df.columns if col != date_col]
    df = df[[date_col] + other_cols]
    print("日期列已置顶")
else:
    # 如果没有找到日期列，创建默认日期列
    print("警告：未找到'日期'列，将使用索引作为日期")
    df["日期"] = pd.date_range(start="2024-01-01", periods=len(df), freq="D").date
    other_cols = [col for col in df.columns if col != "日期"]
    df = df[["日期"] + other_cols]

# 4. 处理缺失值
print("处理缺失值...")
num_cols = [
    "dau", "大盘广告收益￥", "大盘ecpm-￥", "大盘广告曝光总次数",
    "免模收入", "免模ecpm", "网赚收入", "网赚ecpm", "原生收入", "原生ecpm"
]
# 只处理实际存在的列
existing_num_cols = [col for col in num_cols if col in df.columns]
if existing_num_cols:
    df[existing_num_cols] = df[existing_num_cols].fillna(0)
    print(f"已处理缺失值的列：{existing_num_cols}")

# 5. 处理异常值
print("处理异常值...")
if "dau" in df.columns and "大盘广告曝光总次数" in df.columns:
    df = df[(df["dau"] > 0) & (df["大盘广告曝光总次数"] >= 0)]
    print("已过滤dau和曝光次数异常值")

if "大盘广告收益￥" in df.columns:
    q99 = df["大盘广告收益￥"].quantile(0.99)
    df = df[df["大盘广告收益￥"] <= q99]
    print(f"已过滤大盘广告收益异常值（> 99%分位数：{q99:.2f}）")

# 6. 计算衍生指标
print("计算衍生指标...")
if all(col in df.columns for col in ["大盘广告收益￥", "大盘广告曝光总次数"]):
    df["大盘单曝光收益_￥"] = np.where(
        df["大盘广告曝光总次数"] > 0,
        (df["大盘广告收益￥"] / df["大盘广告曝光总次数"]).round(6),
        0
    )
    print("已计算大盘单曝光收益_￥")

if all(col in df.columns for col in ["大盘广告收益￥", "网赚收入"]):
    df["网赚收益占比"] = np.where(
        df["大盘广告收益￥"] > 0,
        (df["网赚收入"] / df["大盘广告收益￥"]).round(4),
        0
    )
    print("已计算网赚收益占比")

if all(col in df.columns for col in ["大盘广告收益￥", "免模收入"]):
    df["免模收益占比"] = np.where(
        df["大盘广告收益￥"] > 0,
        (df["免模收入"] / df["大盘广告收益￥"]).round(4),
        0
    )
    print("已计算免模收益占比")

if all(col in df.columns for col in ["大盘广告收益￥", "原生收入"]):
    df["原生收益占比"] = np.where(
        df["大盘广告收益￥"] > 0,
        (df["原生收入"] / df["大盘广告收益￥"]).round(4),
        0
    )
    print("已计算原生收益占比")

# 7. 保存数据
print("保存清洗后数据...")
df.to_excel(save_path, index=False, engine="openpyxl")

# 8. 输出总结
print("\n===== Joox 数据清洗完成！ =====")
print(f"📊 有效数据量：{len(df)} 行")
if "日期" in df.columns:
    min_date = df["日期"].min()
    max_date = df["日期"].max()
    print(f"🗓️  时间范围：{min_date} 至 {max_date}")
print(f"📈 数据列数：{len(df.columns)}")
print(f"💾 保存路径：{save_path}")
print("✅ 已完成：日期置顶+删原日期+纯年月日+衍生指标完整")