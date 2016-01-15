# -*- coding: cp1251 -*-
__author__ = 'whoami'

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CyberGhost(object):
    def __init__(self, loger, elements, result_text, url):
        super(CyberGhost, self).__init__()
        self.loger = loger
        self.elements = elements
        self.result_text = result_text
        self.plan_text = "Free"
        self.url = url
        self.response_timeout = 5
        self.max_script_run = 5
        self.page_load_timeout = 20
        self.impl_wait = 10
        self.driver = None

    def load_stop(self):
        self.driver.execute_script('window.stop();')

    def driver_stop(self):
        self.loger.store("I", "CG", "driver_stop", "Остановка драйвера")
        self.driver.close()

    def driver_start(self):
        self.loger.store("I", "CG", "driver_start", "Запуск драйвера...")

        self.fp = webdriver.FirefoxProfile()
        self.fp.set_preference("http.response.timeout", self.response_timeout)
        self.fp.set_preference("dom.max_script_run_time", self.max_script_run)
        self.driver = webdriver.Firefox(firefox_profile=self.fp)
        self.driver.set_page_load_timeout(self.page_load_timeout)
        self.driver.implicitly_wait(self.impl_wait)

    def login(self, userinfo):
        user_name, password = userinfo
        self.loger.store("I", "CG", "login", "Вход на сайт username:%s, "
                                             "password:%s" % (user_name,
                                                              password)
                         )
        self.driver.get(self.url)
        login = self.get_element(self.elements["username"])
        passwd = self.get_element(self.elements["password"])
        button = self.get_element(self.elements["btn_signin"])

        if not login or not passwd or not button:
            self.loger.store("E", "CG", "login",
                             "Не удалось получить элементы!")
            return False

        login.send_keys(user_name)
        passwd.send_keys(password)

        try:
            button.click()
        except (exceptions.TimeoutException,
                exceptions.StaleElementReferenceException):
            self.load_stop()

        if "account" not in self.driver.current_url:
            self.loger.store("E", "CG", "login", "Вход не удался!!!")
            return False
        text = None
        while True:
            text = self.get_element(self.elements["login_text"])
            user_name = user_name.upper()
            if user_name in text.text:
                break

        self.load_stop()
        self.loger.store("I", "CG", "login", "Ок логин: %s" % text.text)
        return True

    def run_check(self, key):
        self.loger.store("A", "CG", "run_check", "Чекаем ключ: %s" % key)
        if not self.__key_input_activate():
            self.loger.store("E", "CG", "run_check", "__key_input_activate() "
                                                     "вернул False!")
            return False
        if not self.__send_key(key):
            self.loger.store("E", "CG", "run_check", "__send_key(key) "
                                                     "вернул False!")
            return False
        if self.__get_alert_text():
            self.loger.store("A", "CG", "run_check",
                             "Ключ ушспешно активирован")
            return True
        else:
            self.loger.store("E", "CG", "run_check", "__get_alert_text() "
                                                     "вернул False!")
            return False

    def __key_input_activate(self):
        show_form = self.get_element(self.elements['key_input_show'])
        if show_form:
            self.loger.store("I", "CG", "__key_input_activate", "Ок")
            try:
                show_form.send_keys(Keys.RETURN)
            except exceptions.StaleElementReferenceException:
                self.driver.refresh()
                return self.__key_input_activate()
            return True
        else:
            self.loger.store("E", "CG", "__key_input_activate",
                             "Не удалось получить key_input_show")
            return False

    def __send_key(self, key):
        key_input = self.get_element(self.elements['key_input'])
        button = self.get_element(self.elements['key_send'])
        if not button or not key_input:
            self.loger.store("E", "CG", "__send_key",
                             "Не удалось получить key_input или key_send")
            return False

        key_input.clear()
        key_input.send_keys(key)

        try:
            button.click()
        except exceptions.TimeoutException:
            self.load_stop()
        self.loger.store("I", "CG", "__send_key", "Элементы получены. Ок")
        return True

    def __get_alert_text(self):
        alert_text = self.get_element(self.elements["alert_text"])
        if not alert_text:
            self.loger.store("E", "CG", "__get_alert_text",
                             "Не удалось получить alert_text")
            return False
        self.loger.store("I", "CG", "__get_alert_text",
                         "Алерт текс равен %s" % alert_text.text)

        result = self.result_text["activated"] not in alert_text.text
        if result:
            button = self.get_element(self.elements["alert_btn_ok"])
            if not button:
                result = False
                button = self.get_element(self.elements["alert_btn_cancel"])
        else:
            button = self.get_element(self.elements["alert_btn_cancel"])

        try:
            button.click()
        except exceptions.TimeoutException:
            self.load_stop()

        return result

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
