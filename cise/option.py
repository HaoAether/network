import argparse as ag

programe_name = 'cise'
# 成都工业职业技术学院学生网络认证工具
description = 'cise - Chengdu Industry Student Enabler (v1.0)'

class Option:
    def __init__(self):
        self.ap = ag.ArgumentParser(prog="cise")
        pass