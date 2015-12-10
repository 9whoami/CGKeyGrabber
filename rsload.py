# -*- coding: cp1251 -*-
__author__ = 'whoami'

import re
from os import path
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions


class RsLoad(object):
    def __init__(self, user, url, page, headers, xpath, loger, history):
        super(RsLoad, self).__init__()
        self.loger = loger
        self.keys = []
        self.history = history
        self.login, self.passwd = user
        self.url = url
        self.cur_page = page
        self.headers = headers
        self.xpath = xpath
        dcap = dict(DesiredCapabilities.PHANTOMJS).copy()
        dcap["phantomjs.page."\
                  "settings.userAgent"] = ("Mozilla/5.0 (Windows NT "
                                           "6.1; WOW64; rv:41.0) "
                                           "Gecko/20100101 Firefox/41.0")
        dcap["browserName"] = ("Mozilla Firefox")
        self.driver = webdriver.PhantomJS(executable_path="phantomjs.exe",
                                          service_log_path=path.devnull,
                                          desired_capabilities=dcap
                                          )
        self.driver.set_window_size(1120, 550)  # optional

    def max_page(self):
        result = self.get_element(self.xpath["max_page"])
        if not result:
            return None
        result = result.text
        pattern = "[0-9]+"
        max_page = re.findall(pattern, result)
        self.loger.store("I", "RSLOAD", "max_page: Page count: %s" % max_page[0])
        return max_page[0]

    def rw_file(self, data=None):
        try:
            if data:
                with open(self.history, 'a') as f:
                    for index in data:
                        f.write(index + '\n')
            else:
                with open(self.history, 'r') as f:
                    data = [line.strip() for line in f]
            return data
        except Exception as e:
            self.loger.store("E", "RSLOAD", "rw_file: %s" % e)
        else:
            self.loger.store("I", "RSLOAD", "rw_file: OK")

    def get_all_keys(self):
        old_keys = self.rw_file()
        pattern = r"([A-Z0-9])+-([A-Z0-9])+-([A-Z0-9])+-([A-Z0-9])+-([A-Z0-9])+-([A-Z0-9])+"
        try:
            source = self.driver.page_source
            keys_list = re.finditer(pattern, source, re.MULTILINE)
            new_keys = []

            for key in keys_list:
                key = key.group()
                if not key in old_keys:
                    new_keys.append(key)

            self.loger.store("A", "RSLOAD", "get_all_keys: Найдено %d новых ключей: %s" % (len(new_keys), new_keys))

            if new_keys:
                self.rw_file(new_keys)
                return new_keys
            else:
                return None
        except Exception as e:
            self.loger.store("A", "RSLOAD", "get_all_keys: %s" % e)
            return None

    def is_login(self):
        try:
            result = self.get_element(self.xpath["is_login"])
            result = result.text
            self.loger.store("A", "RSLOAD", "is_login: OK %s" % result)
            return self.login in result
        except Exception as e:
            self.loger.store("E", "RSLOAD", "is_login: %s" % e)
            return False

    def update(self):
        self.driver.get(self.url % (self.cur_page))
        max_page = int(self.max_page())
        if self.cur_page != max_page:
            self.driver.get(self.url % (max_page))
            self.cur_page = max_page
        return self.is_login()

    def signin(self):
        self.driver.get(self.url % self.cur_page)
        login = self.get_element(self.xpath["input_login"])
        passwd = self.get_element(self.xpath["input_passwd"])
        btn = self.get_element(self.xpath["btn"])

        self.loger.store("I", "RSLOAD", "signin")
        if login and passwd and btn:
            login.send_keys(self.login)
            passwd.send_keys(self.passwd)
            btn.click()
            return self.is_login()
        else:
            self.loger.store("A", "RSLOAD", "signin")
            return False

    def get_element(self, xpath):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
        except exceptions.TimeoutException:
            return None