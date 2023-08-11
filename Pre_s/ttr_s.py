#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import sqlite3
import pandas as pd

#ﾃﾞｰﾀ読込
import glob

#ｳｪﾌﾞｽｸﾚｲﾋﾟﾝｸﾞ用ﾗｲﾌﾞﾗﾘ
from selenium import webdriver
from selenium.webdriver.common.keys import Keys as keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

import chromedriver_binary
from time import sleep
from urllib.parse import urljoin 
from bs4 import BeautifulSoup
import urllib.request
import requests

#正規表現
import re
import unicodedata


# In[ ]:


#鳥取
def ttr_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='K']['URL'][30]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='K']['name'][30]
    df_ttr = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        #frameに移動
        browser.switch_to_frame('search')

        #検索ワード入力
        browser.find_element_by_id('search').find_element_by_css_selector('input[name="Phrase[]"]').send_keys(SearchWord)
        #検索実行
        browser.find_element_by_css_selector('input[value="  検　索  "]').click()
        sleep(1)

        browser.switch_to.window(browser.window_handles[-1])

        #該当なしの場合
        nohit_temp1 = browser.find_element_by_id('list')
        nohit_temp2 = nohit_temp1.find_element_by_tag_name('div')
        nohit_temp3 = nohit_temp2.find_element_by_css_selector('p[class="count"]')
        counts = nohit_temp3.find_elements_by_tag_name('span')
        if counts[0] == 0 and counts[1] ==0:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_ttr.columns)
            df_ttr = df_ttr.append(record,ignore_index=True) 
            browser.quit()

        #該当ありの場合
        else:
            Name = BookMarkName
            resultlists = browser.find_element_by_id('list').find_element_by_css_selector('div[class="result"]').find_elements_by_xpath(".//*")
            for i in range(len(resultlists)):
                if resultlists[i].tag_name == 'dt':
                    Date = resultlists[i].find_elements_by_tag_name('span')[1].text
                    JournalTitle = resultlists[i].find_element_by_tag_name('a').text
                elif resultlists[i].tag_name == 'dd':
                    Speaker_temp = resultlists[i].text
                    if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                        Speaker = Speaker_temp
                        if resultlists[i-1].tag_name == 'dt':
                            SpeakOrder = 1
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder]
                                               , index=df_ttr.columns)
                            df_ttr = df_ttr.append(record,ignore_index=True)
                        else:
                            num = 1
                            for j in range(1,i):
                                if resultlists[i-j].tag_name == 'dd':
                                    num += 1
                                elif resultlists[i-j].tag_name == 'dt':
                                    break
                            SpeakOrder = num
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder]
                                               , index=df_ttr.columns)
                            df_ttr = df_ttr.append(record,ignore_index=True)
                        
            nextlinks = browser.find_element_by_css_selector('div[class="pagination"]').find_element_by_tag_name('ul').find_elements_by_tag_name('li')
            while nextlinks[-1].get_attribute('class') !='disabled':
                nextlinks = browser.find_element_by_css_selector('div[class="pagination"]').find_element_by_tag_name('ul').find_elements_by_tag_name('li')
                nextlinks[-1].click()

                resultlists = browser.find_element_by_id('list').find_element_by_css_selector('div[class="result"]').find_elements_by_xpath(".//*")
                for i in range(len(resultlists)):
                    if resultlists[i].tag_name == 'dt':
                        Date = resultlists[i].find_elements_by_tag_name('span')[1].text
                        JournalTitle = resultlists[i].find_element_by_tag_name('a').text
                    elif resultlists[i].tag_name == 'dd':
                        Speaker_temp = resultlists[i].text
                        if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                            Speaker = Speaker_temp
                            if resultlists[i-1].tag_name == 'dt':
                                SpeakOrder = 1
                                record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder]
                                                   , index=df_ttr.columns)
                                df_ttr = df_ttr.append(record,ignore_index=True)
                            else:
                                num = 1
                                for j in range(1,i):
                                    if resultlists[i-j].tag_name == 'dd':
                                        num += 1
                                    elif resultlists[i-j].tag_name == 'dt':
                                        break
                                SpeakOrder = num
                                record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder]
                                                   , index=df_ttr.columns)
                                df_ttr = df_ttr.append(record,ignore_index=True)
                nextlinks = browser.find_element_by_css_selector('div[class="pagination"]').find_element_by_tag_name('ul').find_elements_by_tag_name('li')

            browser.quit()

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_ttr.columns)
        df_ttr = df_ttr.append(record,ignore_index=True)
        browser.quit()
            
    return df_ttr


# In[ ]:


if __name__ == '__main__':
    ttr_s()

