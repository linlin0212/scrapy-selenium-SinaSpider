# -*- coding: utf-8 -*-
import scrapy
from scrapy_weibo.items import  WeiboItem
from scrapy.http import Request
import time
class WeibospiderSpider(scrapy.Spider):
    name = "WeiboSpider"
    start_urls = ['http://my.sina.com.cn/profile/unlogin']
    page_num=0
    weibo_num=0

    def parse(self, response):
        self.page_num = self.page_num + 1
        print('开始爬取第{}页'.format(self.page_num))
        # print('parse response+',response)
        weibo_hrefs = response.xpath(
            "//div[@class='content clearfix']/div[@class='feed_from W_textb']/a[@class='W_textb']/@href").extract()
        next_url = response.xpath("//div[@class='W_pages']/a[@class='page next S_txt1 S_line1']/@href").extract()
        for weibo_href in weibo_hrefs:
            self.weibo_num = self.weibo_num + 1
            weibo_href = 'https:' + weibo_href
            print('开始爬取第{}个微博'.format(self.weibo_num))
            time.sleep(4)
            yield Request(weibo_href, callback=self.parse_weibo)
        print('本页微博数为{}'.format(len(weibo_hrefs)))
        # 如果页面有下一页
        if  len(next_url)!=0:
            next_url='https://s.weibo.com/'+next_url[0]
            # print('next_url+',next_url)
            time.sleep(1)
            yield Request(next_url,callback=self.parse)
    def parse_weibo(self, response):
        # 爬取微博和评论
        # print('parse_next response+', response)
        try:
            weibo_item = WeiboItem()
            weibo_text = response.xpath("//div[@class='WB_text W_f14']/text()").extract()
            weibo_id = response.xpath("//div[@action-type='feed_list_item']/@mid").extract()
            weibo_time = response.xpath(
                "//div[@class='WB_detail']/div[@class='WB_from S_txt2']/a[@node-type='feed_list_item_date']/text()").extract()
            weibo_publisher = response.xpath("//a[@class='W_f14 W_fb S_txt1']/text()").extract()
            fw_num = response.xpath("//span[@node-type='forward_btn_text']/span/em[2]/text()").extract()
            re_num = response.xpath("//span[@node-type='comment_btn_text']/span/em[2]/text()").extract()
            like_num = response.xpath("//span[@class='pos']/span/span[@node-type='like_status']/em[2]/text()").extract()
            ## 去除博文中的\n、空格和： 并将其转化为字符串形式
            weibo_text="".join(weibo_text).strip("\n").strip(" ")
            weibo_id=''.join(weibo_id)
            weibo_time="".join(weibo_time)
            weibo_publisher="".join(weibo_publisher)
            fw_num ="".join(fw_num)
            re_num ="".join(re_num)
            like_num="".join(like_num)
            # 有的微博没有转发、评论和赞，就会显示“转发、评论或赞”的字样，数目置为0
            if fw_num == '转发':
                fw_num = 0
            if re_num == '评论':
                re_num = 0
            if like_num == '赞':
                like_num = 0
            fw_num=int(fw_num)
            re_num=int(re_num)
            like_num=int(like_num)
            weibo_item['fw_num'] = fw_num
            weibo_item['re_num'] = re_num
            weibo_item['like_num'] = like_num
            weibo_item['weibo_id'] = weibo_id
            weibo_item['weibo_text'] = weibo_text
            weibo_item['weibo_publisher'] = weibo_publisher
            weibo_item['weibo_time'] = weibo_time
            comments = []
            #如果评论数不为0，爬取评论
            if re_num != 0:
                global comment_count
                comment_count = 0
                comment_reviewers=response.xpath(
                    "//div[@class='list_con']/div[@class='WB_text']/a[1]/text()").extract()
                comment_times=response.xpath(
                    "//div[@class='list_con']/div[@class='WB_func clearfix']/div[@class='WB_from S_txt2']/text()").extract()
                comment_texts=response.xpath(
                    "//div[@class='list_con']/div[@class='WB_text']")

                for i in range(0,len(comment_reviewers)):
                    comment = {}
                    # 去除评论中的\n、空格和：
                    comment_text=comment_texts[i].xpath("text()").extract()
                    comment_text = ''.join(comment_text).strip("\n").strip(' ').strip("：")
                    comment_reviewer = ''.join(comment_reviewers[i])
                    comment_time = ''.join(comment_times[i])
                    comment['comment_reviewer'] = comment_reviewer
                    comment['comment_time'] = comment_time
                    comment['comment_text'] = comment_text
                    comments.append(comment)
                    comment_count = comment_count + 1
                    print("已经爬取{}条评论".format(comment_count))
                    time.sleep(1)
            weibo_item['comments'] = comments
            yield weibo_item
        except Exception as e :
                print("爬去过程中出现错误",e)






