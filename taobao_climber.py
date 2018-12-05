# -*- coding: utf-8 -*-
from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import os
from PIL import Image
import requests
from selenium.webdriver.chrome.options import Options


class TaobaoClimber:
    def __init__(self):
        self.__session = requests.Session()

    driver = None
    action = None

    # 是否登录
    __is_logined = False

    # 登陆URL
    __login_url = "https://login.taobao.com/member/login.jhtml"

    def login(self):
        # 1.登陆
        try:
            self.driver.get(self.__login_url)
        except exceptions.TimeoutException:  # 当页面加载时间超过设定时间，JS来停止加载
            self.driver.execute_script('window.stop()')

        self.__login_one()


        # 2.保存cookies
        # driver.switch_to_default_content() #需要返回主页面，不然获取的cookies不是登陆后cookies
        list_cookies = self.driver.get_cookies()
        #cookies = {}
        #for s in list_cookies:
        #    cookies[s['name']] = s['value']
         #   requests.utils.add_dict_to_cookiejar(self.__session.cookies, cookies)  # 将获取的cookies设置到session
        return list_cookies


    def __login_one(self):

        #htmlElem = self.driver.find_element_by_tag_name('html')
        #for i in range(15):
        #    htmlElem.send_keys(Keys.RIGHT)

        
        username_login_btn = self.driver.find_element_by_xpath("//a[@class='forget-pwd J_Quick2Static']")
        if username_login_btn.is_displayed() is False:
            username_login_btn.click()
        time.sleep(2)

        self.driver.get_screenshot_as_file('screenshot.png') # 截图

        # 通过find_element_by_xpath获取图片元素
        imgelement = self.driver.find_element_by_xpath('//*[@id="J_QRCodeImg"]/img')

        # 通过图片元素获取图片大小及位置
        left = imgelement.location['x']
        top = imgelement.location['y']
        right = imgelement.location['x'] + imgelement.size['width']
        bottom = imgelement.location['y'] + imgelement.size['height']

        #left = 1320
        #top = 360
        #right = 1490
        #bottom = 540

        im = Image.open('screenshot.png')
        #print(im.size)
        im = im.crop((left, top, right, bottom))
        #print((left, top, right, bottom))
        im.save('img.png') # 保存我们接下来的验证码图片 进行打码

        os.startfile("img.png")
        input("扫描后按回车")
        print("正在登录...")
        time.sleep(5)
        


def login_run():
    # 初始化
    options = Options()
    options.add_argument('-headless')  # 无头参数 
    options.add_argument('log-level=3')
    #TaobaoClimber.driver = webdriver.PhantomJS()#chrome_options=options)  # 应将浏览器驱动放于python根目录下，且python已配置path环境变量
    TaobaoClimber.driver = webdriver.Chrome(chrome_options=options)  # 应将浏览器驱动放于python根目录下，且python已配置path环境变量
    #TaobaoClimber.driver.maximize_window()  # 浏览器最大化
    TaobaoClimber.driver.set_window_size(1920,1080)
    TaobaoClimber.action = ActionChains(TaobaoClimber.driver)
    TaobaoClimber.driver.execute_script("window.open('')")

    climber = TaobaoClimber()
    cookie = climber.login()

    return cookie
