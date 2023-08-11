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


#宮城
def myg_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='D']['URL'][3]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='D']['name'][3]
    df_myg = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        #検索ワード入力
        browser.find_element_by_id('in-detail-keywords').send_keys(SearchWord)
        #会議内容選択
        checkboxes = browser.find_elements_by_class_name('checkbox')
        checkboxes[0].click()
        checkboxes[1].click()
        checkboxes[2].click()
        checkboxes[3].click()
        checkboxes[6].click()
        checkboxes[7].click()
        checkboxes[8].click()
        #会議種類選択
        checkboxes[-3].click()
        checkboxes[-2].click()
        #検索実行
        browser.find_element_by_id('v-search').click()

        sleep(3)

        org_window = browser.current_window_handle
        slideList_temp = browser.find_elements_by_class_name('slick-track')
        if slideList_temp == []:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_osk.columns)
            df_myg = df_myg.append(record,ignore_index=True) 
            browser.quit()
        else:
            slideList = browser.find_element_by_class_name('slick-track').find_elements_by_tag_name("div")
            for i in range(len(slideList)):
                slideList = browser.find_element_by_class_name('slick-track').find_elements_by_tag_name("div")
                browser.implicitly_wait(20)
                slideList[i].click()
                sleep(3)
                parentlist = browser.find_element_by_id('tbl-hit-result').find_elements_by_class_name('schedule')
                if parentlist != []:
                    for j in range(len(parentlist)):
                        parentlist = browser.find_element_by_id('tbl-hit-result').find_elements_by_class_name('schedule')
                        JournalTitle = parentlist[j].find_element_by_tag_name('span').text.split(' ')[0]
                        Date = JournalTitle.split('年')[0]+"年"+parentlist[j].find_element_by_tag_name('span').text.split(' ')[-2].split('－')[0]
                        if parentlist[j].find_element_by_tag_name('img').get_attribute('class') != 'rotate':
                            parentlist[j].click()
                            sleep(2)
                        childlist = parentlist[j].find_elements_by_class_name('minute ')
                        num = 1
                        for k in range(len(childlist)):
                            if childlist[k].get_attribute('class') == 'minute ':
                                Speaker = childlist[k].text.split('君）')[0]+'君）'
                                if not '議長' in Speaker:
                                    SpeakOrder = num
                                    #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
                                    Name = BookMarkName
                                    #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                                    record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_myg.columns)
                                    df_myg = df_myg.append(record,ignore_index=True)
                                    #繰り返し後の準備
                                    num += 1
                            elif childlist[k].get_attribute('class') == 'minute extra':
                                try:
                                    browser.execute_script('arguments[0].click();', parentlist[j].find_element_by_css_selector('p[class="expand"]'))
                                    sleep(1)
                                except:
                                    pass
                                Speaker = childlist[k].text.split('\n')[0]
                                if '議長' not in Speaker or '委員長' not in Speaker:
                                    SpeakOrder = num
                                    #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
                                    Name = BookMarkName
                                    #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                                    record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_myg.columns)
                                    df_myg = df_myg.append(record,ignore_index=True)
                                    #繰り返し後の準備
                                    num += 1

            browser.quit()

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_myg.columns)
        df_myg = df_myg.append(record,ignore_index=True)
        browser.quit()
            
    return df_myg


# In[ ]:


if __name__ == '__main__':
    myg_s()

