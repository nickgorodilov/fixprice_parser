# Fixprice Parser

Парсер для сбора данных с сайта Fix Price. Разработан с использованием фреймворка Scrapy.

## Описание проекта

Этот парсер предназначен для автоматического сбора данных о товарах на сайте Fix Price. Он позволяет получать информацию о продуктах, включая названия, цены, категории и другие атрибуты.

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/fixprice_parser.git
cd fixprice_parser
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

Для запуска парсера используйте следующую команду:

```bash
cd fixprice_parser
scrapy crawl fixprice
```

### Параметры запуска

Для указания категорий для парсинга:

```bash
scrapy crawl fixprice -a categories='["https://fix-price.com/catalog/category1","https://fix-price.com/catalog/category2"]'
```

## Использование proxy

Список прокси можно добавить в классе SeleniumMiddleware

## Структура проекта

```
fixprice_parser/
├── fixprice_parser/
│   ├── spiders/
│   │   ├── __init__.py
│   │   └── fixprice_spider.py
│   ├── __init__.py
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   └── settings.py
├── output/
│   └── [result files]
└── scrapy.cfg
```

## Результаты

Результаты работы парсера сохраняются в каталоге `output/` в формате JSON.