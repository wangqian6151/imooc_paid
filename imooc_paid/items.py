# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class CourseItem(Item):
    collection = table = 'course'

    category = Field()
    title = Field()
    url = Field()
    id = Field()
    level = Field()
    learners_num = Field()
    duration = Field()
    comment_num = Field()
    overall_rating = Field()
    utility_rating = Field()
    simplicity_rating = Field()
    logic_rating = Field()
    course_stat = Field()
    course_price = Field()
    img = Field()
    summary = Field()
    abstract = Field()
    description = Field()
    lecturer = Field()
    job_type = Field()
    crawl_time = Field()


class CommentItem(Item):
    collection = table = 'comment'

    course_id = Field()
    id = Field()
    username = Field()
    score = Field()
    content = Field()
    teacher_reply = Field()
    time = Field()
    crawl_time = Field()
