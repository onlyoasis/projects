import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time
import os
import json
from datetime import datetime
import random

class EnhancedDiskPricesScraper:
    def __init__(self, filters=None, sort_by=None):
        self.url = "https://diskprices.com/"
        self.data = []
        self.filters = filters or {}  # 例如: {'type': 'internal', 'capacity': '1TB-4TB'}
        self.sort_by = sort_by  # 例如: 'price_per_tb'
        
    async def initialize(self):
        """初始化 Playwright 和浏览器"""
        try:
            self.playwright = await async_playwright().start()
            # 使用更真实的浏览器配置
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            # 设置更真实的浏览器上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            )
            self.page = await self.context.new_page()
            print("浏览器初始化成功")
        except Exception as e:
            print(f"初始化失败: {e}")
            raise
    
    async def apply_filters(self):
        """应用过滤器"""
        try:
            if 'type' in self.filters:
                disk_type = self.filters['type'].lower()
                # 尝试多种可能的选择器
                selectors = [
                    f'text={disk_type.capitalize()}',
                    f'button:has-text("{disk_type.capitalize()}")',
                    f'.filter-option:has-text("{disk_type.capitalize()}")',
                    f'label:has-text("{disk_type.capitalize()}")'
                ]
                
                for selector in selectors:
                    try:
                        element = await self.page.query_selector(selector)
                        if element:
                            print(f"找到过滤器元素: {selector}")
                            await element.click()
                            await self.page.wait_for_timeout(2000)
                            print(f"已点击 {disk_type} 过滤器")
                            break
                    except Exception as e:
                        print(f"尝试点击 {selector} 时出错: {e}")
            
            if 'capacity' in self.filters:
                # 假设有容量过滤器
                capacity = self.filters['capacity']
                # 实现容量过滤逻辑
                
            if 'brand' in self.filters:
                # 假设有品牌过滤器
                brand = self.filters['brand']
                # 实现品牌过滤逻辑
                
            print(f"已应用过滤器: {self.filters}")
            return True
        except Exception as e:
            print(f"应用过滤器时出错: {e}")
            return False
    
    async def apply_sorting(self):
        """应用排序"""
        try:
            if self.sort_by:
                # 实现排序逻辑
                if self.sort_by == 'price':
                    # 点击价格排序按钮
                    await self.page.click('th:has-text("Price")')
                elif self.sort_by == 'price_per_tb':
                    # 点击每TB价格排序按钮
                    await self.page.click('th:has-text("Price/TB")')
                await self.page.wait_for_timeout(1000)
                print(f"已按 {self.sort_by} 排序")
            return True
        except Exception as e:
            print(f"应用排序时出错: {e}")
            return False
    
    async def scrape(self, max_pages=None):
        """爬取网站数据"""
        try:
            print(f"正在访问 {self.url}")
            await self.page.goto(self.url, timeout=60000)
            print("页面已加载")
            
            # 保存页面截图以便调试
            await self.page.screenshot(path="debug_screenshot.png")
            print("已保存页面截图到 debug_screenshot.png")
            
            # 分析页面结构
            print("分析页面结构...")
            
            # 查找所有表格
            tables = await self.page.query_selector_all('table')
            print(f"找到 {len(tables)} 个表格")
            
            # 获取所有表格的类名
            table_classes = []
            for i, table in enumerate(tables):
                class_attr = await table.get_attribute('class')
                table_classes.append(class_attr)
                print(f"表格 {i+1} 类名: {class_attr}")
            
            # 等待表格加载完成 - 使用更通用的选择器
            print("等待表格加载...")
            try:
                # 首先尝试原始选择器
                await self.page.wait_for_selector('table.disktable', timeout=10000)
                table_selector = 'table.disktable'
                print("找到原始表格选择器: table.disktable")
            except Exception:
                print("未找到 table.disktable，尝试其他选择器...")
                # 尝试找到包含硬盘数据的表格
                await self.page.wait_for_selector('table', timeout=20000)
                # 使用评估脚本找到可能的数据表格
                table_selector = await self.page.evaluate('''
                    () => {
                        // 查找所有表格
                        const tables = document.querySelectorAll('table');
                        
                        // 查找包含硬盘数据的表格
                        for (let table of tables) {
                            // 检查表头是否包含典型的硬盘数据列
                            const headers = table.querySelectorAll('th');
                            const headerTexts = Array.from(headers).map(h => h.innerText.toLowerCase());
                            
                            if (headerTexts.some(text => 
                                text.includes('price') || 
                                text.includes('capacity') || 
                                text.includes('model') ||
                                text.includes('tb')
                            )) {
                                // 返回这个表格的选择器
                                return table.tagName.toLowerCase() + 
                                       (table.className ? '.' + table.className.replace(/\\s+/g, '.') : '');
                            }
                        }
                        
                        // 如果没有找到特定表格，返回第一个表格的选择器
                        const firstTable = document.querySelector('table');
                        return firstTable ? 
                               firstTable.tagName.toLowerCase() + 
                               (firstTable.className ? '.' + firstTable.className.replace(/\\s+/g, '.') : '') : 
                               'table';
                    }
                ''')
                print(f"使用替代表格选择器: {table_selector}")
            
            print(f"表格已加载，使用选择器: {table_selector}")
            
            # 应用过滤器和排序
            await self.apply_filters()
            await self.apply_sorting()
            
            # 获取所有页面的数据
            has_next_page = True
            page_num = 1
            
            while has_next_page and (max_pages is None or page_num <= max_pages):
                print(f"正在爬取第 {page_num} 页...")
                
                # 添加随机延迟，模拟人类行为
                await self.page.wait_for_timeout(random.randint(1000, 3000))
                
                # 等待表格数据加载 - 使用找到的选择器
                await self.page.wait_for_selector(f'{table_selector} tbody tr', timeout=10000)
                
                # 提取当前页面的数据
                rows = await self.page.query_selector_all(f'{table_selector} tbody tr')
                print(f"找到 {len(rows)} 行数据")
                
                # 如果没有找到行数据，尝试其他方法
                if len(rows) == 0:
                    print("未找到行数据，尝试直接提取表格内容...")
                    # 提取整个表格的HTML
                    table_html = await self.page.evaluate(f'document.querySelector("{table_selector}").outerHTML')
                    with open("table_html.txt", "w", encoding="utf-8") as f:
                        f.write(table_html)
                    print("已保存表格HTML到 table_html.txt")
                    
                    # 尝试使用更通用的选择器
                    rows = await self.page.query_selector_all('tr')
                    print(f"使用通用选择器找到 {len(rows)} 行数据")
                
                for row in rows:
                    try:
                        # 提取每一行的数据
                        cells = await row.query_selector_all('td')
                        
                        # 如果这一行没有足够的单元格，可能是表头或空行
                        if len(cells) < 3:
                            continue
                        
                        # 打印单元格数量以便调试
                        print(f"行包含 {len(cells)} 个单元格")
                        
                        # 提取第一个单元格的文本作为产品名称
                        product_name = await cells[0].inner_text() if len(cells) > 0 else "N/A"
                        
                        # 尝试提取链接
                        product_link = await cells[0].query_selector('a') if len(cells) > 0 else None
                        product_url = await product_link.get_attribute('href') if product_link else "N/A"
                        
                        # 根据单元格数量灵活提取数据
                        capacity = await cells[1].inner_text() if len(cells) > 1 else "N/A"
                        price = await cells[2].inner_text() if len(cells) > 2 else "N/A"
                        
                        # 其他字段可能不存在，使用条件提取
                        price_per_tb = await cells[3].inner_text() if len(cells) > 3 else "N/A"
                        interface = await cells[4].inner_text() if len(cells) > 4 else "N/A"
                        form_factor = await cells[5].inner_text() if len(cells) > 5 else "N/A"
                        seller = await cells[6].inner_text() if len(cells) > 6 else "N/A"
                        
                        # 提取更多详细信息
                        details = {}
                        try:
                            # 获取卖家链接
                            if len(cells) > 6:
                                seller_link = await cells[6].query_selector('a')
                                if seller_link:
                                    details['seller_url'] = await seller_link.get_attribute('href')
                        
                            # 获取其他可能的详细信息
                            details['raw_price'] = price.replace('$', '').strip() if '$' in price else price
                            if price_per_tb != "N/A":
                                details['raw_price_per_tb'] = price_per_tb.replace('$', '').strip() if '$' in price_per_tb else price_per_tb
                        except Exception as e:
                            print(f"提取详细信息时出错: {e}")
                        
                        self.data.append({
                            'product_name': product_name,
                            'product_url': product_url,
                            'capacity': capacity,
                            'price': price,
                            'price_per_tb': price_per_tb,
                            'interface': interface,
                            'form_factor': form_factor,
                            'seller': seller,
                            'details': details,
                            'date_scraped': datetime.now().strftime('%Y-%m-%d')
                        })
                    except Exception as e:
                        print(f"处理行数据时出错: {e}")
                        continue
                
                # 如果成功提取了数据，保存一个中间结果
                if self.data and page_num == 1:
                    self.save_to_csv("first_page_data.csv")
                    print("已保存第一页数据到 first_page_data.csv")
                
                # 检查是否有下一页 - 使用更灵活的方法
                try:
                    if max_pages and page_num >= max_pages:
                        print(f"已达到最大页数限制 ({max_pages})")
                        has_next_page = False
                    else:
                        # 尝试多种可能的下一页按钮选择器
                        next_button = None
                        for selector in [
                            'a.page-link[aria-label="Next"]', 
                            'a[aria-label="Next"]',
                            'a:has-text("Next")',
                            'a:has-text("下一页")',
                            'button:has-text("Next")',
                            '.pagination .next',
                            '.pagination li:last-child a'
                        ]:
                            next_button = await self.page.query_selector(selector)
                            if next_button:
                                print(f"找到下一页按钮: {selector}")
                                break
                        
                        if next_button:
                            # 检查下一页按钮是否被禁用
                            is_disabled = await next_button.get_attribute('aria-disabled')
                            disabled_class = await next_button.get_attribute('class')
                            
                            if is_disabled == 'true' or (disabled_class and 'disabled' in disabled_class):
                                has_next_page = False
                                print("已到达最后一页")
                            else:
                                print("点击下一页")
                                # 使用JavaScript点击，更可靠
                                await self.page.evaluate('(button) => button.click()', next_button)
                                await self.page.wait_for_timeout(3000)  # 等待新页面加载
                                page_num += 1
                        else:
                            has_next_page = False
                            print("未找到下一页按钮")
                except Exception as e:
                    print(f"处理分页时出错: {e}")
                    has_next_page = False
                    
            print(f"爬取完成，共获取 {len(self.data)} 条数据")
            
            # 如果没有数据但已经分析了页面，保存页面内容以便进一步分析
            if not self.data:
                print("未能提取到数据，保存页面内容以便分析...")
                html_content = await self.page.content()
                with open("full_page_html.txt", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("已保存完整页面HTML到 full_page_html.txt")
                
        except Exception as e:
            print(f"爬取过程中出错: {e}")
            # 保存已爬取的数据
            if self.data:
                print("保存已爬取的部分数据...")
                self.save_to_csv("partial_data.csv")
            
            # 保存页面截图和HTML以便调试
            try:
                await self.page.screenshot(path="error_screenshot.png")
                print("已保存错误页面截图到 error_screenshot.png")
                
                html_content = await self.page.content()
                with open("error_page_html.txt", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("已保存错误页面HTML到 error_page_html.txt")
            except Exception as debug_error:
                print(f"保存调试信息时出错: {debug_error}")
    
    def save_to_csv(self, filename=None):
        """将数据保存为CSV文件"""
        if not self.data:
            print("没有数据可保存")
            return
            
        if not filename:
            filename = f"diskprices_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            # 处理嵌套的details字典
            flat_data = []
            for item in self.data:
                flat_item = item.copy()
                if 'details' in flat_item:
                    details = flat_item.pop('details')
                    for k, v in details.items():
                        flat_item[k] = v
                flat_data.append(flat_item)
                
            df = pd.DataFrame(flat_data)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"数据已保存到 {filename}")
        except Exception as e:
            print(f"保存CSV时出错: {e}")
    
    def save_to_excel(self, filename=None):
        """将数据保存为Excel文件"""
        if not self.data:
            print("没有数据可保存")
            return
            
        if not filename:
            filename = f"diskprices_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        try:
            # 处理嵌套的details字典
            flat_data = []
            for item in self.data:
                flat_item = item.copy()
                if 'details' in flat_item:
                    details = flat_item.pop('details')
                    for k, v in details.items():
                        flat_item[k] = v
                flat_data.append(flat_item)
                
            df = pd.DataFrame(flat_data)
            df.to_excel(filename, index=False)
            print(f"数据已保存到 {filename}")
        except Exception as e:
            print(f"保存Excel时出错: {e}")
    
    def save_to_json(self, filename=None):
        """将数据保存为JSON文件"""
        if not self.data:
            print("没有数据可保存")
            return
            
        if not filename:
            filename = f"diskprices_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到 {filename}")
        except Exception as e:
            print(f"保存JSON时出错: {e}")
    
    async def close(self):
        """关闭浏览器和 Playwright"""
        try:
            await self.browser.close()
            await self.playwright.stop()
            print("浏览器已关闭")
        except Exception as e:
            print(f"关闭浏览器时出错: {e}")

async def main():
    # 示例：使用过滤器和排序
    filters = {
        'type': 'internal',  # 'internal' 或 'external'
        # 'capacity': '1TB-4TB',  # 容量范围
        # 'brand': 'WD'  # 品牌
    }
    sort_by = 'price_per_tb'  # 'price' 或 'price_per_tb'
    
    scraper = EnhancedDiskPricesScraper(filters=filters, sort_by=sort_by)
    try:
        await scraper.initialize()
        await scraper.scrape(max_pages=3)  # 限制爬取前3页
        scraper.save_to_csv()
        scraper.save_to_excel()
        scraper.save_to_json()
    except Exception as e:
        print(f"主程序出错: {e}")
    finally:
        await scraper.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"程序执行失败: {e}") 