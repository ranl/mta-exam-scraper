# -*- coding: utf-8 -*-
"""
Create a list of user agents

scrapy crawl --output=/tmp/ran --output-format=csv user_agent_generator && sed -i '1d' /tmp/ran
"""

# python
import re

# Scrapy
import scrapy

# mta_exam_scraper
from mta_exam_scraper.items import UserAgent


class UserAgentGenerator(scrapy.Spider):

    """
    The Spider Class
    """

    name = 'user_agent_generator'
    allowed_domains = ['http://www.useragentstring.com/']
    min_len = 20
    start_urls = ('http://www.useragentstring.com/pages/All/',)
    exclude = [
        re.compile('^/pages/.*\.php$'),
        re.compile('^/$'),
        re.compile('^http'),
    ]

    def parse(self, response):

        for a in response.xpath('//a'):
            try:
                ua = a.xpath('text()').extract()[0].strip().strip('"')
            except Exception:
                continue

            if len(ua) <= self.min_len:
                continue

            for r in self.exclude:
                try:
                    if r.match(a.xpath('@href').extract()[0]):
                        break
                except Exception:
                    pass
            else:
                yield UserAgent(name=ua)
