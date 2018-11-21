# -*- coding: utf-8 -*-
# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy import signals
import random
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
from scrapy_weibo.settings import USER_AGENT
class RandomUserAgent(object):
    #建立用户代理
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    # def from_crawler(cls,crawler):
    #     # 从settings中加载USER_AGENT的值
    #     return cls(
    #         user_agent=crawler.settings.getlist('USER_AGENT')
    #     )

    def process_request(self, request, spider):
        # 在process_request中设置User-Agent的值
        ua = random.choice(USER_AGENT)
        if ua:
            # 显示当前使用的useragent
            # print "********Current UserAgent:%s************" %ua
            # 记录
            # logging.log(logging.INFO,'Current UserAgent: ' + ua)
            request.headers.setdefault('User-Agent', ua)

class RandomProxy(object):
    #建立IP代理
    def __init__(self, iplist=''):
        self.iplist = iplist

    # def from_crawler(cls,crawler):
    #     # 在settings中加载IPLIST的值
    #     return cls(
    #         iplist=crawler.settings.getlist('IPLIST')
    #     )
    def process_request(self, request, spider):
        # 在请求上添加代理
        proxy = self.get_random_proxy()
        if proxy:
            # logging.log(logging.INFO,'Current IP: '+ proxy)
            request.meta['proxy'] = proxy

    def process_response(self, request, response, spider):
        '''对返回的response处理'''
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            proxy = self.get_random_proxy()
            print("this is response ip:" + proxy)
            # 对当前reque加上代理
            request.meta['proxy'] = proxy
            return request
        return response

    def get_random_proxy(self):
        '''随机从文件中读取proxy'''
        while 1:
            with open('D:\\PyScrapyWeibo\\scrapy_weibo\\proxies.txt', 'r') as f:
                proxies = f.readlines()
            if proxies:
                break
            else:
                time.sleep(1)
        proxy = random.choice(proxies).strip()
        return proxy

