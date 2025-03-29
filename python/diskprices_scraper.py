try:
    boto3
    from botocore.config import Config
    import pandas as pd
    import time
    import os
    from datetime import datetime
    import json
    import random
    from amazon.paapi import AmazonAPI
except ImportError as e:
    print(f"缺少必要的依赖包: {e}")
    print("请运行: pip install python-amazon-paapi pandas openpyxl boto3")
    exit(1)

class AmazonDiskPricesScraper:
    def __init__(self, access_key, secret_key, partner_tag, country='US'):
        """
        初始化Amazon API客户端
        access_key: Amazon Access Key
        secret_key: Amazon Secret Key
        partner_tag: Amazon Associates Partner Tag
        country: 国家/地区代码
        """
        self.amazon = AmazonAPI(access_key, secret_key, partner_tag, country)
        self.data = []
        
    def search_disks(self):
        """搜索硬盘产品"""
        try:
            # 搜索条件
            search_terms = [
                'internal hard drive',
                'external hard drive',
                'SSD',
                'NVMe SSD',
                'SATA SSD'
            ]
            
            for term in search_terms:
                print(f"搜索: {term}")
                try:
                    # 使用Amazon API搜索产品
                    response = self.amazon.search_items(
                        keywords=term,
                        search_index='Electronics',
                        item_count=10,  # 每个类别获取10个商品
                        resources=[
                            'ItemInfo.Title',
                            'Offers.Listings.Price',
                            'ItemInfo.Features',
                            'ItemInfo.TechnicalInfo',
                            'ItemInfo.Classifications'
                        ]
                    )
                    
                    # 处理搜索结果
                    if response.items:
                        for item in response.items:
                            try:
                                # 提取容量信息
                                capacity = self._extract_capacity(item)
                                if not capacity:
                                    continue
                                
                                # 提取接口类型
                                interface = self._extract_interface(item)
                                
                                # 提取价格
                                price = self._extract_price(item)
                                if not price:
                                    continue
                                
                                # 计算每TB价格
                                price_per_tb = self._calculate_price_per_tb(price, capacity)
                                
                                # 提取硬盘形态
                                form_factor = self._extract_form_factor(item)
                                
                                self.data.append({
                                    'product_name': item.item_info.title.display_value,
                                    'product_url': item.detail_page_url,
                                    'capacity': f"{capacity}TB",
                                    'price': f"${price:.2f}",
                                    'price_per_tb': f"${price_per_tb:.2f}/TB",
                                    'interface': interface,
                                    'form_factor': form_factor,
                                    'seller': 'Amazon',
                                    'date_scraped': datetime.now().strftime('%Y-%m-%d')
                                })
                                
                            except Exception as e:
                                print(f"处理商品时出错: {e}")
                                continue
                    
                    # 避免请求过快
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    print(f"搜索 {term} 时出错: {e}")
                    continue
                
            print(f"搜索完成，共获取 {len(self.data)} 条数据")
            
        except Exception as e:
            print(f"搜索过程中出错: {e}")
            if self.data:
                print("保存已获取的部分数据...")
                self.save_data()
                
    def _extract_capacity(self, item):
        """从商品信息中提取容量（TB）"""
        try:
            # 从标题和特征中提取容量信息
            title = item.item_info.title.display_value.lower()
            features = [f.lower() for f in item.item_info.features.display_values] if item.item_info.features else []
            
            # 常见容量单位转换
            conversions = {
                'tb': 1,
                'gb': 0.001,
                'mb': 0.000001
            }
            
            # 在标题和特征中查找容量信息
            for text in [title] + features:
                for unit, factor in conversions.items():
                    if unit in text:
                        # 使用正则表达式提取数字
                        import re
                        numbers = re.findall(r'(\d+(?:\.\d+)?)\s*' + unit, text)
                        if numbers:
                            return float(numbers[0]) * factor
            
            return None
        except Exception:
            return None
            
    def _extract_interface(self, item):
        """从商品信息中提取接口类型"""
        try:
            # 从标题和特征中提取接口信息
            title = item.item_info.title.display_value.lower()
            features = [f.lower() for f in item.item_info.features.display_values] if item.item_info.features else []
            
            # 常见接口类型
            interfaces = ['sata', 'nvme', 'usb', 'thunderbolt', 'pcie']
            
            # 在标题和特征中查找接口信息
            for text in [title] + features:
                for interface in interfaces:
                    if interface in text:
                        return interface.upper()
            
            return 'Unknown'
        except Exception:
            return 'Unknown'
            
    def _extract_price(self, item):
        """提取商品价格"""
        try:
            if item.offers and item.offers.listings:
                return float(item.offers.listings[0].price.amount)
            return None
        except Exception:
            return None
            
    def _calculate_price_per_tb(self, price, capacity):
        """计算每TB价格"""
        try:
            return price / capacity if capacity > 0 else 0
        except Exception:
            return 0
            
    def _extract_form_factor(self, item):
        """从商品信息中提取硬盘形态"""
        try:
            # 从标题和特征中提取形态信息
            title = item.item_info.title.display_value.lower()
            features = [f.lower() for f in item.item_info.features.display_values] if item.item_info.features else []
            
            # 常见硬盘形态
            form_factors = {
                '2.5': '2.5"',
                '3.5': '3.5"',
                'm.2': 'M.2',
                'external': 'External'
            }
            
            # 在标题和特征中查找形态信息
            for text in [title] + features:
                for key, value in form_factors.items():
                    if key in text:
                        return value
            
            return 'Unknown'
        except Exception:
            return 'Unknown'
        
    def save_data(self):
        """保存数据到各种格式"""
        if not self.data:
            print("没有数据可保存")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 创建data目录
        os.makedirs('data', exist_ok=True)
        
        try:
            # 保存为CSV
            csv_file = f"data/diskprices_{timestamp}.csv"
            df = pd.DataFrame(self.data)
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"数据已保存到CSV: {csv_file}")
            
            # 保存为Excel
            excel_file = f"data/diskprices_{timestamp}.xlsx"
            df.to_excel(excel_file, index=False)
            print(f"数据已保存到Excel: {excel_file}")
            
            # 保存为JSON
            json_file = f"data/diskprices_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到JSON: {json_file}")
            
            # 保存最新数据
            latest_json = "data/latest_data.json"
            with open(latest_json, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"最新数据已保存到: {latest_json}")
            
        except Exception as e:
            print(f"保存数据时出错: {e}")

def main():
    # 请替换为您的Amazon API凭证
    access_key = "YOUR_ACCESS_KEY"
    secret_key = "YOUR_SECRET_KEY"
    partner_tag = "YOUR_PARTNER_TAG"
    
    scraper = AmazonDiskPricesScraper(access_key, secret_key, partner_tag)
    try:
        scraper.search_disks()
        scraper.save_data()
    except Exception as e:
        print(f"主程序出错: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序执行失败: {e}") 