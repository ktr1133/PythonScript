#!/usr/bin/env python
# coding: utf-8

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


#岩手
def iwt_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='C']['URL'][2]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='C']['name'][2]
    df_iwt = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)
        Name = BookMarkName

        browser.switch_to.frame('SearchFrame')

        if '　' in SearchWord:
            SearchWords = SearchWord.split('　')
            SearchWordInputs_temp = browser.find_elements_by_css_selector('input[name^="keyword"]')
            SearchWordInputs = []
            for i in range(len(SearchWords)):
                SearchWordInputs.append(SearchWordInputs_temp[i])
            for ele1,ele2 in zip(SearchWords, SearchWordInputs):
                ele2.send_keys(ele1)
        elif ' ' in SearchWord:
            SearchWords = SearchWord.split(' ')
            SearchWordInputs_temp = browser.find_elements_by_css_selector('input[name^="keyword"]')
            SearchWordInputs = []
            for i in range(len(SearchWords)):
                SearchWordInputs.append(SearchWordInputs_temp[i])
            for ele1,ele2 in zip(SearchWords, SearchWordInputs):
                ele2.send_keys(ele1)
        else:
            SearchWordInput = browser.find_element_by_css_selector('input[name="keyword1"]')
            SearchWordInput.send_keys(SearchWord)

        #会議選択
        browser.find_element_by_css_selector('input[name="honkaigiAllCheckButton"]').click()
        #検索実行
        sleep(1)
        browser.find_element_by_css_selector("input[value='検　索']").click()

        browser.switch_to_default_content()
        browser.switch_to.frame('ResultFrame')

        if '条件を満たすデータが見つかりません。' in browser.find_element_by_tag_name('body').text:
            not_applicable = '該当する文書は存在しません。'
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_iwt.columns)
            df_iwt = df_iwt.append(record,ignore_index=True) 
            browser.quit()

        else:
            hits = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[1].find_elements_by_tag_name('tr')
            num =1
            for i in range(len(hits)):
                hits = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[1].find_elements_by_tag_name('tr')
                JournalTitle = hits[i].find_element_by_tag_name('a').text.split('(')[0]
                Date = hits[i].find_element_by_tag_name('a').text.split('年')[0] + "年" + hits[i].find_element_by_tag_name('a').text.split('(')[1].split(')')[0]
                Speaker_temp = hits[i].find_element_by_tag_name('a').text.split('　')[2]
                if '議長' not in Speaker_temp or '委員長' not in Speaker_temp:
                    if not '議事日程' in Speaker_temp:
                        Speaker = Speaker_temp
                        if Date == hits[i-1].find_element_by_tag_name('a').text.split('年')[0] + "年" + hits[i-1].find_element_by_tag_name('a').text.split('(')[1].split(')')[0]:
                            num += 1
                            SpeakOrder = num
                            Name = BookMarkName
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_iwt.columns)
                            df_iwt = df_iwt.append(record,ignore_index=True)
                        else:
                            num = 1
                            SpeakOrder = num
                            Name = BookMarkName
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_iwt.columns)
                            df_iwt = df_iwt.append(record,ignore_index=True)


            nextlink_candidate = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[2].find_elements_by_tag_name('td')[2]            
            while nextlink_candidate.find_elements_by_tag_name('a') != []:
                nextlink_candidate = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[2].find_elements_by_tag_name('td')[2]
                nextlink_candidate.find_element_by_tag_name('a').click()
                sleep(3)

                browser.switch_to_default_content()
                browser.switch_to.frame('ResultFrame')

                hits = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[1].find_elements_by_tag_name('tr')
                num =1
                for i in range(len(hits)):
                    hits = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[1].find_elements_by_tag_name('tr')
                    JournalTitle = hits[i].find_element_by_tag_name('a').text.split('(')[0]
                    Date = hits[i].find_element_by_tag_name('a').text.split('年')[0] + "年" + hits[i].find_element_by_tag_name('a').text.split('(')[1].split(')')[0]
                    Speaker_temp = hits[i].find_element_by_tag_name('a').text.split('　')[2]
                    if not '議長' in Speaker_temp and '委員長' not in Speaker_temp:
                        if not '議事日程' in Speaker_temp:
                            Speaker = Speaker_temp
                            if Date == hits[i-1].find_element_by_tag_name('a').text.split('年')[0] + "年" + hits[i-1].find_element_by_tag_name('a').text.split('(')[1].split(')')[0]:
                                num += 1
                                SpeakOrder = num
                                Name = BookMarkName
                                record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_iwt.columns)
                                df_iwt = df_iwt.append(record,ignore_index=True)
                            else:
                                num = 1
                                SpeakOrder = num
                                Name = BookMarkName
                                record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_iwt.columns)
                                df_iwt = df_iwt.append(record,ignore_index=True)

                nextlink_candidate = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[2].find_elements_by_tag_name('td')[2]            

            else:            
                browser.quit()

    except:
        error = 'error'
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_iwt.columns)
        df_iwt = df_iwt.append(record,ignore_index=True)
        browser.quit()
            
    return df_iwt


# In[ ]:


if __name__ == '__main__':
    iwt_s()