class SeleniumMiddlewares(object):
    def __init__(self):
        self.chrome_opt = webdriver.ChromeOptions()
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "plugins.plugins_disabled": ['Chrome PDF Viewer'],
            "plugins.plugins_disabled": ['Adobe Flash Player'],
                 }
        self.chrome_opt.add_experimental_option("prefs", prefs)
    def process_request(self, request, spider):
        login_url='http://my.sina.com.cn/profile/unlogin'
        #如果request是login_url
        if request.url==login_url:
            self.driver = webdriver.Chrome(executable_path='D:\ChromeDriver\chromedriver.exe', options=self.chrome_opt)
            self.driver.get(login_url)
            self.driver.implicitly_wait(5)
            self.driver.find_element_by_id("hd_login").click()
            self.driver.find_element_by_name("loginname").send_keys('ddpecv')
            self.driver.find_element_by_name("password").send_keys('qazwsx852')
            self.driver.find_element_by_class_name("login_btn").click()
            try:
                # 输入验证码
                time.sleep(10)
                self.driver.find_element_by_class_name("login_btn").click()
            except:
                # 不用输验证码，忽略
                pass
            self.driver.find_element_by_id("search_input").send_keys('小凤雅')
            self.driver.find_element_by_id("search_submit").click()
            print('Login successfully!')
            # 获取当前页句柄,定位新标签页
            num = self.driver.window_handles
            print(num)
            self.driver.switch_to.window(num[1])
            time.sleep(15)
            page=self.driver.page_source
            return HtmlResponse(self.driver.current_url, body=page, encoding='utf-8', request=request)
        #如果request页面是page1/2/3的形式
        elif "page" in request.url:

            self.driver.get(request.url)
            num = self.driver.window_handles
            print(num)
            self.driver.switch_to.window(num[1])
            time.sleep(5)
            next_page = self.driver.page_source
            return HtmlResponse(self.driver.current_url, body=next_page, encoding='utf-8', request=request)
        #对微博页的处理
        else:
            self.driver.get(request.url)
            time.sleep(5)
            #不管有没有评论数，下拉三次，出现网页底部状况
            for i in range(3):
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
                time.sleep(3)
            time.sleep(3)
           #底部网页结构的三种情况
            try:

                more_click = self.driver.find_element_by_xpath(
                    "//div[@class='WB_repeat S_line1']/div[@class='repeat_list']/div[2]/div[@class='list_box']/div[@class='list_ul']/a")
                next_page = self.driver.find_element_by_xpath(
                    "//div[@class='WB_cardpage S_line1']/div[@class='W_pages']/a[@class='page next S_txt1 S_line1']")
                # 底部有“查看更多”的按钮，所有点击完毕后返回
                if more_click!=0:
                    while( more_click!=0):
                        more_click.click()
                        time.sleep(3)
                        more_click = self.driver.find_element_by_xpath(
                            "//div[@class='WB_repeat S_line1']/div[@class='repeat_list']/div[2]/div[@class='list_box']/div[@class='list_ul']/a")


                    #一级评论全部加载完，查看是否有二级评论
                    v2_click=self.driver.find_elements_by_xpath(
                            "//div[@class='WB_repeat S_line1']/div[@class='repeat_list']/div[2]/div[@class='list_box']/div[@class='list_ul']/div[@class ='list_li S_line1 clearfix']/div[@class='list_con']/div[@class='list_box_in S_bg3']/div[@node-type='child_comment']/div[@class='list_li_v2']/div[@class='WB_text']/a[@action-type='click_more_child_comment_big']")

                    if (len(v2_click)!=0):
                        while(len(v2_click)!=0):
                            for v2 in v2_click:

                                ActionChains(self.driver).move_to_element(v2).click().perform()
                                time.sleep(3)
                            v2_click = self.driver.find_elements_by_xpath(
                                "//div[@class='WB_repeat S_line1']/div[@class='repeat_list']/div[2]/div[@class='list_box']/div[@class='list_ul']/div[@class ='list_li S_line1 clearfix']/div[@class='list_con']/div[@class='list_box_in S_bg3']/div[@node-type='child_comment']/div[@class='list_li_v2']/div[@class='WB_text']/a[@action-type='click_more_child_comment_big']")
                    weibo_page = self.driver.page_source
                    return HtmlResponse(self.driver.current_url, body=weibo_page, encoding='utf-8', request=request)

