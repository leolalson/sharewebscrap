import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta
import openpyxl
import pandas as pd
from threading import Timer
from time import time, sleep
import matplotlib.pyplot as plt
import json
import bokeh
import sys
from intraday_methods import ScrapMoneycontrol

base_dir = "D:\\Users\\Lalson\\pycharmprojects\\sharemarketdata"
output_dir = base_dir + "\\output"
input_dir = base_dir + "\\input"


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return


def check_input_dir(directory):
    if not os.path.exists(directory):
        print("directory not available")
        sys.exit()
    return


if __name__ == '__main__':
    create_dir(output_dir)
    check_input_dir(input_dir)



    stock_list = ["ICICI","INFOSYS","SBIN","SUNPHARMA","WIPRO"]
    scrap = ScrapMoneycontrol(input_dir,output_dir)
    scrap.plot_intraday_graphs()
    scrap.run_analysis()

    print("lalson")


