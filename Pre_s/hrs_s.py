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


#広島
def hrs_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='B']['URL'][33]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='B']['name'][33]
    df_hrs = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        links_atag = browser.find_elements_by_tag_name('a')
        for link in links_atag:
            if 'search-meeting' in link.get_attribute('href'):
                search_step =link
        search_step.click()                
        sleep(1)

        #会議種類の選択
        MTList = browser.find_element_by_id('cabinet-is-here').find_elements_by_tag_name('option')
        actions = ActionChains(browser)
        actions.key_down(keys.SHIFT)
        for mt_ele in MTList:
            if '本会議' in mt_ele.text:
                actions.click(mt_ele)
                actions.perform()

        #分類名の選別
        classList = browser.find_element_by_id('class-is-here').find_elements_by_tag_name('option')
        for class_ele in classList:
            if '本文' in class_ele.text:
                class_ele.click()

        browser.find_element_by_css_selector("input[type='submit']").click()
        sleep(1)
        #新しいページに移動
        browser.switch_to.window(browser.window_handles[-1])
        #検索ワード入力
        browser.find_element_by_css_selector("input[type='text']").send_keys(SearchWord) 
        browser.find_element_by_css_selector("input[type='submit']").click()

        sleep(3)
        #新しく開いたｳｨﾝﾄﾞｳに移動
        browser.switch_to.window(browser.window_handles[-1])

        #検索結果の全ての文書のaタグ情報を取得
        org_window = browser.current_window_handle
        JURLList2_step1 = browser.find_elements_by_css_selector('div[class="result-list"]') #広島、佐賀

        if browser.find_elements_by_css_selector('div[class="result-list-nohit"]') != []:
            not_applicable = '該当する文書は存在しません。。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_hrs.columns)
            df_hrs = df_hrs.append(record,ignore_index=True)
            browser.quit()

        else:
            for i in range(len(JURLList2_step1)):
                JURLList2_step1 = browser.find_elements_by_css_selector('div[class="result-list"]')
                Date = JURLList2_step1[i].find_element_by_css_selector('span[class="result-document-date"]').text
                JournalTitle = JURLList2_step1[i].find_element_by_css_selector('div[class="result-document"]').find_element_by_tag_name('a').text
                voise_list = JURLList2_step1[i].find_elements_by_css_selector('div[class="result-voice-list"]')
                num = 1
                for j in range(len(voise_list)):
                    Speaker = voise_list[j].find_element_by_tag_name('a').text
                    if '議長' not in Speaker and '委員長' not in Speaker:
                        SpeakOrder = num
                        Name = BookMarkName
                        record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_hrs.columns)
                        df_hrs = df_hrs.append(record,ignore_index=True)
                        num += 1

            while browser.find_element_by_class_name("pagination").find_elements_by_tag_name('span')[-1].find_elements_by_tag_name('a') != []:
                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('span')[-1].find_element_by_tag_name('a').click()
                sleep(2)
                JURLList2_step1 = browser.find_elements_by_css_selector('div[class="result-list"]')
                for i in range(len(JURLList2_step1)):
                    JURLList2_step1 = browser.find_elements_by_css_selector('div[class="result-list"]')
                    Date = JURLList2_step1[i].find_element_by_css_selector('span[class="result-document-date"]').text
                    JournalTitle = JURLList2_step1[i].find_element_by_css_selector('div[class="result-document"]').find_element_by_tag_name('a').text
                    voise_list = JURLList2_step1[i].find_elements_by_css_selector('div[class="result-voice-list"]')
                    num = 1
                    for j in range(len(voise_list)):
                        Speaker = voise_list[j].find_element_by_tag_name('a').text
                        if '議長' not in Speaker and '委員長' not in Speaker:
                            SpeakOrder = num
                            Name = BookMarkName
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_hrs.columns)
                            df_hrs = df_hrs.append(record,ignore_index=True)
                            num += 1

                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('span')[-1].find_elements_by_tag_name('a')

            browser.quit()

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_hrs.columns)
        df_hrs = df_hrs.append(record,ignore_index=True)
        browser.quit()
        
    return df_hrs


if __name__ == '__main__':
    hrs_s()

