# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import json
import logging
import random
import re
from scrapy import signals
from scrapy.http import HtmlResponse
from seleniumwire import webdriver
import urllib.parse
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.common.exceptions import TimeoutException
import os

class SeleniumMiddleware:    
	def __init__(self):   
		self.logger = logging.getLogger('SeleniumMiddleware')
		self.proxies = []		
		self.ekaterinburg_data = {"city":"Екатеринбург","cityId":55,"longitude":60.597474,"latitude":56.838011,"prefix":"г"}
		self.encoded_cookie_value = urllib.parse.quote(json.dumps(self.ekaterinburg_data, ensure_ascii=False))

		selenium_logger = logging.getLogger('seleniumwire')
		selenium_logger.setLevel(logging.ERROR)

	def wait_for_loader_to_disappear(self, driver, timeout=30):
		loader_selector = '[data-component="VLoader"]'
		try:
			WebDriverWait(driver, 5).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, loader_selector))
			)
		except TimeoutException:			
			self.logger.warning("Загрузчик не найден")				
		try:
			WebDriverWait(driver, timeout).until_not(
				EC.presence_of_element_located((By.CSS_SELECTOR, loader_selector))
			)
		except TimeoutException:
			error_message = "Загрузчик не исчез"
			self.logger.warning(error_message)
			raise Exception(error_message)

	def init_driver(self):
		self.logger.debug("Инициализация Chrome WebDriver")
		
		user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
		seleniumwire_options = {
			'disable_encoding': True, 
			'verify_ssl': False,
			'exclude_hosts': ['google.com', 'yandex.ru', 'mail.ru', 'googleapis.com', 'vk.com'],
			'ignore_http_methods': ['OPTIONS', 'TRACE']
		}

		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--headless')  
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--disable-dev-shm-usage')
		chrome_options.add_argument('--disable-gpu')
		chrome_options.add_argument('--window-size=1920,1080')		
		chrome_options.add_argument(f'user-agent={user_agent}')

		if self.proxies:
			proxy = random.choice(self.proxies)
			chrome_options.add_argument(f'--proxy-server={proxy}')
			self.logger.info(f"Используется прокси: {proxy}")
        
		try:
			driver = webdriver.Chrome(
				options=chrome_options,
				seleniumwire_options=seleniumwire_options
			)
			self.logger.debug("Chrome WebDriver инициализирован")
			
			# Установка куки для города Екатеринбург
			driver.get("https://fix-price.com/")			
			driver.add_cookie({
				'name': 'locality',
				'value': self.encoded_cookie_value,
				'domain': '.fix-price.com',
				'path': '/'
			})
			
			return driver
		except Exception as e:
			self.logger.error(f"Ошибка при инициализации Chrome WebDriver: {e}")
			raise e
		
	def capture_debug_info(self, driver, url):
		# Создание директории для сохранения отладочной информации
		debug_dir = 'debug_screenshots'
		os.makedirs(debug_dir, exist_ok=True)

		# Сохранение скриншота
		screenshot_path = os.path.join(debug_dir, f'screenshot_{int(time.time())}.png')
		driver.save_screenshot(screenshot_path)
		self.logger.info(f"Скриншот сохранен: {screenshot_path}")

		# Сохранение HTML
		html_path = os.path.join(debug_dir, f'page_{int(time.time())}.html')
		with open(html_path, 'w', encoding='utf-8') as f:
			f.write(driver.page_source)
		self.logger.info(f"HTML сохранен: {html_path}")
	
	def process_request(self, request, spider):
		if not request.meta.get('selenium', False):
			return None
	
		driver = None
		try:
			driver = self.init_driver()
			
			self.logger.info(f"Загрузка страницы: {request.url}")
			driver.get(request.url)			
			self.wait_for_loader_to_disappear(driver)
			try:
				WebDriverWait(driver, 20).until(
					EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.city-obtain.spread .geo'), "Екатеринбург")
				)
			except TimeoutException:
				raise Exception("Город не установлен ❌")

			def tag_request(pattern, timeout=30):			
				pattern = re.escape(pattern)
				try:
					request.meta['tagged_request'] = driver.wait_for_request(
						pattern, 
						timeout
					)				
					
				except TimeoutException:
					self.logger.warning("API запрос не перехвачен в течение 30 секунд")

			if '/p-' in request.url:
				self.logger.info(f"Загружена страница товара: {request.url}")
				WebDriverWait(driver, 20).until(
					EC.presence_of_element_located((By.CSS_SELECTOR, '.product-details'))
				)
			else:
				self.logger.info(f"Загружена страница категории: {request.url}")
				WebDriverWait(driver, 20).until(
					EC.presence_of_element_located((By.CSS_SELECTOR, '.category-content'))
				)
				tag_request('/v1/product/')
				try:
					WebDriverWait(driver, 10).until(
						EC.presence_of_element_located((By.CSS_SELECTOR, '.pagination .number'))
					)
				except TimeoutException:
					self.logger.warning("Элемент с пагинацией не найден")
								
			response = HtmlResponse(
				url=driver.current_url,
				body=driver.page_source,
				encoding='utf-8',
				request=request,
			)
			return response
			
		except Exception as e:
			self.logger.error(f"Ошибка при загрузке страницы: {e}")
			if driver:
				self.capture_debug_info(driver, request.url)
			raise e
		finally:			
			if driver:
				self.logger.debug("Закрытие WebDriver")
				driver.quit()

class FixpriceParserSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn't have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class FixpriceParserDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
