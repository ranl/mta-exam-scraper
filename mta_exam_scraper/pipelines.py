# -*- coding: utf-8 -*-
"""
Mta Exam Scraper Pipelines
"""

# Python Std
from collections import defaultdict

# Scrapy
from scrapy.exceptions import DropItem

# mta_exam_scraper
from mta_exam_scraper.items import (
    Megama,
    Course,
    Lecturer,
)


class AddTypePipeline(object):

    """
    Add the type of the item (class name)
    to the item
    """

    def process_item(self, item, spider):
        item['item_type'] = type(item).__name__
        return item


class MtaDedupDrop(object):

    """
    Drop duplication
    """

    def __init__(self):
        self.lecturers = set()
        self.megamas = set()
        self.courses = defaultdict(set)

    def _validate(self, item_id, item_set, item_type):
        """
        Validate against the set
        """

        if item_id in item_set:
            raise DropItem('Duplicate {0}'.format(
                item_type,
            ))
        item_set.add(item_id)

    def process_item(self, item, spider):
        """
        Process the item and drop it if it exists
        """

        if isinstance(item, Lecturer):
            self._validate(str(item), self.lecturers, 'lecturer')
        elif isinstance(item, Course):
            self._validate(item['name'], self.courses[item['megama']], 'course')
        elif isinstance(item, Megama):
            self._validate(item['name'], self.megamas, 'megama')

        return item
