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


#愛知
def aic_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='B']['URL'][22]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='B']['name'][22]
    df_aic = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        links = browser.find_elements_by_class_name('nav-searchlink')
        hrefs = []
        for link in links:
            hrefs.append(link.get_attribute('href'))
        for href in hrefs:
            if 'search-meeting' in href:
                browser.close()
                MTurl = urljoin(BookMarkURL, href)
                browser = webdriver.Chrome(ChromeDriverManager().install())
                sleep(3)
                browser.get(MTurl)
                #会議種類の選択
                MTList = browser.find_element_by_id('cabinet').find_elements_by_tag_name('option')
                actions = ActionChains(browser)
                actions.key_down(keys.SHIFT)
                for mt_ele in MTList:
                    if '本会議' in mt_ele.text:
                        actions.click(mt_ele)
                        actions.perform()

                #文書種類の選別
                classList = browser.find_element_by_id('class').find_elements_by_tag_name('option')
                for class_ele in classList:
                    if '本文' in class_ele.text:
                        class_ele.click()

                browser.find_element_by_css_selector("button[type='submit']").click()
                sleep(1)
                #新しいページに移動
                browser.switch_to.window(browser.window_handles[-1])
                #検索ワード入力
                browser.find_element_by_css_selector("input[type='text']").send_keys(SearchWord) 
                #検索実行
                browser.find_element_by_css_selector("button[type='submit']").click()

        sleep(3)
        #新しく開いたｳｨﾝﾄﾞｳに移動
        browser.switch_to.window(browser.window_handles[-1])

        #検索結果の全ての文書のaタグ情報を取得
        org_window = browser.current_window_handle
        JURLList1_step1 = browser.find_elements_by_class_name("result-doc") #青森、茨城、東京、福井、富山、山梨、愛知、京都、島根、福岡
        if JURLList1_step1 == []:
            not_applicable = browser.find_element_by_class_name('result-nohit__title').text
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_aic.columns)
            df_aic = df_aic.append(record,ignore_index=True)
            browser.quit()

        else:
            Name = BookMarkName
            JURLList1_step1 = browser.find_elements_by_class_name("result-doc")
            for i in range(len(JURLList1_step1)):
                JournalTitle = JURLList1_step1[i].find_element_by_css_selector('div[class="result-doc__title"]').find_element_by_tag_name('a').text
                Date = JURLList1_step1[i].find_element_by_css_selector('div[class="result-doc__date"]').text.split(': ')[1]
                voices = JURLList1_step1[i].find_elements_by_css_selector('div[class="result-voice"]')
                num = 1
                for j in range(len(voices)):
                    Speaker = voices[j].find_element_by_tag_name('a').text
                    if '議長' not in Speaker and '委員長' not in Speaker:
                        SpeakOrder = num
                        record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_aic.columns)
                        df_aic = df_aic.append(record,ignore_index=True)
                        num += 1

            nextlink = browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_elements_by_tag_name('a')
            while nextlink != []:
                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_element_by_tag_name('a').click()
                sleep(2)
                browser.switch_to.window(browser.window_handles[-1])
                org_window = browser.current_window_handle

                JURLList1_step1 = browser.find_elements_by_class_name("result-doc")
                for i in range(len(JURLList1_step1)):
                    JournalTitle = JURLList1_step1[i].find_element_by_css_selector('div[class="result-doc__title"]').find_element_by_tag_name('a').text
                    Date = JURLList1_step1[i].find_element_by_css_selector('div[class="result-doc__date"]').text.split(': ')[1]
                    voices = JURLList1_step1[i].find_elements_by_css_selector('div[class="result-voice"]')
                    num = 1
                    for j in range(len(voices)):
                        Speaker = voices[j].find_element_by_tag_name('a').text
                        if '議長' not in Speaker and '委員長' not in Speaker:
                            SpeakOrder = num
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_aic.columns)
                            df_aic = df_aic.append(record,ignore_index=True)
                            num += 1

                nextlink = browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_elements_by_tag_name('a')

            browser.quit()
            
    except:
        error = 'error'
        Name = BookMarkName
        SearchWord = SearchWord
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_aic.columns)
        df_aic = df_aic.append(record,ignore_index=True)
        browser.quit()

    return df_aic


# In[ ]:


if __name__ == '__main__':
    aic_s()

