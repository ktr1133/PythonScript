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


#福岡
def fko_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='B']['URL'][39]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='B']['name'][39]
    df_fko = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        browser.find_element_by_class_name('start').find_element_by_tag_name('a').click()
        sleep(1)
        for ele in browser.find_elements_by_class_name('glink__item'):
            try:
                if 'search-meeting' in ele.get_attribute('href'):
                    link = ele
            except TypeError:
                pass
        link.click()
        sleep(1)
        MTList = browser.find_element_by_id('cabinet1').find_elements_by_tag_name('option')
        actions = ActionChains(browser)
        actions.key_down(keys.SHIFT)
        for mt_ele in MTList:
            if '本会議' in mt_ele.text:
                actions.click(mt_ele)
                actions.perform()
        #分類選択肢がないルートの設定
        #分類名の選別
        classList = browser.find_element_by_id('class1').find_elements_by_tag_name('option')
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
        if browser.find_elements_by_css_selector('div[class="result-doc--nohit"]') != []:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_fko.columns)
            df_fko = df_fko.append(record,ignore_index=True)
            browser.quit()

        else:    
            #発言、会議名、議会日時取得
            Name = BookMarkName
            browser.find_element_by_css_selector('p[class="result-display__item"] > a[class="btn"]').click()
            sleep(4)
            JURLList1_step1 = browser.find_elements_by_class_name("result-doc")
            for i in range(len(JURLList1_step1)):
                JournalTitle = JURLList1_step1[i].find_element_by_css_selector('a[class="result-title__name"]').text
                Date = re.sub('開催日: ', '', JURLList1_step1[i].find_element_by_css_selector("span[class='result-title__date']").text)
                voices = JURLList1_step1[i].find_elements_by_css_selector('div[class="result-voice"]')
                num = 1
                for j in range(len(voices)):
                    Speaker = voices[j].find_element_by_tag_name('a').text
                    if '議長' not in Speaker or '委員長' not in Speaker:
                        SpeakOrder = num
                        record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_fko.columns)
                        df_fko = df_fko.append(record,ignore_index=True)
                        num += 1

            while browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-2].find_elements_by_tag_name('a') != []:
                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-2].find_element_by_tag_name('a').click()
                sleep(2)
                browser.switch_to.window(browser.window_handles[-1])
                org_window = browser.current_window_handle

                JURLList1_step1 = browser.find_elements_by_class_name("result-doc")
                for i in range(len(JURLList1_step1)):
                    JournalTitle = JURLList1_step1[i].find_element_by_css_selector('a[class="result-title__name"]').text
                    Date = re.sub('開催日: ', '', JURLList1_step1[i].find_element_by_css_selector("span[class='result-title__date']").text)
                    voices = JURLList1_step1[i].find_elements_by_css_selector('div[class="result-voice"]')
                    num = 1
                    for j in range(len(voices)):
                        Speaker = voices[j].find_element_by_tag_name('a').text
                        if '議長' not in Speaker or '委員長' not in Speaker:
                            SpeakOrder = num
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_fko.columns)
                            df_fko = df_fko.append(record,ignore_index=True)
                            num += 1

            browser.quit()
        
    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_fko.columns)
        df_fko = df_fko.append(record,ignore_index=True)
        browser.quit()
        
    return df_fko


# In[ ]:


if __name__ == '__main__':
    fko_s()

