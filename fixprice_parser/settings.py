# Scrapy settings for fixprice_parser project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# Настройка middleware для Selenium
SELENIUM_TIMEOUT = 30  # Увеличенный таймаут для Selenium

# Включаем Selenium middleware с высоким приоритетом
DOWNLOADER_MIDDLEWARES = {
    'fixprice_parser.middlewares.SeleniumMiddleware': 543,
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 400,
}

# Базовые настройки
BOT_NAME = 'fixprice_parser'
SPIDER_MODULES = ['fixprice_parser.spiders']
NEWSPIDER_MODULE = 'fixprice_parser.spiders'
ROBOTSTXT_OBEY = False  # Отключаем соблюдение robots.txt, так как некоторые сайты могут запрещать доступ ботам

# Настройка задержек между запросами (важно для избежания блокировки)
DOWNLOAD_DELAY = 3  # Увеличиваем задержку в секундах между последовательными запросами
RANDOMIZE_DOWNLOAD_DELAY = True  # Случайная задержка

# Настройка User-Agent (маскируемся под обычный браузер)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'

# Настройка конвейеров для обработки данных
ITEM_PIPELINES = {
    'fixprice_parser.pipelines.JsonExportPipeline': 300,  # 300 - это приоритет обработки
}

# Настройка вывода
FEED_EXPORT_ENCODING = 'utf-8'  # Кодировка для сохранения данных

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "fixprice_parser.middlewares.FixpriceParserSpiderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
# REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
