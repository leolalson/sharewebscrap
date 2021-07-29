import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta
import openpyxl
import pandas as pd
from threading import Timer
from time import time, sleep
import matplotlib.pyplot as plt
import matplotlib
import json
import bokeh
import sys
import numpy as np


class ScrapMoneycontrol:
    def __init__(self,input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir


    def plot_intraday_graphs(self):
        stock_list = self.get_today_stock_list("today")
        file_name_excel = self.output_dir + "\\analysis_data_today.xlsx"
        urls = self.get_urls(stock_list)

        old_data = {}
        avg_data = {}

        time_intervel = 2
        num_day = 9
        current = datetime.today()
        time_stamp = current #- timedelta(days=1)
        #time_stamp = current.replace(day=current.day, hour=9, minute=20, second=0, microsecond=0)

        while (True):
            for url in urls:
                old_data[url], status = self.get_old_data2(num_day, urls[url],time_stamp)
            if status == 1:
                break
            else:
                sleep(60 * time_intervel)

        while (True):
            current_data = {}
            for url in urls:
                current_data[url], status = self.get_old_data2(1, urls[url],time_stamp)
            if status == 1:
                all_data = {}
                for url in urls:
                    all_data[url] = self.process_data(old_data[url], current_data[url])
                        #self.plot_old_data(url, all_data[url])
                volprice_analysis_data = self.process_data3(time_intervel,stock_list, all_data, 360, file_name_excel)
                self.plot_old_data2(volprice_analysis_data,all_data)
                plt.pause(60 * time_intervel)
            else:
                sleep(60 * time_intervel)

    def run_analysis(self):
        file_name_csv = self.output_dir + "\\analysis_data.csv"
        file_name_excel = self.output_dir + "\\analysis_data.xlsx"
        stock_list = self.get_today_stock_list("analysis")
        urls = self.get_urls(stock_list)
        old_data = {}

        time_intervel = 2
        num_day = 9
        current = datetime.today()
        time_stamp = current #- timedelta(days=1)
        #time_stamp = current.replace(day=current.day, hour=9, minute=20, second=0, microsecond=0)

        while (True):
            for url in urls:
                old_data[url], status = self.get_old_data2(num_day, urls[url],time_stamp)
            if status == 1:
                break
            else:
                sleep(60 * time_intervel)

        while (True):
            current_data = {}
            for url in urls:
                current_data[url], status = self.get_old_data2(1, urls[url],time_stamp)
            if status == 1:
                all_data = {}
                vol_change_percent = {}
                analysis_data_df = pd.DataFrame()#(columns=["Stock","volume_chnage","price_chnage"])
                price_change_percent = {}
                count = 0
                for url in urls:
                    all_data[url] = self.process_data(old_data[url], current_data[url])
                volprice_analysis_data = self.process_data3(15,stock_list, all_data,360,file_name_excel)
                #self.plot_old_data2(volprice_analysis_data)
                    #vol_change_percent[url],price_change_percent[url] = self.process_data2(all_data[url])
                    #temp_dict = {"Stock":url,"volume_change":vol_change_percent[url],"price_change":price_change_percent[url]}
                    #analysis_data_df = analysis_data_df.append(temp_dict,ignore_index=True)
            #avg_diff_percent_df = pd.DataFrame.from_dict(analysis_data).transpose()
            #analysis_data_df.to_csv(file_name_csv, index=False)
            #writer = pd.ExcelWriter("analysis_data.xlsx",engine='xlsxwriter')
            #analysis_data_df.to_excel(file_name_excel,sheet_name="sheet1",index=False)



            print("Analysis completed")
            break
            #sleep(60 * time_intervel)

    def get_today_stock_list(self,type):
        #stock_list = ["ICICI"]
        file_name = self.input_dir + "\\today_analysis_list.csv"
        data = pd.read_csv(file_name, encoding='ISO-8859-1')

        if type == "today":
            data = data[data["YES/NO"] == "Y"]
            stock_list = list(data["SYMBOL"])
        elif type == "analysis":
            data = data[data["Analysis"] == "Y"]
            stock_list = list(data["SYMBOL"])
        return stock_list

    def get_urls(self, keys):
        file_name = self.input_dir + "\\urls.csv"
        url_data = pd.read_csv(file_name, encoding='ISO-8859-1')
        url_dict = dict(zip(url_data["SYMBOL"], url_data["url"]))
        urls = {}
        for key in keys:
            urls[key] = url_dict[key]
        return urls

    def get_data_from_internet(self, link):
        temp_data = {}
        try:
            req1 = requests.get(link)
            soup1 = BeautifulSoup(req1.content, 'html.parser')

            data_string = soup1.contents[0]
            temp_data = json.loads(data_string)
        except requests.exceptions.ConnectionError as e:
            temp_data = {"s": "no_internet_connection"}

        return temp_data

    def plot_old_data(self,key, old_dataframe):
        current = datetime.today()
        morning = current.replace(day=current.day, hour=9, minute=0, second=0, microsecond=0)
        evening = current.replace(day=current.day, hour=15, minute=15, second=0, microsecond=0)
        temp_1115 = current.replace(day=current.day, hour=11, minute=15, second=0, microsecond=0)
        date_str_list=[]
        line_colour = ["Black","Blue","Aqua","DarkKhaki","DarkSalmon","LightBlue","Olive","Grey","Khaki","Lavender","LemonChiffon"]
        count = 0
        #sum_volume = [0] * (len((old_dataframe[list(old_dataframe.keys())[0]])['t']))
        xaxis_intervel = timedelta(days = 0,hours= 0,minutes= 5, seconds=0)
        for date in reversed(old_dataframe):
            date_str_list.append(date)
            temp_dataframe = old_dataframe[date]
            # temp_dataframe.plot(x='t', y='v', kind='line')
            x2 = list(temp_dataframe['t'])
            x2 = self.covert_time_todaytime(x2)
            y2 = list(temp_dataframe['v'])

            plt.figure(key, figsize=(5, 6))
            plt.plot(x2, y2, c=line_colour[count])
            count = count +1
            #plt.gcf().autofmt_xdate()

            # plt.gcf().autofmt_xdate()
            # plt.pause(1)
        #plot average data
        #average_volume = np.divide(sum_volume,(count+1))
        #plt.figure(key, figsize=(5, 6))
        #plt.plot(x2, average_volume, c="Black")

        myFmt = matplotlib.dates.DateFormatter('%H:%M')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xticks(np.arange(morning,evening+xaxis_intervel,xaxis_intervel),rotation =90, fontsize=6)
        plt.grid(key)
        plt.legend(date_str_list)
        #wplt.xlim(morning,temp_1115)


    def covert_time_todaytime(self,time_list):
        # nly_time = datetime.fromtimestamp(time_list)
        # only_time = [datetime.time(datetime.fromtimestamp(x)) for x in time_list]
        only_time = [datetime.combine(datetime.today().date(), datetime.time(datetime.fromtimestamp(x))) for x in time_list]
        # only_time = matplotlib.dates.date2num(only_time)
        return only_time

    def get_average_line(self,old_dataframe):
        temp_vol = pd.DataFrame()

        for date in old_dataframe:
            temp_dataframe = old_dataframe[date]
            temp_vol[date] = temp_dataframe['v']
            temp_time = temp_dataframe['t']

        mean_line = temp_vol.mean(1)
        average_line = pd.DataFrame()
        average_line['v'] = mean_line
        average_line['t'] = temp_time
        average_line.dropna(subset=['t'], inplace=True)
        return average_line

    def get_old_data2(self,num_day, link,time_stamp=datetime.today()):
        morning = time_stamp.replace(day=time_stamp.day, hour=9, minute=15, second=0, microsecond=0)
        evening = time_stamp.replace(day=time_stamp.day, hour=15, minute=15, second=0, microsecond=0)

        temp_data2 = {}
        old_data = {}
        status = 0

        for count in range(num_day):
            if num_day == 1:
                day = 0
            elif num_day > 1:
                day = num_day-count
            temp_date_morning = morning - timedelta(days=day)
            temp_date_evening = evening - timedelta(days=day)

            if temp_date_evening > time_stamp:
                temp_date_evening = time_stamp - timedelta(seconds=40)
                if temp_date_morning > time_stamp:
                    status=1
                    print("waiting for 9:15")
                    temp_date_morning_int = round(temp_date_morning.timestamp())
                    temp_data2['t'] = [temp_date_morning_int]
                    temp_data2['v'] = [0]
                    temp_dataframe = pd.DataFrame.from_dict(temp_data2)
                    old_data[temp_date_morning.strftime("%d %b")] = temp_dataframe
                    return old_data,status
            temp_date_morning_int = round(temp_date_morning.timestamp())
            temp_date_evening_int = round(temp_date_evening.timestamp())
            temp_link = link + str(temp_date_morning_int) + "&to=" + str(temp_date_evening_int)
            temp_data = self.get_data_from_internet(temp_link)
            # string_length = len(temp_data["t"])
            if temp_data["s"] == "no_internet_connection":
                print("no internet connection")
                status = 0
                return old_data, status
            status = 1
            #temp_dataframe = pd.DataFrame.from_dict(temp_data)
            old_data[temp_date_morning.strftime("%d %b")] = temp_data
        return old_data, status

    def plot_data(self,key, old_dataframe):
        current = datetime.today()
        morning = current.replace(day=current.day, hour=9, minute=0, second=0, microsecond=0)
        evening = current.replace(day=current.day, hour=15, minute=15, second=0, microsecond=0)
        temp_1115 = current.replace(day=current.day, hour=11, minute=15, second=0, microsecond=0)
        date_str_list=[]
        line_colour = ["Blue","Aqua","DarkKhaki","DarkSalmon","LightBlue","Olive","Grey","Khaki","Lavender","LemonChiffon"]
        count = 0
        #sum_volume = [0] * (len((old_dataframe[list(old_dataframe.keys())[0]])['t']))
        xaxis_intervel = timedelta(days = 0,hours= 0,minutes= 5, seconds=0)
        for date in old_dataframe:
            date_str_list.append(date.strftime("%d %b"))
            temp_dataframe = old_dataframe[date]
            # temp_dataframe.plot(x='t', y='v', kind='line')
            x2 = list(temp_dataframe['t'])
            x2 = self.covert_time_todaytime(x2)
            y2 = list(temp_dataframe['v'])

            plt.figure(key, figsize=(5, 6))
            plt.plot(x2, y2, c=line_colour[count])
            count = count +1
            #plt.gcf().autofmt_xdate()

            # plt.gcf().autofmt_xdate()
            # plt.pause(1)
        #plot average data
        #average_volume = np.divide(sum_volume,(count+1))
        #plt.figure(key, figsize=(5, 6))
        #plt.plot(x2, average_volume, c="Black")

        myFmt = matplotlib.dates.DateFormatter('%H:%M')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xticks(np.arange(morning,evening+xaxis_intervel,xaxis_intervel),rotation =90, fontsize=6)
        plt.grid(key)
        plt.legend(date_str_list)
        #wplt.xlim(morning,temp_1115)

    def process_data(self,old_data,current_data):
        all_data = {}
        for date in old_data:
            if old_data[date]['s'] == "ok" and len(old_data[date]['t']) > 2:
                temp_data = old_data[date].copy()    #['t','o','h','l','c','v']
                del temp_data["s"]
                all_data[date] = pd.DataFrame.from_dict(temp_data)
        avg_data = self.get_average_line(all_data)

        for date in current_data:

            if not current_data[date]['s'] == "no_data":
                if current_data[date]['s'] == "ok" and len(current_data[date]['t']) > 2:
                    temp_data = current_data[date].copy()
                    del temp_data['s']
                    all_data[date] = pd.DataFrame.from_dict(temp_data)

        all_data['Average'] = avg_data
        return all_data

    def process_data2(self,all_data):
        vol_data = pd.DataFrame()
        price_data = pd.DataFrame()
        vol_data['Average'] = all_data['Average']['v']
        all_data_keys = list(all_data.keys())
        date_stamp = all_data_keys[len(all_data_keys)-2]
        temp = all_data[date_stamp]['v']
        #temp = temp.iloc[0:30]
        vol_data['Today'] = temp
        vol_data.dropna(subset=['Average','Today'], inplace=True)

        mean_line = (pd.DataFrame(vol_data.mean(0)))
        avg_diff_percent = 100 * (mean_line[0]['Today'] - mean_line[0]['Average'])/(mean_line[0]['Average'])

        price_data['o'] = all_data[date_stamp]['o']
        price_data['h'] = all_data[date_stamp]['h']
        price_data['l'] = all_data[date_stamp]['l']
        price_data['c'] = all_data[date_stamp]['c']
        price_data_length = price_data.shape[0]

        price_open = price_data['o'][0]
        price_close = price_data['c'][price_data_length-1]
        price_diff_percent = -100*(price_open-price_close)/price_open

        return avg_diff_percent,price_diff_percent

    def process_data3(self,interval,stock_list,full_data,minute_time,file_name_excel):

        vol_change_percent = {}
        vol_change_percent_df = pd.DataFrame()
        price_change_percent = {}
        price_change_percent_df = pd.DataFrame()

        time_list = [i for i in np.arange(interval,minute_time+interval,interval)]
        for url in stock_list:
            for thisTime in time_list:
                vol_data = pd.DataFrame()
                price_data = pd.DataFrame()
                all_data = full_data[url]
                vol_data['Average'] = all_data['Average']['v']
                all_data_keys = list(all_data.keys())
                date_stamp = all_data_keys[len(all_data_keys)-2]
                temp = all_data[date_stamp]['v']

                price_data_length = temp.shape[0] - 1
                if thisTime > price_data_length:
                    thisTime = price_data_length
                temp = temp.iloc[0:thisTime]
                vol_data['Today'] = temp
                vol_data.dropna(subset=['Average','Today'], inplace=True)

                mean_line = (pd.DataFrame(vol_data.mean(0)))
                avg_diff_percent = 100 * (mean_line[0]['Today'] - mean_line[0]['Average'])/(mean_line[0]['Average'])

                vol_change_percent[thisTime] = avg_diff_percent



                price_data['o'] = all_data[date_stamp]['o']
                price_data['h'] = all_data[date_stamp]['h']
                price_data['l'] = all_data[date_stamp]['l']
                price_data['c'] = all_data[date_stamp]['c']
                price_data_length = price_data.shape[0] -1

                price_open = price_data['o'][0]

                if thisTime > price_data_length:
                    thisTime = price_data_length
                price_close = price_data['c'][thisTime]
                price_diff_percent = -100*(price_open-price_close)/price_open

                #vol_change_percent[url] = avg_diff_percent
                price_change_percent[thisTime] = price_diff_percent
            temp1_df = pd.Series(vol_change_percent, index=vol_change_percent.keys())
            vol_change_percent_df[url] = temp1_df

            temp2_df = pd.Series(price_change_percent, index=price_change_percent.keys())
            price_change_percent_df[url] = temp2_df
        vol_change_percent_df = vol_change_percent_df.transpose()
        price_change_percent_df = price_change_percent_df.transpose()
        writer = pd.ExcelWriter(file_name_excel, engine='xlsxwriter')

        # Write each dataframe to a different worksheet.
        vol_change_percent_df.to_excel(writer, sheet_name='Volume')
        price_change_percent_df.to_excel(writer, sheet_name='Price')

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()
        analysis_data = {"vol_analysis":vol_change_percent_df,"price_analysis":price_change_percent_df}
        return analysis_data

    def plot_old_data2(self,analysis_data,all_data):

        vol_data = analysis_data["vol_analysis"]
        price_data = analysis_data["price_analysis"]

        df_length = vol_data.shape[0]
        time_data = vol_data.columns.values.tolist()
        all_data_keys = list(all_data.keys())
        count = 0
        for stock in vol_data.index:
            vol = vol_data.loc[stock].values.tolist()
            price = price_data.loc[stock].values.tolist()
            time_data = vol_data.columns.values.tolist()
            vol.pop()
            price.pop()
            x = time_data
            x.pop()

            # y-axis values
            y1 = vol

            # secondary y-axis values
            y2 = price

            # plotting figures by creating aexs object
            # using subplots() function
            fig, (ax,ax3) = plt.subplots(1,2,figsize=(10, 5))
            fig.canvas.set_window_title(stock)
            #plt.title('Example of Two Y labels')

            # using the twinx() for creating another
            # axes object for secondry y-Axis
            ax2 = ax.twinx()
            ax.plot(x, y1, color='g')
            ax2.plot(x, y2, color='b')

            # giving labels to the axises
            ax.set_xlabel('x-axis', color='r')
            ax.set_ylabel('Volume', color='g')

            # secondary y-axis label
            ax2.set_ylabel('Price', color='b')

            x3 = [1,2,3]
            y3 = [1,2,3]
            this_data = all_data[all_data_keys[count]]
            count = count+1

            #ax3.plot(x3, y3, color='b')
            self.plot_data3(ax3,this_data)
            # defining display layout
            plt.tight_layout()

    def plot_data3(self,ax3, old_dataframe):
        current = datetime.today()
        morning = current.replace(day=current.day, hour=9, minute=0, second=0, microsecond=0)
        evening = current.replace(day=current.day, hour=15, minute=15, second=0, microsecond=0)
        temp_1115 = current.replace(day=current.day, hour=11, minute=15, second=0, microsecond=0)
        date_str_list=[]
        line_colour = ["Blue","Aqua","DarkKhaki","DarkSalmon","LightBlue","Olive","Grey","Khaki","Lavender","LemonChiffon"]
        count = 0
        #sum_volume = [0] * (len((old_dataframe[list(old_dataframe.keys())[0]])['t']))
        xaxis_intervel = timedelta(days = 0,hours= 0,minutes= 5, seconds=0)
        for date in old_dataframe:
            #date_str_list.append(date.strftime("%d %b"))
            temp_dataframe = old_dataframe[date]
            # temp_dataframe.plot(x='t', y='v', kind='line')
            x2 = list(temp_dataframe['t'])
            x2 = self.covert_time_todaytime(x2)
            y2 = list(temp_dataframe['v'])

            #plt.figure(key, figsize=(5, 6))
            ax3.plot(x2, y2, c=line_colour[count])
            count = count +1
            #plt.gcf().autofmt_xdate()

            # plt.gcf().autofmt_xdate()
            # plt.pause(1)
        #plot average data
        #average_volume = np.divide(sum_volume,(count+1))
        #plt.figure(key, figsize=(5, 6))
        #plt.plot(x2, average_volume, c="Black")

        myFmt = matplotlib.dates.DateFormatter('%H:%M')
        #ax3.gca().xaxis.set_major_formatter(myFmt)
        #ax3.set_xticks(np.arange(morning,evening+xaxis_intervel,xaxis_intervel), fontsize=6)
        ax3.grid()
        ax3.legend(date_str_list)
        #wplt.xlim(morning,temp_1115)









