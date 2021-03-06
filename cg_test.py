# -*- coding: cp1251 -*-
__author__ = 'whoami'
__version__ = '0.0.0 Alpha'

from threading import Thread
from sys import exit
from time import sleep
from cg import *
from rsload import *
from logger import *

rs_user = ("wiom", "ghbphfr1",)

files = dict(
    out="out.txt",
    story="history.txt",
    users="users.txt"
)
interval = 10
cur_page = 95
urls = dict(
    cyber="https://account.cyberghostvpn.com/en_us/login",
    rs_load="http://forum.rsload.net/cat-kryaki-seriyniki-varez/topic-4820-page-%d.html"
)

elements = dict(
    cg=dict(
        username=".//*[@id='loginForm']/div/input[1]",
        password=".//*[@id='loginForm']/div/input[2]",
        btn_signin=".//*[@id='loginForm']/div/button",
        login_text=".//*[@id='nav-logout']/a",

        key_input_show=".//*[@id='account']/div[1]/div[2]/div[1]/div[3]/a",
        key_input=".//*[@id='account']/div[1]/div[2]/div[3]/div[2]/input",
        key_send=".//*[@id='account']/div[1]/div[2]/div[3]/div[3]/button[1]",

        alert_text=".//*[@id='ng-app']/body/div[4]/div/div/div[1]/h3",
        alert_btn_cancel=".//*[@id='ng-app']/body/div[4]/div/div/div[3]/button",
        alert_btn_ok=".//*[@id='ng-app']/body/div[4]/div/div/div[3]/button[1]",

        plan_name=".//*[@id='account']/div[1]/div[2]/div[1]/div[2]"),

    rs=dict(
        is_login="/html/body/div[2]/form[1]/fieldset/dl/dt[1]/a/b",
        input_login="/html/body/div[2]/form[1]/fieldset/label[1]/input",
        input_passwd="/html/body/div[2]/form[1]/fieldset/label[2]/input",
        btn="/html/body/div[2]/form[1]/fieldset/div[1]/span/span/input")
)

result_text = dict(activated="Activation",
                   done="activate")

headers = [(
    'User-agent',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'
)]


def get_cg_user(file):
    with open(file, "r") as f:
        buf = f.readlines()

    try:
        user = buf.pop()
    except IndexError as e:
        return False

    with open(file, "w") as f:
        f.writelines(buf)

    return user


def write_to_file(fname, text):
    text += '\n'
    with open(fname, "a") as f:
        f.write(text)


def input_wait(msg):
    msg[0] = input("Type to quit:\n")
    if "None" not in msg:
        print("��������� ����� ���������...")

if __name__ == "__main__":
    loger = Logger()

    cg_users = get_cg_user(files["users"])
    if not cg_users:
        loger.store("E", "SYSTEM", "No cyberghost account!")
        exit(1)

    cg = CyberGhost(
        loger=loger,
        elements=elements["cg"],
        result_text=result_text,
        url=urls["cyber"]
    )

    test_key = "CHIPX2015-YJ8QE-UGDJ8-RBDCB-BBSM2-HXNFC"

    msg = ['None']
    m = Thread(target=input_wait, args=(msg,))
    m.setDaemon(True)
    m.start()
    while True:
        try:
            for i in range(interval):
                if "None" not in msg:
                    raise KeyboardInterrupt
                sleep(1)
        except KeyboardInterrupt:
            print("Bye")
            break

    cg.driver_start()
    cg.login(tuple(cg_users.split(":")))
    cg.run_check(test_key)
    cg.driver_stop()
