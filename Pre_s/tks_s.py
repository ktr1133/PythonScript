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


#徳島
def tks_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='L']['URL'][35]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='L']['name'][35]
    df_tks = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        #検索ワード入力
        browser.find_element_by_id('tab-detail').click()
        browser.find_element_by_id('se-detail-keywords').send_keys(SearchWord)

        #会議・資料の種類選択
        browser.find_element_by_id('chk-committee-all').click()
        inputs1 = browser.find_element_by_id('tbl-council-type').find_elements_by_tag_name('input')
        for ele in inputs1:
            if '5' in ele.get_attribute('value'):
                ele.click()
        inputs2 = browser.find_element_by_id('tbl-material-type').find_elements_by_tag_name('input')
        for ele in inputs2:
            if '10' in ele.get_attribute('value'):
                ele.click()

        #検索実行
        browser.find_element_by_id('btn-search').click()

        sleep(3)
        dropdown_temp = browser.find_elements_by_id('slt-hit-year')
        if browser.find_element_by_id('v-hit-count').text == '0':
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_tks.columns)
            df_tks = df_tks.append(record,ignore_index=True) 
            browser.quit()
        else:
            dropdown = browser.find_element_by_id('slt-hit-year')
            select = Select(dropdown)
            options = select.options
            for i in range(len(options)):
                browser.find_element_by_id('slt-hit-year').click()
                sleep(3)
                dropdown = browser.find_element_by_id('slt-hit-year')
                select = Select(dropdown)
                options = select.options
                options[i].click()
                sleep(3)

                parentlist_temp = browser.find_element_by_id('v-hit-list').find_elements_by_tag_name('tr')
                parentlist = []
                for ele in parentlist_temp:
                    if 'schedule' in ele.get_attribute('class'):
                        parentlist.append(ele)
                    elif 'minutes' in ele.get_attribute('class'):
                        parentlist.append(ele)
                for i in range(len(parentlist)):
                    if 'schedule' in parentlist[i].get_attribute('class'):
                        items = parentlist[i].find_elements_by_tag_name('td')
                        if items[3].find_element_by_tag_name('button').text == '▼':
                            items[3].find_element_by_tag_name('button').click()
                            sleep(1)
                        Date = items[0].text+items[2].text.split('－')[0]
                        JournalTitle = items[1].text
                    elif 'minutes' in parentlist[i].get_attribute('class'):
                        temp =  parentlist[i].find_element_by_tag_name('tbody')
                        trtags = temp.find_elements_by_tag_name('tr')
                        num = 1
                        for j in range(len(trtags)):
                            child_items = trtags[j].find_elements_by_tag_name('td')
                            Speaker = child_items[1].text
                            if '委員長' not in Speaker:
                                SpeakOrder = num
                                Name = BookMarkName
                                record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_tks.columns)
                                df_tks = df_tks.append(record,ignore_index=True)
                                num += 1

            browser.quit()
            
    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_tks.columns)
        df_tks = df_tks.append(record,ignore_index=True)
        browser.quit()
            
    return df_tks


# In[ ]:


if __name__ == '__main__':
    tks_s()

