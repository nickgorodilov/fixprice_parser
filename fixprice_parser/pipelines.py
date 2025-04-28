# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import os
from datetime import datetime
import scrapy

class JsonExportPipeline:
    """
    Конвейер для экспорта данных в JSON-файл
    """
    
    def __init__(self):
        self.file = None
        self.items = []  # Список для хранения всех собранных товаров
        
    def open_spider(self, spider):
        """Метод вызывается при запуске паука"""
        # Получаем базовый путь проекта
        project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        
        # Создаем директорию для сохранения результатов внутри пакета проекта
        output_dir = os.path.join(project_dir, 'fixprice_parser', 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Формируем имя файла в формате fixprice_YYYY-MM-DD_HH-MM-SS.json с полным путем
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.file_name = os.path.join(output_dir, f'fixprice_{timestamp}.json')
        
        spider.logger.info(f'Будет создан файл: {self.file_name}')
    
    def close_spider(self, spider):
        """Метод вызывается при завершении паука"""
        # Записываем все собранные элементы в файл
        with open(self.file_name, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=4)
        
        spider.logger.info(f'Сохранено {len(self.items)} товаров в файл {self.file_name}')
    
    def process_item(self, item, spider):
        """Метод вызывается для каждого извлеченного товара"""
        # Добавляем элемент в список
        self.items.append(dict(item))
        return item  # Возвращаем элемент для дальнейшей обработки (если есть)
