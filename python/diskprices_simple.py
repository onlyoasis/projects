import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time
import os
from datetime import datetime

async def scrape_diskprices():
    """简单版本的diskprices.com爬虫"""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)  # 设为False以便观察
    page = await browser.new_page()
    
    data = []
    
    try:
        print("正在访问网站...")
        await page.goto("https://diskprices.com/", timeout=60000)
        print("页面已加载")
        
        # 保存截图
        await page.screenshot(path="simple_screenshot.png")
        print("已保存截图")
        
        # 等待页面加载完成
        await page.wait_for_load_state("networkidle")
        
        # 查找所有表格
        tables = await page.query_selector_all('table')
        print(f"找到 {len(tables)} 个表格")
        
        if len(tables) > 0:
            # 假设第一个表格是数据表格
            main_table = tables[0]
            
            # 获取表格行
            rows = await main_table.query_selector_all('tbody tr')
            print(f"找到 {len(rows)} 行数据")
            
            for row in rows:
                try:
                    # 获取所有单元格
                    cells = await row.query_selector_all('td')
                    
                    if len(cells) >= 3:  # 至少需要产品名、容量和价格
                        product_text = await cells[0].inner_text()
                        capacity = await cells[1].inner_text() if len(cells) > 1 else "N/A"
                        price = await cells[2].inner_text() if len(cells) > 2 else "N/A"
                        
                        data.append({
                            'product': product_text,
                            'capacity': capacity,
                            'price': price
                        })
                except Exception as e:
                    print(f"处理行时出错: {e}")
            
            # 保存数据
            if data:
                df = pd.DataFrame(data)
                df.to_csv("simple_data.csv", index=False)
                print(f"已保存 {len(data)} 条数据到 simple_data.csv")
            else:
                print("未找到数据")
                
            # 保存表格HTML以便分析
            table_html = await page.evaluate('(table) => table.outerHTML', main_table)
            with open("simple_table.html", "w", encoding="utf-8") as f:
                f.write(table_html)
            print("已保存表格HTML到 simple_table.html")
        else:
            print("未找到表格")
            # 保存完整页面以便分析
            html = await page.content()
            with open("simple_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("已保存页面HTML到 simple_page.html")
    
    except Exception as e:
        print(f"爬取过程中出错: {e}")
        # 保存错误页面
        await page.screenshot(path="simple_error.png")
        html = await page.content()
        with open("simple_error.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("已保存错误页面信息")
    
    finally:
        await browser.close()
        await playwright.stop()
        print("浏览器已关闭")

if __name__ == "__main__":
    asyncio.run(scrape_diskprices()) 