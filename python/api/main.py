from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os
from datetime import datetime
from typing import List, Optional
import glob

app = FastAPI(title="DiskPrices API")

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置数据文件路径 - 根据实际情况调整
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "")

@app.get("/api/latest")
async def get_latest_data():
    """获取最新的爬虫数据"""
    try:
        # 查找所有Excel文件
        excel_files = glob.glob(os.path.join(DATA_DIR, "diskprices_data_*.xlsx"))
        if not excel_files:
            # 尝试查找CSV文件
            csv_files = glob.glob(os.path.join(DATA_DIR, "diskprices_data_*.csv"))
            if not csv_files:
                raise HTTPException(status_code=404, detail="没有找到数据文件")
            latest_file = max(csv_files)
            df = pd.read_csv(latest_file)
        else:
            latest_file = max(excel_files)
            df = pd.read_excel(latest_file, sheet_name="简化数据")
        
        print(f"正在读取文件: {latest_file}")
        
        # 获取列名并重命名为前端期望的格式
        columns = df.columns.tolist()
        column_mapping = {
            "产品名称": "product_name",
            "容量": "capacity",
            "价格": "price",
            "每TB价格": "price_per_tb",
            "接口": "interface",
            "硬盘形态": "form_factor",
            "卖家": "seller",
            "评分": "rating",
            "产品链接": "product_url",
            "卖家链接": "seller_url",
            "爬取时间": "date_scraped"
        }
        
        # 如果列名是中文，进行重命名
        if "产品名称" in columns:
            df = df.rename(columns=column_mapping)
        
        # 转换为JSON格式
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"获取数据出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files")
async def get_data_files():
    """获取所有可用的数据文件"""
    try:
        # 查找所有Excel和CSV文件
        excel_files = glob.glob(os.path.join(DATA_DIR, "diskprices_data_*.xlsx"))
        csv_files = glob.glob(os.path.join(DATA_DIR, "diskprices_data_*.csv"))
        
        all_files = excel_files + csv_files
        files_info = []
        
        for file in all_files:
            filename = os.path.basename(file)
            file_size = os.path.getsize(file)
            file_date = os.path.getmtime(file)
            
            files_info.append({
                "name": filename,
                "size": file_size,
                "date": datetime.fromtimestamp(file_date).strftime("%Y-%m-%d %H:%M:%S"),
                "path": file
            })
        
        return sorted(files_info, key=lambda x: x["date"], reverse=True)
    except Exception as e:
        print(f"获取文件列表出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/file/{filename}")
async def get_file_data(filename: str):
    """获取指定文件的数据"""
    try:
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"文件 {filename} 不存在")
        
        if filename.endswith(".xlsx"):
            df = pd.read_excel(file_path, sheet_name="简化数据")
        else:
            df = pd.read_csv(file_path)
        
        # 处理列名映射
        columns = df.columns.tolist()
        column_mapping = {
            "产品名称": "product_name",
            "容量": "capacity",
            "价格": "price",
            "每TB价格": "price_per_tb",
            "接口": "interface",
            "硬盘形态": "form_factor",
            "卖家": "seller",
            "评分": "rating",
            "产品链接": "product_url",
            "卖家链接": "seller_url",
            "爬取时间": "date_scraped"
        }
        
        # 如果列名是中文，进行重命名
        if "产品名称" in columns:
            df = df.rename(columns=column_mapping)
            
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"获取文件数据出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 挂载静态文件
app.mount("/", StaticFiles(directory="frontend/build", html=True)) 