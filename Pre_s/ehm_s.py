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


# In[ ]:


#愛媛
def ehm_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='I']['URL'][37]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='I']['name'][37]
    df_ehm = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    record_temps = []
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        #検索語の指定
        browser.find_element_by_css_selector('input[name="KeyWord"]').send_keys(SearchWord)
        #会議期間の指定
        dropdown = browser.find_element_by_css_selector('select[name="fromYear"]')
        select = Select(dropdown)
        options = select.options
        browser.find_element_by_css_selector('select[name="fromYear"]').click()
        options[-1].click()
        #検索実行
        browser.find_element_by_css_selector('input[value="検索"]').click()

        browser.implicitly_wait(5)

        temp0 = browser.find_element_by_css_selector('div[id="wrapper"]')
        temp1 = temp0.find_element_by_css_selector('div[class="content4"]')
        temp2 = temp1.find_element_by_css_selector('div[class="content2_1"]')
        key = temp2.find_elements_by_tag_name('table')[2].find_element_by_tag_name('tbody').find_element_by_tag_name('tr')
        resulttext = key.text
        if 'はありませんでした。' in resulttext:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_ehm.columns)
            df_ehm = df_ehm.append(record,ignore_index=True) 
            browser.quit()
        else:
            #調査結果の年ﾘｽﾄ作成
            key1 = browser.find_element_by_css_selector('div[class="content2_1"]').find_elements_by_tag_name('table')
            yearslist_temp = key1[2].find_element_by_tag_name('tbody').find_element_by_tag_name('table').find_elements_by_tag_name('td')
            yearslist = []
            for ele in yearslist_temp:
                if ele.find_elements_by_tag_name('a') != []:
                    yearslist.append(ele)

            #年別にfor文作成
            for i in range(len(yearslist)):
                key1 = browser.find_element_by_css_selector('div[class="content2_1"]').find_elements_by_tag_name('table')
                yearslist_temp = key1[3].find_element_by_tag_name('tbody').find_element_by_tag_name('table').find_elements_by_tag_name('td')
                yearslist = []
                for ele in yearslist_temp:
                    if ele.find_elements_by_tag_name('a') != []:
                        yearslist.append(ele)

                #議事録取得該当年のクリック
                yearslist[i].find_element_by_tag_name('a').click()
                sleep(5)
                #検索結果の件別ﾘｽﾄ作成
                key1 = browser.find_element_by_css_selector('div[class="content2_1"]').find_elements_by_tag_name('table')
                trtags = key1[3].find_elements_by_tag_name('tr')#検索結果の行ﾃﾞｰﾀ格納タグ参照
                resultList = []
                for ele in trtags:
                    tdtags = ele.find_elements_by_tag_name('td')
                    if len(tdtags) == 5:
                        if '会' in tdtags[0].text:
                            resultList.append(ele)

                for j in range(len(resultList)):
                    #繰り返し処理中にﾌﾞﾗｳｻﾞﾊﾞｯｸ処理を行うため、resultListを再作成
                    key1 = browser.find_element_by_css_selector('div[class="content2_1"]').find_elements_by_tag_name('table')
                    trtags = key1[3].find_elements_by_tag_name('tr')#検索結果の行ﾃﾞｰﾀ格納タグ参照
                    resultList = []
                    for ele in trtags:
                        tdtags = ele.find_elements_by_tag_name('td')
                        if len(tdtags) == 5:
                            if '会' in tdtags[0].text:
                                resultList.append(ele)                    
                    #会議名取得
                    JournalTitle = resultList[j].find_elements_by_tag_name('td')[0].text
                    #会議日時取得
                    Date = JournalTitle.split('年')[0]+'年'+resultList[j].find_elements_by_tag_name('td')[1].text.split('号')[1].split('）')[0]
                    #発言者取得
                    Speaker = resultList[j].find_elements_by_tag_name('td')[4].text
                    #その他ﾚｺｰﾄﾞ記載事項
                    Name = BookMarkName
                    SpeakOrder = 'temp'
                    #仮ﾚｺｰﾄﾞ作成
                    record_temp = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_ehm.columns)
                    record_temps.append(record_temp)

                    
    except:
        error = 'error'
        Name = BookMarkName
        record_temp = pd.Series([Name, SearchWord, error, '', '', ''], index=df_ehm.columns)
        record_temps.append(record_temp)
        browser.quit()

    try:
        for k in range(len(record_temps)):
            if k -1 == -1:
                SpeakOrder = 1
                record_temps[k]['SpeakOrder'] = SpeakOrder
            else:
                if record_temps[k]['JournalTitle'] == record_temps[k-1]['JournalTitle']:
                    if record_temps[k]['Date'] == record_temps[k-1]['Date']:
                        record_temps[k]['SpeakOrder'] = record_temps[k-1]['SpeakOrder'] +1
                    else:
                        record_temps[k]['SpeakOrder'] = 1
                else:
                    if record_temps[k]['JournalTitle'] == 'error':
                        pass
                    else:
                        record_temps[k]['SpeakOrder'] = 1

        browser.quit()
        for record in record_temps:            
            df_ehm = df_ehm.append(record,ignore_index=True)

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_ehm.columns)
        df_ehm = df_ehm.append(record,ignore_index=True)
        browser.quit()
        
    return df_ehm


if __name__ == '__main__':
    ehm_s()