#翻页评论的处理有问题！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
                # 底部有翻页按钮，每页都要返回
                if next_page!=0:


                    #一级评论全部加载完，查看是否有二级评论
                    v2_click=self.driver.find_elements_by_xpath(
                            "//div[@class='WB_repeat S_line1']/div[@class='repeat_list']/div[2]/div[@class='list_box']/div[@class='list_ul']/div[@class ='list_li S_line1 clearfix']/div[@class='list_con']/div[@class='list_box_in S_bg3']/div[@node-type='child_comment']/div[@class='list_li_v2']/div[@class='WB_text']/a[@action-type='click_more_child_comment_big']")

                    if (len(v2_click)!=0):
                        while(len(v2_click)!=0):
                            for v2 in v2_click:
                                ActionChains(self.driver).move_to_element(v2).click().perform()
                                time.sleep(3)
                            v2_click = self.driver.find_elements_by_xpath(
                                "//div[@class='WB_repeat S_line1']/div[@class='repeat_list']/div[2]/div[@class='list_box']/div[@class='list_ul']/div[@class ='list_li S_line1 clearfix']/div[@class='list_con']/div[@class='list_box_in S_bg3']/div[@node-type='child_comment']/div[@class='list_li_v2']/div[@class='WB_text']/a[@action-type='click_more_child_comment_big']")


                    weibo_page = self.driver.page_source
                    return HtmlResponse(self.driver.current_url, body=weibo_page, encoding='utf-8', request=request)
                    while(next_page!=0):
                        #先将本页的网页返回，爬取评论
                        #点击下一页按钮
                        next_page.click()
                        time.sleep(3)
                        next_page = self.driver.find_element_by_xpath(
                            "//div[@class='WB_cardpage S_line1']/div[@class='W_pages']/a[@class='page next S_txt1 S_line1']")

                        # 一级评论全部加载完，查看是否有二级评论
                        v2_click = self.driver.find_elements_by_xpath(
                            "//div[@class='WB_repeat S_line1']/div[@class='repeat_list']/div[2]/div[@class='list_box']/div[@class='list_ul']/div[@class ='list_li S_line1 clearfix']/div[@class='list_con']/div[@class='list_box_in S_bg3']/div[@node-type='child_comment']/div[@class='list_li_v2']/div[@class='WB_text']/a[@action-type='click_more_child_comment_big']")
                        if (len(v2_click)!= 0):
                            while (len(v2_click) != 0):
                                for v2 in v2_click:
                                    ActionChains(self.driver).move_to_element(v2).click().perform()
                                    time.sleep(3)
                                v2_click = self.driver.find_elements_by_xpath(
                                    "//div[@class='WB_repeat S_line1']/div[@class='repeat_list']/div[2]/div[@class='list_box']/div[@class='list_ul']/div[@class ='list_li S_line1 clearfix']/div[@class='list_con']/div[@class='list_box_in S_bg3']/div[@node-type='child_comment']/div[@class='list_li_v2']/div[@class='WB_text']/a[@action-type='click_more_child_comment_big']")

                        weibo_page = self.driver.page_source
                        return HtmlResponse(self.driver.current_url, body=weibo_page, encoding='utf-8', request=request)
                #没有评论或者底部评论直接加载完
                if (next_page==0 and more_click==0):
                    #查看是否有二级评论
                    v2_click=self.driver.find_elements_by_xpath(
                            "//div[@class='WB_repeat S_line1']/div[@class='repeat_list']/div[2]/div[@class='list_box']/div[@class='list_ul']/div[@class ='list_li S_line1 clearfix']/div[@class='list_con']/div[@class='list_box_in S_bg3']/div[@node-type='child_comment']/div[@class='list_li_v2']/div[@class='WB_text']/a[@action-type='click_more_child_comment_big']")
                    if (len(v2_click)!=0):
                        while(len(v2_click)!=0):
                            for v2 in v2_click:
                                ActionChains(self.driver).move_to_element(v2).click().perform()
                                time.sleep(3)
                            v2_click = self.driver.find_elements_by_xpath(
                                "//div[@class='WB_repeat S_line1']/div[@class='repeat_list']/div[2]/div[@class='list_box']/div[@class='list_ul']/div[@class ='list_li S_line1 clearfix']/div[@class='list_con']/div[@class='list_box_in S_bg3']/div[@node-type='child_comment']/div[@class='list_li_v2']/div[@class='WB_text']/a[@action-type='click_more_child_comment_big']")

                    weibo_page = self.driver.page_source
                    return HtmlResponse(self.driver.current_url, body=weibo_page, encoding='utf-8', request=request)
            except Exception as e :
                print("寻找元素出错",e)







# class ScrapyWeiboSpiderMiddleware(object):
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the spider middleware does not modify the
#     # passed objects.
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_spider_input(response, spider):
#         # Called for each response that goes through the spider
#         # middleware and into the spider.
#
#         # Should return None or raise an exception.
#         return None
#
#     def process_spider_output(response, result, spider):
#         # Called with the results returned from the Spider, after
#         # it has processed the response.
#
#         # Must return an iterable of Request, dict or Item objects.
#         for i in result:
#             yield i
#
#     def process_spider_exception(response, exception, spider):
#         # Called when a spider or process_spider_input() method
#         # (from other spider middleware) raises an exception.
#
#         # Should return either None or an iterable of Response, dict
#         # or Item objects.
#         pass
#
#     def process_start_requests(start_requests, spider):
#         # Called with the start requests of the spider, and works
#         # similarly to the process_spider_output() method, except
#         # that it doesn’t have a response associated.
#
#         # Must return only requests (not items).
#         for r in start_requests:
#             yield r
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)
