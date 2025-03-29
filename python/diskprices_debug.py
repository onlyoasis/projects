import asyncio
from playwright.async_api import async_playwright

async def debug_website():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)  # 设为False以查看浏览器
    page = await browser.new_page()
    
    try:
        print("正在访问网站...")
        await page.goto("https://diskprices.com/", timeout=60000)
        print("页面已加载")
        
        # 截图保存
        await page.screenshot(path="diskprices_screenshot.png")
        print("已保存截图到 diskprices_screenshot.png")
        
        # 输出页面HTML结构
        html_content = await page.content()
        with open("diskprices_html.txt", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("已保存HTML到 diskprices_html.txt")
        
        # 等待用户查看
        print("请按Enter键继续...")
        input()
        
    except Exception as e:
        print(f"调试过程中出错: {e}")
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(debug_website()) 