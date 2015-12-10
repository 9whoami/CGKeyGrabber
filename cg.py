# -*- coding: cp1251 -*-
__author__ = 'whoami'

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CyberGhost(object):
    def __init__(self, user, loger, elements, result_text, plan_text, url):
        super(CyberGhost, self).__init__()
        self.loger = loger
        self.elements = elements
        self.result_text = result_text
        self.plan_text = plan_text
        self.url = url
        self.user_name, self.user_passwd = user
        self.response_timeout = 5
        self.max_script_run = 5
        self.page_load_timeout = 20
        self.impl_wait = 10
        fp = webdriver.FirefoxProfile()

        fp.set_preference("http.response.timeout", self.response_timeout)
        fp.set_preference("dom.max_script_run_time", self.max_script_run)
        self.driver = webdriver.Firefox(firefox_profile = fp)
        self.driver.set_page_load_timeout(self.page_load_timeout)
        self.driver.implicitly_wait(self.impl_wait)

    def load_stop(self):
        self.driver.execute_script('window.stop();')

    def login(self):
        self.loger.store("I", "CG::login", "Sign in username:%s, password:%s"
                         % (self.user_name, self.user_passwd))
        self.driver.get(self.url)
        try:
            login = self.get_element(self.elements["login"])
            passwd = self.get_element(self.elements["passwd"])
            button = self.get_element(self.elements["button_login"])
        except Exception as e:
            self.loger.store("E", "CG::login", e)
            return False

        login.send_keys(self.user_name)
        passwd.send_keys(self.user_passwd)
        try:
            button.click()
        except exceptions.TimeoutException:
            self.load_stop()
        self.__load_end('Management')
        text = self.get_element(self.elements["check_login"])
        user_name = self.user_name.upper()
        if user_name in text.text:
            self.loger.store("I", "CG::login", "OK")
            self.load_stop()
            self.__key_input_activate()
            return True
        else:
            self.loger.store("I", "CG::login", text.text)
            return False

    def run_check(self, key):
        self.loger.store("I", "CG::run_check", "Start key checking KEY:%s"
                         % key)
        # try:
        #     self.driver.refresh()
        # except exceptions.TimeoutException:
        #     self.load_stop()
        # self.__key_input_activate()
        self.__send_key(key)
        return self.__get_alert_text()

    def __key_input_activate(self):
        try:
            show_form = self.get_element(self.elements['show_keys_form'])
            show_form.send_keys(Keys.RETURN)
        except Exception as e:
            self.loger.store("E", "CG::key_input_activate", e)
            return False
        else:
            self.loger.store("E", "CG::key_input_activate", "OK")
            return True

    def __send_key(self, key):
        try:
            key_input = self.get_element(self.elements['input_key'])
            button = self.get_element(self.elements['button_key'])
        except Exception as e:
            self.loger.store("E", "CG::check_key", e)
            return
        else:
            self.loger.store("E", "CG::check_key", "OK")

        key_input.clear()
        key_input.send_keys(key)

        try:
            button.click()
        except exceptions.TimeoutException:
            self.driver.execute_script('window.stop();')

    def __get_alert_text(self):
        try:
            text = self.get_element(self.elements["alert_text"]).text
            self.loger.store("I", "CG::get_alert_text", text)

            if self.result_text["not_found"] in text or self.result_text["activated"] in text:
                button = self.get_element(self.elements["alert_button"])
            else:
                button = self.get_element(self.elements["activation_button"])
            button.click()
            sleep(3)
            plan = self.get_element(self.elements["plan_text"]).text
            self.loger.store("A", "CG::get_alert_text", plan)
            return self.plan_text not in plan
        except Exception as e:
            self.loger.store("E", "CG", e)
            return False
        else:
            self.loger.store("I", "CG::get_alert_text", "OK")

    def __load_end(self, msg):
        while not (msg in self.driver.title):
            pass
        return True

    def get_element(self, xpath):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
        except exceptions.TimeoutException:
            return None

    def __del__(self):
        self.driver.close()