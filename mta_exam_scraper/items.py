# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserAgent(scrapy.Item):

    name = scrapy.Field()


class MtaParserItem(scrapy.Item):

    item_type = scrapy.Field()


class Megama(MtaParserItem):

    id = scrapy.Field()
    name = scrapy.Field()


class Course(MtaParserItem):

    id = scrapy.Field()
    name = scrapy.Field()
    megama = scrapy.Field()


class Exam(MtaParserItem):

    megama = scrapy.Field()
    course = scrapy.Field()
    year = scrapy.Field()
    semester = scrapy.Field()
    moed = scrapy.Field()
    lecturer = scrapy.Field()
    link = scrapy.Field()


class Solution(Exam):

    pass


class Lecturer(MtaParserItem):

    name = scrapy.Field()
    megama = scrapy.Field()
    course = scrapy.Field()
