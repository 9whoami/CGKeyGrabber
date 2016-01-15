# -*- coding: cp1251 -*-
__author__ = 'whoami'
__version__ = '1.2.2 Beta'

from thread import thread
from time import sleep
from cg import CyberGhost
from rsload import RsLoad
from logger import Logger
from re import sub as replace

interval = 60
cur_page = 95
msg = ['None']
rs_user = ("wiom", "ghbphfr1",)

files = dict(
    out="out.txt",
    story="history.txt",
    users="users.txt"
)

urls = dict(
    cyber="https://account.cyberghostvpn.com/en_us/login",
    rs_load="http://forum.rsload.net/",
    rs_load_rss="http://forum.rsload.net/topic4820/rss.xml"
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
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 " \
    "Fedora/3.0.1-1.fc9 Firefox/3.0.1'
)]

CG_USERS = []


def switch_func(func):

    def wrapper(*args):
        global get_cg_user, change_user
        get_cg_user = change_user

        return func(*args) if args else func()

    return wrapper


def get_username():

    filter = lambda s: replace("^\ufeff", "", s)

    try:
        assert len(CG_USERS), "Not accounts to CG!"
        assert ":" in CG_USERS[0], "Not accounts to CG!"
        user = filter(CG_USERS[0])
        user = user.split(":")
        return user[:2]
    except IndexError:
        raise SystemExit("Not accounts to CG!")


def change_user(file):
    global CG_USERS

    CG_USERS.pop(0)

    with open(file, "w") as f:
        f.writelines(CG_USERS)

    return get_username()


@switch_func
def get_cg_user(file):
    global CG_USERS

    with open(file, "r") as f:
        CG_USERS = f.readlines()

    return get_username()


def write_to_file(fname, text):
    global CG_USERS

    with open(fname, "a") as f:
        if ':' in text:
            f.writelines(CG_USERS[0])
        else:
            f.writelines(text)

    with open(fname, "r") as f:
        buf = f.readlines()

    return len(buf)


@thread
def input_wait(msg):
    while "quit" not in msg:
        msg[0] = input("Type 'quit' to exit this program:\n")
    print("Exit...")


def add_new_accounts():
    global CG_USERS

    CG_USERS.clear()
    with open(files["users"], "r") as f:
        CG_USERS = f.readlines()

    filter = lambda s: replace("^\ufeff", "", s)
    user = filter(CG_USERS[0]).split(":")

    return user[:2]


if __name__ == "__main__":
    logger = Logger()
    logger.store("I", "SYSTEM", "HELLO",
                "<=================HELLO=======================>")

    cg = CyberGhost(
        loger=logger,
        elements=elements["cg"],
        result_text=result_text,
        url=urls["cyber"]
    )
    rs_load = RsLoad(
        user=rs_user,
        url=urls,
        page=cur_page,
        headers=headers,
        xpath=elements["rs"],
        loger=logger,
        history=files["story"])

    status = dict(
        new_keys_count=0,
        accounts_activate=0,
        accounts=0
    )

    logger.store("I", "SYSTEM", "", "Компоненты загружены и готовы к работе")

    if rs_load.signin():

        cg_users = get_cg_user(files["users"])
        status["accounts"] = len(CG_USERS)

        input_wait(msg)

        while True:
            try:
                keys = rs_load.get_all_keys()

                if keys:
                    status["new_keys_count"] += len(keys)
                    cg.driver_start()

                    for key in keys:
                        cg.login(cg_users)

                        if cg.run_check(key=key):
                            status["accounts_activate"] = write_to_file(
                                files["out"],
                                ":".join(cg_users)
                            )
                            cg_users = get_cg_user(files["users"])
                            status["accounts"] = len(CG_USERS)

                        key += "\n"
                        write_to_file(files["story"], key)

                    cg.driver_stop()
                    print(status)
                    print("Type 'quit' to exit this program:\n")

                for i in range(interval):

                    if "quit" in msg:
                        raise KeyboardInterrupt
                    elif "status" in msg:
                        msg[0] = None
                        print(status)
                    elif "add_accounts" in msg:
                        msg[0] = None
                        cg_users = add_new_accounts()
                        status["accounts"] = len(CG_USERS)

                        print("New account added\n",
                              "cg_users:", cg_users,
                              "\nAccounts count:", status["accounts"],
                              "\nAccounts list:\n", "".join(CG_USERS))

                    sleep(1)
            except KeyboardInterrupt:
                # write_to_file(files["users"], ":".join(cg_users))
                logger.store("I", "SYSTEM", "Bye",
                            "<=========Работа программы завершена==========>")
                break
