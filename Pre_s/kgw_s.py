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


#香川 #特殊事例
def kgw_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='G']['URL'][36]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='G']['name'][36]
    df_kgw = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        #検索ワード入力
        browser.find_element_by_id('content').find_element_by_css_selector('input[name="Phrase[]"]').send_keys(SearchWord)
        #文書の選択
        browser.find_element_by_id('cabinet1').click()
        browser.find_element_by_id('cabinet2').click()
        #分類の選択
        browser.find_element_by_id('classes1').click()
        #検索の実行
        sleep(1)
        browser.find_element_by_css_selector('li[class="submit"]').find_element_by_tag_name('a').click()

        #開いたﾍﾟｰｼﾞに移動
        browser.switch_to.window(browser.window_handles[-1])

        resultTable = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol')
        documents = resultTable.find_elements_by_class_name('title')
        divtags = resultTable.find_elements_by_tag_name('div')
        if documents == []:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_kgw.columns)
            df_kgw = df_kgw.append(record,ignore_index=True)
        else:
            for i in range(len(divtags)):
                if 'title' in divtags[i].get_attribute('class'):
                    Date = divtags[i].find_element_by_tag_name('span').text.split('：')[1]
                    JournalTitle = divtags[i].find_element_by_tag_name('a').text
                elif 'voice' in divtags[i].get_attribute('class'):
                    Speaker = divtags[i].find_element_by_tag_name('a').text
                    if divtags[i-1].get_attribute('class') == 'title':
                        SpeakOrder = 1
                        Name = BookMarkName
                        record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_kgw.columns)
                        df_kgw = df_kgw.append(record,ignore_index=True)
                    else:
                        num = 1
                        for j in range(1,i):
                            if divtags[i-j].get_attribute('class') == 'voice':
                                num += 1
                            elif divtags[i-j].get_attribute('class') == 'title':
                                break
                        SpeakOrder = num
                        Name = BookMarkName
                        record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_kgw.columns)
                        df_kgw = df_kgw.append(record,ignore_index=True)


            nextlinkCandidate = browser.find_element_by_css_selector('div[class="pagination"]').find_elements_by_tag_name('a')
            if nextlinkCandidate ==[]:
                browser.quit()
            else:
                nextlinkCandidate = browser.find_element_by_css_selector('div[class="pagination"]').find_elements_by_tag_name('a')
                while "次" in nextlinkCandidate[-1].text:
                    nextlinkCandidate = browser.find_element_by_css_selector('div[class="pagination"]').find_elements_by_tag_name('a')
                    nextlinkCandidate[-1].click()
                    sleep(3)

                    resultTable = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol')
                    divtags = resultTable.find_elements_by_tag_name('div')
                    for i in range(len(divtags)):
                        if 'title' in divtags[i].get_attribute('class'):
                            Date = divtags[i].find_element_by_tag_name('span').text.split('：')[1]
                            JournalTitle = divtags[i].find_element_by_tag_name('a').text
                        elif 'voice' in divtags[i].get_attribute('class'):
                            Speaker = divtags[i].find_element_by_tag_name('a').text
                            if divtags[i-1].get_attribute('class') == 'title':
                                SpeakOrder = 1
                                Name = BookMarkName
                                record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_kgw.columns)
                                df_kgw = df_kgw.append(record,ignore_index=True)
                            else:
                                num = 1
                                for j in range(1,i):
                                    if divtags[i-j].get_attribute('class') == 'voice':
                                        num += 1
                                    elif divtags[i-j].get_attribute('class') == 'title':
                                        break
                                SpeakOrder = num
                                Name = BookMarkName
                                record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_kgw.columns)
                                df_kgw = df_kgw.append(record,ignore_index=True)

                    nextlinkCandidate = browser.find_element_by_css_selector('div[class="pagination"]').find_elements_by_tag_name('a')

                else:
                    browser.quit()

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_kgw.columns)
        df_kgw = df_kgw.append(record,ignore_index=True)
        browser.quit()
                    
    return df_kgw


# In[ ]:


if __name__ == '__main__':
    kgw_s()

