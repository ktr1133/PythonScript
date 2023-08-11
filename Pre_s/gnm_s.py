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


#群馬
def gnm_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='E']['URL'][9]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='E']['name'][9]
    df_gnm = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)
        Name = BookMarkName

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

        #検索実行SearchExecution
        browser.find_element_by_css_selector("input[type='submit']").click()                    

        sleep(3)

        iframe = browser.find_element_by_css_selector('iframe')
        browser.switch_to.frame(iframe)

        #【最新年度】議事録のURL保存
        JURLs_temp1 = browser.find_elements_by_tag_name('table')
        if JURLs_temp1 == []:
            not_applicable = '該当する発言は存在しません。'
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_gnm.columns)
            df_gnm = df_gnm.append(record,ignore_index=True)
            browser.quit()

        else:
            JURLs_temp1 = browser.find_elements_by_tag_name('table')[1].find_elements_by_css_selector('a[target="HLD_WIN"]')
            org_window = browser.current_window_handle
            for ele1 in JURLs_temp1:
                ele1.click()
                sleep(3)
                browser.switch_to.window(browser.window_handles[-1]) #新しく開いたｳｨﾝﾄﾞｳに移動
                sleep(1)
                browser.switch_to.frame('header')
                JournalTitle = browser.find_element_by_tag_name('span').text.split('－')[0]
                Date = JournalTitle.split('年')[0]+'年'+browser.find_element_by_tag_name('span').text.split('－')[1].split('-')[0]
                browser.switch_to_default_content()
                browser.switch_to.frame('sidebar')
                speakers_temp1 = browser.find_elements_by_css_selector('td[bgcolor="yellow"]')
                num = 1
                for ele in speakers_temp1:
                    Speaker = ele.text
                    if '委員長' not in Speaker:
                        SpeakOrder = num
                        record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_gnm.columns)
                        df_gnm = df_gnm.append(record,ignore_index=True)
                        num = num+1                    
                browser.switch_to.window(browser.window_handles[0]) #元いたｳｨﾝﾄﾞｳに戻る
                browser.switch_to.frame(iframe)

            #次ﾍﾟｰｼﾞの有無確認    
            nextlink_candidates = browser.find_element_by_tag_name('table').find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[1].find_elements_by_tag_name('a')
            if nextlink_candidates == []:
                pass
            else:
                nextlink = []
                for ele in nextlink_candidates:
                    if '次ページ' in ele.text:
                        nextlink.append(ele)
                while nextlink != []:
                    nextlink[0].click()

                    JURLs_temp1 = browser.find_elements_by_tag_name('table')[1].find_elements_by_css_selector('a[target="HLD_WIN"]')
                    org_window = browser.current_window_handle
                    for ele1 in JURLs_temp1:
                        ele1.click()
                        sleep(3)
                        browser.switch_to.window(browser.window_handles[-1]) #新しく開いたｳｨﾝﾄﾞｳに移動
                        sleep(1)
                        browser.switch_to.frame('header')
                        JournalTitle = browser.find_element_by_tag_name('span').text.split('－')[0]
                        Date = JournalTitle.split('年')[0]+'年'+browser.find_element_by_tag_name('span').text.split('－')[1].split('-')[0]
                        browser.switch_to_default_content()
                        browser.switch_to.frame('sidebar')
                        speakers_temp1 = browser.find_elements_by_css_selector('td[bgcolor="yellow"]')
                        num = 1
                        for ele in speakers_temp1:
                            Speaker = ele.text
                            if '委員長' not in Speaker:
                                SpeakOrder = num
                                Name = BookMarkName
                                record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_gnm.columns)
                                df_gnm = df_gnm.append(record,ignore_index=True)
                                num = num+1                    

                        browser.switch_to.window(browser.window_handles[0]) #元いたｳｨﾝﾄﾞｳに戻る
                        browser.switch_to.frame(iframe)
                        nextlink_candidates = browser.find_element_by_tag_name('table').find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[1].find_elements_by_tag_name('a')
                        nextlink = []
                        for ele in nextlink_candidates:
                            if '次ページ' in ele.text:
                                nextlink.append(ele)

            browser.quit()
            
    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_gnm.columns)
        df_gnm = df_gnm.append(record,ignore_index=True)
        browser.quit()
        
    return df_gnm


if __name__ == '__main__':
    gnm_s()

