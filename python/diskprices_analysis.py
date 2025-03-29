import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_data(file_path):
    """加载数据文件"""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        return pd.read_excel(file_path)
    else:
        raise ValueError("不支持的文件格式，请提供CSV或Excel文件")

def clean_data(df):
    """清洗和准备数据"""
    # 清理价格数据
    df['price_clean'] = df['price'].str.replace('$', '').str.replace(',', '').astype(float)
    df['price_per_tb_clean'] = df['price_per_tb'].str.replace('$', '').str.replace(',', '').astype(float)
    
    # 提取容量为数字
    df['capacity_num'] = df['capacity'].str.extract(r'(\d+\.?\d*)').astype(float)
    df['capacity_unit'] = df['capacity'].str.extract(r'(\D+)$')
    
    # 标准化容量单位为TB
    conditions = [
        df['capacity_unit'].str.contains('TB', case=False),
        df['capacity_unit'].str.contains('GB', case=False)
    ]
    choices = [
        df['capacity_num'],
        df['capacity_num'] / 1024
    ]
    df['capacity_tb'] = np.select(conditions, choices, default=df['capacity_num'])
    
    return df

def analyze_data(df):
    """分析数据并生成统计信息"""
    # 基本统计
    print("数据概览:")
    print(df.describe())
    
    # 按卖家统计
    seller_stats = df.groupby('seller').agg({
        'product_name': 'count',
        'price_clean': 'mean',
        'price_per_tb_clean': 'mean'
    }).rename(columns={
        'product_name': '产品数量',
        'price_clean': '平均价格',
        'price_per_tb_clean': '平均每TB价格'
    }).sort_values('产品数量', ascending=False)
    
    print("\n卖家统计:")
    print(seller_stats)
    
    # 按接口类型统计
    interface_stats = df.groupby('interface').agg({
        'product_name': 'count',
        'price_clean': 'mean',
        'price_per_tb_clean': 'mean'
    }).rename(columns={
        'product_name': '产品数量',
        'price_clean': '平均价格',
        'price_per_tb_clean': '平均每TB价格'
    }).sort_values('产品数量', ascending=False)
    
    print("\n接口类型统计:")
    print(interface_stats)
    
    return {
        'seller_stats': seller_stats,
        'interface_stats': interface_stats
    }

def visualize_data(df, stats, output_dir='charts'):
    """可视化数据"""
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 设置样式
    sns.set(style="whitegrid")
    
    # 1. 价格分布图
    plt.figure(figsize=(10, 6))
    sns.histplot(df['price_clean'], bins=30, kde=True)
    plt.title('硬盘价格分布')
    plt.xlabel('价格 ($)')
    plt.ylabel('数量')
    plt.savefig(f'{output_dir}/price_distribution.png')
    plt.close()
    
    # 2. 每TB价格分布图
    plt.figure(figsize=(10, 6))
    sns.histplot(df['price_per_tb_clean'], bins=30, kde=True)
    plt.title('每TB价格分布')
    plt.xlabel('每TB价格 ($)')
    plt.ylabel('数量')
    plt.savefig(f'{output_dir}/price_per_tb_distribution.png')
    plt.close()
    
    # 3. 卖家比较图
    top_sellers = stats['seller_stats'].head(10)
    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_sellers.index, y='平均每TB价格', data=top_sellers)
    plt.title('各卖家每TB平均价格比较 (前10名)')
    plt.xlabel('卖家')
    plt.ylabel('每TB平均价格 ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/seller_comparison.png')
    plt.close()
    
    # 4. 接口类型比较图
    plt.figure(figsize=(10, 6))
    sns.barplot(x=stats['interface_stats'].index, y='平均每TB价格', data=stats['interface_stats'])
    plt.title('各接口类型每TB平均价格比较')
    plt.xlabel('接口类型')
    plt.ylabel('每TB平均价格 ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/interface_comparison.png')
    plt.close()
    
    # 5. 容量与价格关系图
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='capacity_tb', y='price_clean', hue='interface', data=df)
    plt.title('容量与价格关系')
    plt.xlabel('容量 (TB)')
    plt.ylabel('价格 ($)')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/capacity_price_relationship.png')
    plt.close()
    
    print(f"可视化图表已保存到 {output_dir} 目录")

def main():
    # 加载最新的数据文件
    files = [f for f in os.listdir() if f.startswith('diskprices_data_') and (f.endswith('.csv') or f.endswith('.xlsx'))]
    if not files:
        print("未找到数据文件")
        return
    
    latest_file = max(files)
    print(f"正在分析文件: {latest_file}")
    
    df = load_data(latest_file)
    df = clean_data(df)
    stats = analyze_data(df)
    visualize_data(df, stats)
    
    print("分析完成")

if __name__ == "__main__":
    main() 