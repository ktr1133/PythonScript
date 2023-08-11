#!/usr/bin/env python
# coding: utf-8

# In[4]:


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


# In[5]:


#千葉
def chb_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='G']['URL'][11]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='G']['name'][11]
    df_chb = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        #トップページから詳細検索ページに遷移
        browser.find_element_by_id('nav').find_element_by_css_selector('li[class="detail"]').click()

        #検索ワード入力
        browser.find_element_by_id('content').find_element_by_css_selector('input[name="Phrases"]').send_keys(SearchWord)
        #文書の選択
        browser.find_element_by_id('cabinet1').click()
        browser.find_element_by_id('cabinet2').click()
        #分類の選択
        browser.find_element_by_id('classes2').click()
        #検索の実行
        browser.find_element_by_css_selector('input[value="検索実行"]').click()

        #開いたﾍﾟｰｼﾞに移動
        browser.switch_to.window(browser.window_handles[-1])

        Name = BookMarkName
        SearchWord = self
        resultTable = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol')
        documents = resultTable.find_elements_by_class_name('title')
        divtags_temp = resultTable.find_elements_by_tag_name('div')
        if documents == []:
            not_applicable = '該当する文書は存在しません'
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_chb.columns)
            df_chb = df_chb.append(record,ignore_index=True)
        else:
            divtags_temp = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol').find_elements_by_tag_name('div')
            divtags = []
            for ele in divtags_temp:
                if 'title' in ele.get_attribute('class'):
                    divtags.append(ele)
                elif 'voice' in ele.get_attribute('class'):
                    divtags.append(ele)
            for i in range(len(divtags)):
                if 'title' in divtags[i].get_attribute('class'):
                    Date = divtags[i].find_element_by_css_selector('span[class="date"]').text
                    JournalTitle = divtags[i].find_element_by_tag_name('a').text
                elif 'voice' in divtags[i].get_attribute('class'):
                    if '議長' not in divtags[i].text or '委員長' not in divtags[i].text:
                        Speaker = divtags[i].text
                        if divtags[i-1].get_attribute('class') == 'title':
                            SpeakOrder = 1
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_chb.columns)
                            df_chb = df_chb.append(record,ignore_index=True)
                        elif divtags[i-1].get_attribute('class') == 'voice':
                            num = 1
                            for j in range(1,i):
                                if divtags[i-j].get_attribute('class') == 'voice':
                                    num += 1
                                elif divtags[i-j].get_attribute('class') == 'title':
                                    break
                            SpeakOrder = num
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_chb.columns)
                            df_chb = df_chb.append(record,ignore_index=True)

            nextlinkCandidate = browser.find_element_by_css_selector('div[class="movelist-bottom"]').find_elements_by_tag_name('a')
            if nextlinkCandidate ==[]:
                browser.quit()
            else:
                nextlinkCandidate = browser.find_element_by_css_selector('div[class="movelist-bottom"]').find_elements_by_tag_name('a')
                while "次へ" in nextlinkCandidate[-1].text:
                    nextlinkCandidate = browser.find_element_by_css_selector('div[class="movelist-bottom"]').find_elements_by_tag_name('a')
                    nextlinkCandidate[-1].click()
                    sleep(3)

                    divtags_temp = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol').find_elements_by_tag_name('div')
                    divtags = []
                    for ele in divtags_temp:
                        if 'title' in ele.get_attribute('class'):
                            divtags.append(ele)
                        elif 'voice' in ele.get_attribute('class'):
                            divtags.append(ele)
                    for i in range(len(divtags)):
                        if 'title' in divtags[i].get_attribute('class'):
                            Date = divtags[i].find_element_by_css_selector('span[class="date"]').text
                            JournalTitle = divtags[i].find_element_by_tag_name('a').text
                        elif 'voice' in divtags[i].get_attribute('class'):
                            if '議長' not in divtags[i].text or '委員長' not in divtags[i].text:
                                Speaker = divtags[i].text
                                if 'title' in divtags[i-1].get_attribute('class'):
                                    SpeakOrder = 1
                                    record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_chb.columns)
                                    df_chb = df_chb.append(record,ignore_index=True)
                                elif 'voice' in divtags[i-1].get_attribute('class'):
                                    num = 1
                                    for j in range(1,i):
                                        if divtags[i-j].get_attribute('class') == 'voice':
                                            num += 1
                                        elif divtags[i-j].get_attribute('class') == 'title':
                                            break
                                    SpeakOrder = num
                                    record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_chb.columns)
                                    df_chb = df_chb.append(record,ignore_index=True)

                    nextlinkCandidate = browser.find_element_by_css_selector('div[class="movelist-bottom"]').find_elements_by_tag_name('a')

                else:
                    browser.quit()
                    
    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_chb.columns)
        df_chb = df_chb.append(record,ignore_index=True)
        browser.quit()

    return df_chb


# In[3]:


if __name__ == '__main__':
    chb_s()

