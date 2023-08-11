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


#石川
def isk_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='E']['URL'][16]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='E']['name'][16]
    df_isk = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        if '　' in SearchWord:
            SearchWords = SearchWord.split('　')
            SearchWordInputs_temp = browser.find_elements_by_css_selector('input[class="i_key_t"]')
            SearchWordInputs = []
            for i in range(len(SearchWords)):
                SearchWordInputs.append(SearchWordInputs_temp[i])
            for ele1,ele2 in zip(SearchWords, SearchWordInputs):
                ele2.send_keys(ele1)
        elif ' ' in SearchWord:
            SearchWords = SearchWord.split(' ')
            SearchWordInputs_temp = browser.find_elements_by_css_selector('input[class="i_key_t"]')
            SearchWordInputs = []
            for i in range(len(SearchWords)):
                SearchWordInputs.append(SearchWordInputs_temp[i])
            for ele1,ele2 in zip(SearchWords, SearchWordInputs):
                ele2.send_keys(ele1)
        else:
            SearchWordInput = browser.find_element_by_id('qzs_suggest_start1')
            SearchWordInput.send_keys(SearchWord)

        #発言者種別選択
        browser.find_element_by_id('KTYP_01').click()
        browser.find_element_by_id('KTYP_04').click()

        #会議種類の選択
        browser.find_element_by_id('kgtp2').click()
        browser.find_element_by_id('kgtp3').click()
        browser.find_element_by_id('kgtp4').click()

        #検索実行SearchExecution
        browser.find_element_by_css_selector("input[value='検索実行']").click()                    

        sleep(3)

        browser.switch_to.frame('BOTTOM')

        #【最新年度】議事録のURL保存
        JURLs_temp1 = browser.find_elements_by_tag_name('table')
        if JURLs_temp1 == []:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_isk.columns)
            df_isk = df_isk.append(record,ignore_index=True)
            browser.quit()

        else:
            JURLs_temp2 = browser.find_elements_by_tag_name('table')[1].find_elements_by_css_selector('a[target="HLD_WIN"]')
            org_window = browser.current_window_handle
            for i in range(len(JURLs_temp2)):
                JURLs_temp2 = browser.find_elements_by_tag_name('table')[1].find_elements_by_css_selector('a[target="HLD_WIN"]')
                JURLs_temp2[i].click()
                sleep(3)
                browser.switch_to.window(browser.window_handles[-1]) #新しく開いたｳｨﾝﾄﾞｳに移動
                sleep(3)

                browser.switch_to.frame('header')
                JournalTitle = browser.find_element_by_tag_name('span').text.split('－')[0]
                Date = JournalTitle.split('年')[0]+"年"+browser.find_element_by_tag_name('span').text.split('－')[1].split('-')[0]
                browser.switch_to_default_content()
                browser.switch_to.frame('sidebar')
                speakers_temp1 = browser.find_elements_by_css_selector('td[bgcolor="yellow"]')
                num = 1
                for j in range(len(speakers_temp1)):
                    Speaker = speakers_temp1[j].text
                    SpeakOrder = num
                    Name = BookMarkName
                    record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_isk.columns)
                    df_isk = df_isk.append(record,ignore_index=True)
                    num = num+1
                browser.switch_to.window(org_window) #元いたｳｨﾝﾄﾞｳに戻る
                browser.switch_to.frame('BOTTOM')

            #次ﾍﾟｰｼﾞの有無確認    
            nextlink_candidates = browser.find_element_by_tag_name('tbody').find_element_by_css_selector('td[align="RIGHT"]').find_elements_by_tag_name('a')
            if nextlink_candidates == []:
                pass
            else:
                nextlink = []
                for k in range(len(nextlink_candidates)):
                    nextlink_candidates = browser.find_element_by_tag_name('tbody').find_element_by_css_selector('td[align="RIGHT"]').find_elements_by_tag_name('a')
                    if '次ページ' in nextlink_candidates[k].text:
                        nextlink.append(nextlink_candidates[k])
                while nextlink != []:
                    nextlink[0].click()
                    sleep(2)

                    JURLs_temp2 = browser.find_elements_by_tag_name('table')[1].find_elements_by_css_selector('a[target="HLD_WIN"]')
                    org_window = browser.current_window_handle
                    for i in range(len(JURLs_temp2)):
                        JURLs_temp2 = browser.find_elements_by_tag_name('table')[1].find_elements_by_css_selector('a[target="HLD_WIN"]')
                        JURLs_temp2[i].click()
                        sleep(3)
                        browser.switch_to.window(browser.window_handles[-1]) #新しく開いたｳｨﾝﾄﾞｳに移動
                        sleep(1)
                        browser.switch_to.frame('header')
                        JournalTitle = browser.find_element_by_tag_name('span').text.split('－')[0]
                        Date = JournalTitle.split('年')[0]+"年"+browser.find_element_by_tag_name('span').text.split('－')[1].split('-')[0]
                        browser.switch_to_default_content()
                        browser.switch_to.frame('sidebar')
                        speakers_temp1 = browser.find_elements_by_css_selector('td[bgcolor="yellow"]')
                        num = 1
                        for j in range(len(speakers_temp1)):
                            Speaker = speakers_temp1[j].text
                            SpeakOrder = num
                            Name = BookMarkName
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_isk.columns)
                            df_isk = df_isk.append(record,ignore_index=True)
                            num = num+1
                        browser.switch_to.window(org_window) #元いたｳｨﾝﾄﾞｳに戻る
                        browser.switch_to.frame('BOTTOM')

                    nextlink_candidates = browser.find_element_by_tag_name('tbody').find_element_by_css_selector('td[align="RIGHT"]').find_elements_by_tag_name('a')
                    nextlink = []
                    for l in range(len(nextlink_candidates)):
                        nextlink_candidates = browser.find_element_by_tag_name('tbody').find_element_by_css_selector('td[align="RIGHT"]').find_elements_by_tag_name('a')
                        if '次ページ' in nextlink_candidates[l].text:
                            nextlink.append(nextlink_candidates[l])

            browser.quit()

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_isk.columns)
        df_isk = df_isk.append(record,ignore_index=True)
        browser.quit()
            
    return df_isk


# In[ ]:


if __name__ == '__main__':
    isk_s()

