import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import json

async def scrape_diskprices_enhanced():
    """增强版本的 diskprices.com 爬虫，专门解析 class="disk" 的内容"""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    
    data = []
    
    try:
        print("正在访问网站...")
        await page.goto("https://diskprices.com/", timeout=60000)
        print("页面已加载")
        
        # 等待页面完全加载
        await page.wait_for_load_state("networkidle")
        
        # 获取表格头部信息
        headers = await page.evaluate('''
            () => {
                const headers = document.querySelectorAll('table thead th');
                return Array.from(headers).map(h => h.innerText);
            }
        ''')
        print(f"表格列标题: {headers}")
        
        # 专门获取 class="disk" 的行
        rows = await page.query_selector_all('tr.disk')
        print(f"找到 {len(rows)} 个硬盘数据")
        
        for row in rows:
            try:
                # 获取该行的所有td内容
                cells = await row.query_selector_all('td')
                
                disk_data = {
                    'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # 解析每个td的内容
                for i, cell in enumerate(cells):
                    # 获取td的文本内容
                    text_content = await cell.inner_text()
                    # 获取td的HTML内容
                    html_content = await cell.inner_html()
                    # 获取td中的链接
                    link = await cell.query_selector('a')
                    link_text = await link.inner_text() if link else None
                    link_href = await link.get_attribute('href') if link else None
                    
                    # 根据列的位置存储数据
                    column_prefix = {
                        0: 'product',
                        1: 'capacity',
                        2: 'price',
                        3: 'price_per_tb',
                        4: 'interface',
                        5: 'form_factor',
                        6: 'seller',
                        7: 'rating'
                    }.get(i, f'column_{i}')
                    
                    # 存储该列的所有信息
                    disk_data.update({
                        f'{column_prefix}_text': text_content,
                        f'{column_prefix}_html': html_content,
                        f'{column_prefix}_link_text': link_text,
                        f'{column_prefix}_link_url': link_href
                    })
                
                data.append(disk_data)
                    
            except Exception as e:
                print(f"处理行数据时出错: {e}")
                continue
        
        # 保存数据到不同格式
        if data:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 保存为Excel，包含所有td的内容
            excel_filename = f"diskprices_detailed_{timestamp}.xlsx"
            
            # 创建DataFrame，确保包含所有列
            df = pd.DataFrame(data)
            
            # 重新组织列的顺序
            column_order = []
            for i in range(8):  # 假设最多8列
                prefix = {
                    0: 'product',
                    1: 'capacity',
                    2: 'price',
                    3: 'price_per_tb',
                    4: 'interface',
                    5: 'form_factor',
                    6: 'seller',
                    7: 'rating'
                }.get(i, f'column_{i}')
                
                column_order.extend([
                    f'{prefix}_text',
                    f'{prefix}_html',
                    f'{prefix}_link_text',
                    f'{prefix}_link_url'
                ])
            
            # 添加时间戳列
            column_order.append('date_scraped')
            
            # 重新排序列并保存
            df = df.reindex(columns=column_order)
            
            # 创建一个Excel writer对象
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                # 保存详细数据到第一个sheet
                df.to_excel(writer, sheet_name='详细数据', index=False)
                
                # 创建一个简化版本的sheet
                simple_data = pd.DataFrame({
                    '产品名称': df['product_text'],
                    '容量': df['capacity_text'],
                    '价格': df['price_text'],
                    '每TB价格': df['price_per_tb_text'],
                    '接口': df['interface_text'],
                    '硬盘形态': df['form_factor_text'],
                    '卖家': df['seller_text'],
                    '评分': df.get('rating_text', None),
                    '产品链接': df['product_link_url'],
                    '卖家链接': df['seller_link_url'],
                    '爬取时间': df['date_scraped']
                })
                simple_data.to_excel(writer, sheet_name='简化数据', index=False)
                
                # 创建数据分析sheet - 修改这部分代码
                analysis_sheet_name = '数据分析'
                
                # 首先创建一个空的DataFrame来初始化数据分析sheet
                pd.DataFrame().to_excel(writer, sheet_name=analysis_sheet_name)
                
                # 准备数据分析内容
                analysis_data = {
                    '卖家分布': df['seller_text'].value_counts(),
                    '接口类型分布': df['interface_text'].value_counts(),
                    '硬盘形态分布': df['form_factor_text'].value_counts(),
                    '容量分布': df['capacity_text'].value_counts()
                }
                
                # 获取工作表
                worksheet = writer.sheets[analysis_sheet_name]
                
                # 写入分析数据
                current_row = 1
                for title, data_series in analysis_data.items():
                    # 写入标题
                    worksheet.cell(row=current_row, column=1, value=title)
                    current_row += 1
                    
                    # 写入数据
                    for index, value in data_series.items():
                        worksheet.cell(row=current_row, column=1, value=index)
                        worksheet.cell(row=current_row, column=2, value=value)
                        current_row += 1
                    
                    # 添加空行
                    current_row += 2

            print(f"已保存详细数据到 {excel_filename}")
            
            # 打印简单的数据分析报告
            print("\n数据分析报告:")
            print(f"总商品数量: {len(data)}")
            
            print("\n卖家分布 (前5名):")
            print(df['seller_text'].value_counts().head())
            
            print("\n接口类型分布:")
            print(df['interface_text'].value_counts())
            
            print("\n硬盘形态分布:")
            print(df['form_factor_text'].value_counts())
            
    except Exception as e:
        print(f"爬取过程中出错: {e}")
        await page.screenshot(path="error_screenshot.png")
        
    finally:
        await browser.close()
        await playwright.stop()
        print("浏览器已关闭")

if __name__ == "__main__":
    asyncio.run(scrape_diskprices_enhanced()) 