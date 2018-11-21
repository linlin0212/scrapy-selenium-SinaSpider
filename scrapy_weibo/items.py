# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
# class WeiboCommentsItem(scrapy.Item):
#     weibo_id = scrapy.Field()
#     comment_text=scrapy.Field()
#     comment_time=scrapy.Field()
#     comment_reviewer=scrapy.Field()
class WeiboItem(scrapy.Item):
    weibo_id=scrapy.Field()
    weibo_text=scrapy.Field()
    weibo_time=scrapy.Field()
    weibo_publisher=scrapy.Field()
    fw_num=scrapy.Field()
    re_num=scrapy.Field()
    like_num=scrapy.Field()
    comments=scrapy.Field()




