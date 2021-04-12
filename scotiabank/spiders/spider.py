import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SscotiabankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class SscotiabankSpider(scrapy.Spider):
	name = 'scotiabank'
	start_urls = ['https://ky.scotiabank.com/about-scotiabank/media-centre.html']

	def parse(self, response):
		post_links = response.xpath('//div[@class="cmp cmp-text"]//a/@href').getall()[1:]
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//div[@class="cmp cmp-text"]/p[1]//text()').getall()
		try:
			date = re.findall(r'\w+\s\d+\,\s\d+',''.join(date))
		except TypeError:
			date = ""
		try:
			title = response.xpath('//h1/b/text()').get().strip()
		except AttributeError:
			title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//div[@class="cmp cmp-text"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=SscotiabankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
