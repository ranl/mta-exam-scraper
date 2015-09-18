# -*- coding: utf-8 -*-

# Scrapy settings for mta_exam_scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import os.path

BOT_NAME = 'mta_exam_scraper'

SPIDER_MODULES = ['mta_exam_scraper.spiders']
NEWSPIDER_MODULE = 'mta_exam_scraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'mta_exam_scraper (+http://www.yourdomain.com)'

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'mta_exam_scraper.random_ua.RandomUserAgentMiddleware': 400,
}

ITEM_PIPELINES = {
    'mta_exam_scraper.pipelines.MtaDedupDrop': 400,
    'mta_exam_scraper.pipelines.AddTypePipeline': 500,
}

#FEED_EXPORTERS = {
#    'mta': 'mta_exam_scraper.exporters.MtaExporter',
#}

USER_AGENT_LIST = os.path.join(os.path.dirname(__file__), 'ua.txt')

