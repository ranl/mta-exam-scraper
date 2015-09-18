# -*- coding: utf-8 -*-
"""
This Spider will crawl the MTA public website and output the following
  - list of all the public exams
  - list of all the public exam solutions
  - list of all the lecturers
  - list of all the courses
  - list of all the megamot

How to debug this
    from scrapy.shell import inspect_response
    inspect_response(response)
"""

# Scrapy
import scrapy
from scrapy import log
from scrapy.shell import inspect_response

# mta_exam_scraper
from mta_exam_scraper.items import (
    Megama,
    Course,
    Exam,
    Solution,
    Lecturer,
)


class ExamSpider(scrapy.Spider):

    """
    The Spider Class
    """

    name = 'exam_spider'
    mta_exam_url_tmpl = 'https://{}/library/pages/examssearch.aspx/'
    event_target = '__EVENTTARGET'
    view_state = '__VIEWSTATE'
    solution_string = ur'\u05e4\u05ea\u05e8\u05d5\u05df'

    def __init__(self, mta_domain='acty.mta.ac.il', megama=None, only_list_megama=0):
        super(ExamSpider, self).__init__()
        if only_list_megama == 0:
            self.only_list_megama = False
        else:
            self.only_list_megama = True
        self.mta_domain = mta_domain
        self.allowed_domains = [self.mta_domain]
        self.mta_exam_url = self.mta_exam_url_tmpl.format(self.mta_domain)
        self.start_urls = (self.mta_exam_url,)

        if megama is None:
            self._megama = None
        elif isinstance(megama, list):
            self._megama = set(megama)
        else:
            self._megama = set([megama])

    def extract_options_gen(self, select, item):
        """
        Generator:
            - Extract the ids and name from each select
            - drop options without id or name
            - the item should have the id and name scrapy.Field()s
        """

        opts = select.xpath('.//option')
        opts.pop(0)

        for opt in opts:
            ret = item()

            # Let's see if we have data here
            try:
                ret['id'] = opt.xpath('@value').extract()[0].strip()
            except (IndexError, AttributeError):
                self.log(
                    '{0} option does not have @value {1}'.format(item, opt),
                    level=log.WARNING
                )
                continue
            else:
                if not ret['id']:
                    self.log(
                        '{0} option does not have an id {1}'.format(item, opt),
                        level=log.WARNING
                    )
                    continue

            ret['id'] = int(ret['id'])
            try:
                ret['name'] = opt.xpath('text()').extract()[0].strip()
            except (IndexError, AttributeError):
                self.log(
                    '{0} option has an id={1} but not a name {2}'.format(
                        item, ret['id'], opt
                    ),
                    level=log.ERROR
                )
                continue

            yield ret

    @classmethod
    def extract_view_state(cls, response):
        """
        Extract the annoying __VIEWSTATE hidden field
        """
        return response.xpath(
            '//input[@id="{0}"]'.format(cls.view_state)
        ).xpath('@value').extract()[0].strip()

    @staticmethod
    def get_select(response, select_num):
        """
        Get the wanted select option
        :return select_object, name attribute
        """

        select = response.xpath('//select')[select_num-1]
        event_target = select.xpath('@name').extract()[0].strip()
        return select, event_target

    def parse(self, response):
        """
        Extract all the megamas
        Yield requests to courses

        curl https://www.mta.ac.il/library/Pages/examssearch.aspx/
        """
        megama_select, megama_event_target = self.get_select(response, 1)

        for megama in self.extract_options_gen(megama_select, Megama):
            if self.only_list_megama:
                print('{}\t{}'.format(megama['id'], megama['name'].encode('utf-8')))
            else:
                if not self._megama or str(megama['id']) in self._megama:
                    request = scrapy.FormRequest(
                        self.mta_exam_url,
                        callback=self.parse_courses,
                        method='POST',
                        formdata={
                            self.view_state: self.extract_view_state(response),
                            megama_event_target: str(megama['id']),
                            self.event_target: megama_event_target,
                        },
                    )
                    request.meta['megama'] = megama
                    request.meta['megama_event_target'] = megama_event_target
                    yield megama
                    yield request
                else:
                    self.log(
                        'excluding megama={0}'.format(megama['id']),
                        level=log.WARNING
                    )

    def parse_courses(self, response):
        """
        Extract all the courses
        Yield requests to exams

        curl
            -F 'ctl00$m$g_b314a3a2_2141_4507_96a3_0c3891efb805$Trend=50000117'
            -F '__EVENTTARGET=ctl00$m$g_b314a3a2_2141_4507_96a3_0c3891efb805$Trend'
            https://www.mta.ac.il/library/Pages/examssearch.aspx/
        """

        course_select, course_event_target = self.get_select(response, 2)
        for course in self.extract_options_gen(course_select, Course):
            course['megama'] = response.meta['megama']['id']
            request = scrapy.FormRequest(
                self.mta_exam_url,
                callback=self.parse_exam,
                method='POST',
                formdata={
                    self.view_state: self.extract_view_state(response),
                    course_event_target: str(course['id']),
                    self.event_target: course_event_target,
                    response.meta['megama_event_target']: str(response.meta['megama']['id']),
                },
            )
            request.meta['course'] = course

            # Yield
            yield request

    def parse_exam(self, response):
        """
        Yield all the exams & lecturers

        curl
            -F 'ctl00$m$g_b314a3a2_2141_4507_96a3_0c3891efb805$Trend=50000118'
            -F 'ctl00$m$g_b314a3a2_2141_4507_96a3_0c3891efb805$Course=50000416'
            -F '__EVENTTARGET=ctl00$m$g_b314a3a2_2141_4507_96a3_0c3891efb805$Course'
            -F '__VIEWSTATE=WHATEVER_THAT_WAS_THERE'
            https://www.mta.ac.il/library/Pages/examssearch.aspx/
        """

        trs = response.xpath('//table[@id="calendar"]//tr')

        try:
            trs.pop(0)
        except IndexError:
            self.log(
                'course {0} in megama {1} has wierd exam table,'
                'if this happens fequently something is wrong'.format(
                    response.meta['course']['id'],
                    response.meta['course']['megama'],
                ),
                level=log.ERROR,
            )
            return

        if len(trs[0].xpath('.//td')) == 1:
            self.log(
                'course {0} in megama {1} does not have any exams'.format(
                    response.meta['course']['id'],
                    response.meta['course']['megama'],
                ),
                level=log.WARNING,
            )
            return

        yield response.meta['course']

        for tr in trs:
            tds = tr.xpath('.//td')
            course, year, semester, moed, lecturer_td = tds

            # Lecturer
            lecturer = Lecturer()
            try:
                lecturer['name'] = lecturer_td.xpath('text()').extract()[0].strip()
            except (IndexError, AttributeError):
                self.log(
                    'could not determine the lecturer of the exam {0}'.format(tr),
                    level=log.ERROR
                )
                lecturer['name'] = 'NULL'
            else:
                lecturer['course'] = response.meta['course']['id']
                lecturer['megama'] = response.meta['course']['megama']
                yield lecturer

            # Get the link to the exam
            # Determine if this is solution
            link = 'NULL'
            is_solution = False
            for a in course.xpath('.//a'):
                link_elem = a.xpath('@href')
                link = link_elem.extract()[0].strip()
                if link:
                    if a.xpath('text()').extract()[0].strip() == self.solution_string:
                        is_solution = True
                    break
            else:
                self.log('could not find the link of exam {0}'.format(tr))

            # Create the Exam / Solution
            if is_solution:
                exam = Solution()
            else:
                exam = Exam()

            exam['course'] = response.meta['course']['id']
            exam['megama'] = response.meta['course']['megama']
            exam['lecturer'] = lecturer['name']
            exam['year'] = year.xpath('text()').extract()[0].strip().replace('"', '')
            exam['semester'] = semester.xpath('text()').extract()[0].strip()
            exam['moed'] = moed.xpath('text()').extract()[0].strip()
            exam['link'] = link

            yield exam
