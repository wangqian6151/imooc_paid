# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
import scrapy
from scrapy import Request
from scrapy.linkextractors import LinkExtractor

from imooc_paid.items import CourseItem, CommentItem


class ImoocPaySpider(scrapy.Spider):
    name = 'imooc_pay'
    allowed_domains = ['coding.imooc.com']
    start_urls = ['http://coding.imooc.com/']

    def parse(self, response):
        le = LinkExtractor(restrict_xpaths='//div[@class="shizhan-header-nav"]/div/a')
        for link in le.extract_links(response)[1:]:
            print(link.url, link.text)
            yield Request(link.url, callback=self.parse_course, meta={'category': link.text})

    def parse_course(self, response):
        category = response.meta.get('category')
        course_list = response.xpath('//div[@class="index-list-wrap"]/div/div')
        for c in course_list:
            course_item = CourseItem()
            course_item['category'] = category
            course_item['title'] = c.xpath('.//p[@class="shizan-name"]/@title').extract_first()
            course_stat = c.css('.course-stat::text').extract_first()
            course_item['course_stat'] = course_stat.strip() if course_stat else course_stat
            course_item['url'] = response.urljoin(c.xpath('./a/@href').extract_first())
            course_item['id'] = c.xpath('./a/@href').re_first(r'[1-9]\d*|0')
            course_item['level'] = c.css('.grade::text').extract_first()
            course_item['learners_num'] = c.css('.grade + span::text').extract_first()
            # course_item['comment_num'] = c.xpath('.//div[@class="shizhan-info"]/span[3]/text()').re_first(r'[1-9]\d*|0')
            learners_num = c.css('.r::text').re_first(r'[1-9]\d*|0')
            course_item['comment_num'] = learners_num if learners_num else 0
            course_item['summary'] = c.css('.shizan-desc::text').extract_first()
            course_price = c.css('.course-card-price::text').extract_first()
            discount_price = c.css('.discount-price::text').extract_first()
            course_item['course_price'] = course_price.strip('￥') if course_price else discount_price.strip('￥')
            course_item['img'] = response.urljoin(c.css('.img-box img::attr(src)').extract_first())
            course_item['lecturer'] = c.css('.lecturer-info img::attr(alt)').extract_first()
            course_item['overall_rating'] = c.css('.big-text::text').extract_first()
            course_item['utility_rating'] = c.xpath('.//div[@class="right-box l"]/p[1]/span/text()').extract_first()
            course_item['simplicity_rating'] = c.xpath('.//div[@class="right-box l"]/p[2]/span/text()').extract_first()
            course_item['logic_rating'] = c.xpath('.//div[@class="right-box l"]/p[3]/span/text()').extract_first()
            '''
            以下是css方式
            course_item['utility_rating'] = c.css('.right-box p:nth-child(1) span::text').extract_first()
            course_item['simplicity_rating'] = c.css('.right-box p:nth-child(2) span::text').extract_first()
            course_item['logic_rating'] = c.css('.right-box p:nth-child(3) span::text').extract_first()
            '''
            yield Request(course_item['url'], callback=self.parse_course_detail, meta={'course_item': course_item})

        if response.xpath('.//div[@class="page"]/a[last()-1]/text()').extract_first() == '下一页':
            le = LinkExtractor(restrict_xpaths='//*[@class="page"]/a[last()-1]')
            link = le.extract_links(response)
            if link:
                next_url = link[0].url
                print('next_course_url:{}'.format(next_url))
                self.logger.debug('next_course_url:{}'.format(next_url))
                yield Request(next_url, callback=self.parse_course)


    def parse_course_detail(self, response):
        course_item = response.meta.get('course_item')
        print('parse_course course_item:{}'.format(course_item))
        self.logger.debug('parse_course course_item:{}'.format(course_item))
        course_item['abstract'] = response.css('.title-box h2::text').extract_first()
        course_item['duration'] = response.xpath('.//div[@class="info-bar clearfix"]/span[4]/text()').extract_first()
        course_item['job_type'] = response.css('.teacher > p::text').extract_first()
        course_item['description'] = response.css('.info-desc::text').extract_first()
        course_item['crawl_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield course_item

        comment_url = response.css('.comp-tab-t > ul > li:nth-child(5) a::attr(href)').extract_first()
        print('comment_url11111', comment_url)
        self.logger.debug('comment_url11111', comment_url)
        if comment_url:
            comment_url = response.urljoin(comment_url)
            print('comment_url22222', comment_url)
            self.logger.debug('comment_url22222 {}'.format(comment_url))
            yield Request(comment_url, callback=self.parse_comment)

    def parse_comment(self, response):
        comment_list = response.css('.cmt-list li')
        for c in comment_list:
            comment_item = CommentItem()
            comment_item['course_id'] = re.findall(r"\d+\.?\d*", response.url)[0]
            comment_item['id'] = c.xpath('@data-commentid').extract_first()
            comment_item['username'] = c.css('.name::text').extract_first()
            comment_item['score'] = c.css('.stars span::text').extract_first()
            comment_item['content'] = c.css('.cmt-txt::text').extract_first()
            comment_item['teacher_reply'] = c.css('.js-reply-value::text').extract_first()
            time = c.css('.post-date::text').extract_first()
            if time and '天前' in time:
                day = int(re.findall(r'[1-9]\d*|0', time)[0])
                comment_item['time'] = (datetime.now() + timedelta(days=-day)).strftime("%Y-%m-%d %H:%M:%S")
            elif time and '小时前' in time:
                hour = int(re.findall(r'[1-9]\d*|0', time)[0])
                comment_item['time'] = (datetime.now() + timedelta(hours=-hour)).strftime("%Y-%m-%d %H:%M:%S")
            elif time and time.startswith('201'):
                comment_item['time'] = time
            else:
                comment_item['time'] = None
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # comment_item['time'] = time if time and time.startswith('201') else current_time
            comment_item['crawl_time'] = current_time
            yield comment_item
        if response.xpath('.//div[@class="page"]/a[last()-1]/text()').extract_first() == '下一页':
            le = LinkExtractor(restrict_xpaths='//*[@class="page"]/a[last()-1]')
            link = le.extract_links(response)
            if link:
                next_url = link[0].url
                print('next_comment_url:{}'.format(next_url))
                self.logger.debug('next_comment_url:{}'.format(next_url))
                yield Request(next_url, callback=self.parse_comment)



