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


#鹿児島
def kgs_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='B']['URL'][45]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='B']['name'][45]
    df_kgs = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        for ele in browser.find_elements_by_tag_name('a'):
            if 'search-meeting' in ele.get_attribute('href'):
                link = ele
        link.click()
        MTList = browser.find_element_by_name('Cabinet[]').find_elements_by_tag_name('option')
        actions = ActionChains(browser)
        actions.key_down(keys.SHIFT)
        for mt_ele in MTList:
            if '本会議' in mt_ele.text:
                actions.click(mt_ele)
                actions.perform()
        #文書種類の選別
        classList = browser.find_element_by_name('Class[]').find_elements_by_tag_name('option')
        for class_ele in classList:
            if '本文' in class_ele.text:
                class_ele.click()
        browser.find_element_by_css_selector("input[type='submit']").click()
        sleep(1)
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
        nohit_temp = browser.find_elements_by_class_name("result-document") #青森、茨城、東京、福井、富山、山梨、愛知、京都、島根、福岡、鹿児島
        if nohit_temp[0].find_elements_by_css_selector('div[class="nohit"]') != []:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_kgs.columns)
            df_kgs = df_kgs.append(record,ignore_index=True)
            browser.quit()

        else:
            JURLList1_step1 = browser.find_elements_by_class_name("result-doc")
            for i in range(len(JURLList1_step1)):
                Date = JURLList1_step1[i].find_element_by_css_selector('span[class="result-title__date"]').text
                JournalTitle = JURLList1_step1[i].find_element_by_css_selector('a[class="result-title__name"]').text
                divtags = JURLList1_step1[i].find_elements_by_class_name('result-voice')
                num = 1
                for j in range(len(divtags)):
                    if not '議長' in divtags[j].find_element_by_tag_name('a').text:
                        Speaker = divtags[j].find_element_by_tag_name('a').text
                        SpeakOrder = num
                        Name = BookMarkName
                        record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_kgs.columns)
                        df_kgs = df_kgs.append(record,ignore_index=True)
                        num += 1

            while browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_elements_by_tag_name('a') != []:
                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_element_by_tag_name('a').click()
                sleep(2)
                browser.switch_to.window(browser.window_handles[-1])
                org_window = browser.current_window_handle
                JURLList1_step1 = browser.find_elements_by_class_name("result-doc")
                for i in range(len(JURLList1_step1)):
                    Date = JURLList1_step1[i].find_element_by_css_selector('span[class="result-title__date"]').text
                    JournalTitle = JURLList1_step1[i].find_element_by_css_selector('a[class="result-title__name"]').text
                    divtags = JURLList1_step1[i].find_elements_by_class_name('result-voice')
                    num = 1
                    for j in range(len(divtags)):
                        if not '議長' in divtags[j].find_element_by_tag_name('a').text:
                            Speaker = divtags[j].find_element_by_tag_name('a').text
                            SpeakOrder = num
                            Name = BookMarkName
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_kgs.columns)
                            df_kgs = df_kgs.append(record,ignore_index=True)
                            num += 1

            browser.quit()


    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_kgs.columns)
        df_kgs = df_kgs.append(record,ignore_index=True)
        browser.quit()

    return df_kgs


# In[ ]:


if __name__ == '__main__':
    kgs_s()

