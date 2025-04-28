import json
import scrapy
import time
import re
from ..items import FixPriceItem
from urllib.parse import urljoin

class FixPriceSpider(scrapy.Spider):
    name = 'fixprice'
    allowed_domains = ['fix-price.com', 'api.fix-price.com']    
    
    def __init__(self, categories=['https://fix-price.com/catalog/kosmetika-i-gigiena/ukhod-za-telom'], *args, **kwargs):
        super(FixPriceSpider, self).__init__(*args, **kwargs)        
        self.captured_product_data = None        
        self.parsed_products = 0
        self.categories = categories        
    
    def start_requests(self):        
        for category_url in self.categories:
            yield scrapy.Request(
                url=category_url,
                callback=self.parse_category,
                meta={'selenium': True, 'category_url': category_url}
            )
    
    def parse_category(self, response):
        self.logger.info(f"Обрабатываю страницу категории: {response.url}")
        response_body = response.meta.get("tagged_request").response.body.decode('utf-8')            
        response_body = json.loads(response_body)   
        keys_to_keep = ['url', 'inStock', 'variantCount']
        response_items = [
			{key: obj[key] for key in keys_to_keep if key in obj}
			for obj in response_body
		]        
        
        if not response_items:
            self.logger.warning(f"На странице не найдено ссылок на товары: {response.url}")            
        else:
            self.logger.info(f"Найдено {len(response_items)} товаров на странице {response.url}")
                    
        for item in response_items:            
            self.logger.info(f"Найден товар: {item}")
            absolute_url = urljoin('https://fix-price.com/catalog/', item['url'])
            self.logger.info(f"Найдена ссылка на товар: {absolute_url}")
            yield scrapy.Request(
                url=absolute_url,
                callback=self.parse_product,
                meta={'selenium': True, 'catalog_data': item}
            )
        
        category_url = response.meta.get('category_url')        
        if not '?page=' in response.url:
            pages = response.css('.pagination .number::text').getall()            
            page_count = int(pages[-1]) if pages else 0
            for page in range(2, page_count + 1):
                next_page_url = category_url + f'?page={page}'
                self.logger.info(f"Переход на следующую страницу: {next_page_url}")
                yield scrapy.Request(
                        url=next_page_url,
                        callback=self.parse_category,
                        meta={'selenium': True, 'category_url': category_url}
                    )               
    
    def get_property_value(self, response, property_title):
        property_element = response.css(f'.additional-information .property:contains("{property_title}")')
        value = property_element.css('span.value::text, a.link::text').get('').strip()        
        return value if value else ''
    
    def convert_to_float(self, price_str):
        if isinstance(price_str, (int, float)):
            return float(price_str)
        elif isinstance(price_str, str):
            price_str = price_str.replace(',', '.')
            return float(re.sub(r'[^0-9.]', '', price_str))
        else:
            return 0.0
        
    def parse_product(self, response):        
        self.logger.info(f"Обрабатываю страницу товара: {response.url}")			
        catalog_data = response.meta.get('catalog_data')        
        item = FixPriceItem()
        item['timestamp'] = int(time.time())
        item['RPC'] = self.get_property_value(response, 'Код товара')
        item['url'] = response.url
        item['title'] = response.css('h1.title::text').get('')
        item['marketing_tags'] = response.css('.price-quantity-block .prices .sticker::text').getall()
        item['brand'] = self.get_property_value(response, 'Бренд')
        item['section'] = response.css('.crumb span.text::text').getall()
        
        price_block = response.css('.price-quantity-block')
        special_price = self.convert_to_float(price_block.css('.special-price::text').get())
        original_price = self.convert_to_float(price_block.css('.regular-price::text').get())
        if special_price > 0:
            discount_percentage = ((original_price - special_price) / original_price) * 100
            sale_tag = f"Скидка {discount_percentage:.2f}%"
        else:
            discount_percentage = 0
            sale_tag = ""
            
        item['price_data'] = {
            'current': special_price if special_price else original_price,
            'original': original_price,
            'sale_tag': sale_tag
        }
        item['stock'] = {
            'in_stock': catalog_data.get('inStock'),
            'count': catalog_data.get('variantCount', 1)
        }
        
        images = response.css('.gallery .zoom::attr(src)').getall()
        item['assets'] = {
            'main_image': images[0] if images else '',
            'set_images': images,
            'view360': [],
            'video': []
        }
        metadata = {
            '__description': response.css('.product-details .description::text').get('')
        }
        attributes = response.css('.property .title::text').getall()
        for attr in attributes:
            metadata[attr] = self.get_property_value(response, attr)
        item['metadata'] = metadata
        item['variants'] = catalog_data.get('variantCount', 1)
        
        self.logger.info(f"Извлечены данные товара: {item.get('title', '')} (RPC: {item.get('RPC', '')})")
        yield item    