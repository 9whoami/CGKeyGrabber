# -*- coding: cp1251 -*-
__author__ = 'whoami'

from datetime import datetime


"""
I - Information
W - Warning
A - Alert
E - Exception
"""


class Logger(object):
    def __init__(self, logfile="log.txt"):
        super(Logger, self).__init__()
        self.logfile = logfile

    def store(self, type, system, subsystem, msg):
        time = str(datetime.now())
        msg = str(msg) + '\n'
        text = (time, type, system, subsystem, msg,)
        with open(self.logfile, "a") as file:
            file.write(' '.join(text))
        print(' '.join(text))
