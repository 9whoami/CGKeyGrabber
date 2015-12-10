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
interval = 60
cur_page = 95
urls = dict(
    cyber="https://account.cyberghostvpn.com/en_us/login",
    rs_load="http://forum.rsload.net/cat-kryaki-seriyniki-varez/topic-" \
            "4820-page-%d.html",
    rs_load_rss="http://forum.rsload.net/topic4820/rss.xml"
)

elements = dict(
    cg=dict(
        cancel_key=".//*[@id='account']/div[1]/div[2]/div[3]/div[3]/button[2]",
        check_login=".//*[@id='nav-logout']/a",
        login="/html/body/div[1]/div/div/div[2]/form/div/input[1]",
        passwd="/html/body/div[1]/div/div/div[2]/form/div/input[2]",
        button_login="/html/body/div[1]/div/div/div[2]/form/div/button",
        show_keys_form="/html/body/div[1]/div/div/div[1]/div[3]/div[1]/" \
                       "div[1]/div[2]/div[1]/div[3]/a",
        input_key="/html/body/div[1]/div/div/div[1]/div[3]/div[1]/div[1]/" \
                  "div[2]/div[3]/div[2]/input",
        button_key="/html/body/div[1]/div/div/div[1]/div[3]/div[1]/div[1]/" \
                   "div[2]/div[3]/div[3]/button[1]",
        alert_text="/html/body/div[4]/div/div/div[2]/div/strong",
        alert_button="/html/body/div[4]/div/div/div[3]/button",
        activation_button="/html/body/div[4]/div/div/div[3]/button[1]",
        plan_text="/html/body/div[1]/div/div/div[1]/div[3]/div[1]/div[1]/" \
                  "div[2]/div[1]/div[2]"),
    rs=dict(
        max_page=".//*[@id='board_index']/div[1]/div/div[2]/ol/li[1]/a",
        keys='.//blockquote/p/span[@class="texthide"]',
        is_login="/html/body/div[2]/form[1]/fieldset/dl/dt[1]/a/b",
        input_login="/html/body/div[2]/form[1]/fieldset/label[1]/input",
        input_passwd="/html/body/div[2]/form[1]/fieldset/label[2]/input",
        btn="/html/body/div[2]/form[1]/fieldset/div[1]/span/span/input")
)

result_text = dict(not_found="Activation key not found",
                   activated="Activation key already used",
                   done="Activate your subscription")

plan_text = "Free Plan"

headers = [(
    'User-agent',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 " \
    "Fedora/3.0.1-1.fc9 Firefox/3.0.1'
)]

msg = ['None']


def get_cg_user(file):
    with open(file, "r") as f:
        buf = f.readlines()

    try:
        user = buf.pop()
    except IndexError as e:
        return False

    with open(file, "w") as f:
        f.writelines(buf)

    if not user:
        loger.store("E", "SYSTEM", "No cyberghost account!")
        exit(1)
    return user


def write_to_file(fname, text):
    with open(fname, "a") as f:
        f.write(text)


def input_wait(msg):
    msg[0] = input("Type to quit: ")

if __name__ == "__main__":
    loger = Logger()
    loger.store("I", "SYSTEM", "=============================================")

    cg = CyberGhost(
        loger=loger,
        elements=elements["cg"],
        result_text=result_text,
        plan_text=plan_text,
        url=urls["cyber"]
    )
    rs_load = RsLoad(
        user=rs_user,
        url=urls,
        page=cur_page,
        headers=headers,
        xpath=elements["rs"],
        loger=loger,
        history=files["story"])

    loger.store("I", "SYSTEM", "Компоненты загружены и готовы к работе")
    if rs_load.signin():
        cg_users = get_cg_user(files["users"])
        while True:
            try:
                keys = rs_load.get_all_keys()
                if keys:
                    cg.driver_start()
                    for key in keys:
                        cg.login(tuple(cg_users.split(":")))
                        if cg.run_check(key=key):
                            write_to_file(files["out"], cg_users)
                            cg_users = get_cg_user(files["users"])
                            cg.login(tuple(cg_users.split(":")))
                        write_to_file(files["story"], key)
                    cg.driver_stop()
                m = Thread(target=input_wait, args=(msg,))
                m.start()
                for i in range(interval):
                    if "None" not in msg:
                        raise KeyboardInterrupt
                    sleep(1)
                if m.isAlive():
                    m.join(2)
            except KeyboardInterrupt:
                write_to_file(files["users"], cg_users)
                print("Bye")
                break
