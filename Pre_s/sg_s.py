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


#佐賀
def sg_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='B']['URL'][40]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='B']['name'][40]
    df_sg = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])

    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        browser.find_element_by_tag_name('textarea').send_keys(SearchWord) 
        #会議種類の選択
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

        sleep(3)
        #新しく開いたｳｨﾝﾄﾞｳに移動
        browser.switch_to.window(browser.window_handles[-1])

        #検索結果の全ての文書のaタグ情報を取得
        org_window = browser.current_window_handle
        JURLList2_step1 = browser.find_elements_by_css_selector('div[class="result-list"]') #広島、佐賀
        divtags = browser.find_element_by_css_selector('div[class="result"]').find_elements_by_tag_name('div')

        if browser.find_elements_by_css_selector('div[class="result-list-nohit"]') != []:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_sg.columns)
            df_sg = df_sg.append(record,ignore_index=True)
            browser.quit()

        else:
            for i in range(len(divtags)):
                divtags = browser.find_element_by_css_selector('div[class="result"]').find_elements_by_tag_name('div')
                if 'result-list' in divtags[i].get_attribute('class'):
                    Date = re.sub('開催日：', '', divtags[i].find_element_by_css_selector("span[class='result-document-date']").text)
                    JournalTitle = divtags[i].find_element_by_tag_name('a').text
                elif 'result-voice-list' in divtags[i].get_attribute('class'):
                    Speaker = divtags[i].find_element_by_tag_name('a').text
                    if divtags[i-1].get_attribute('class') == 'result-list':
                        SpeakOrder = 1
                        Name = BookMarkName
                        record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_sg.columns)
                        df_sg = df_sg.append(record,ignore_index=True)
                    elif divtags[i-1].get_attribute('class') == 'result-voice-text':
                        num = 1
                        for j in range(1,i):
                            if divtags[i-j].get_attribute('class') == 'result-voice-list':
                                num += 1
                            elif divtags[i-j].get_attribute('class') == 'result-list':
                                break
                        SpeakOrder = num
                        Name = BookMarkName
                        record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_sg.columns)
                        df_sg = df_sg.append(record,ignore_index=True)

            while browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_elements_by_tag_name('a') != []:
                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_element_by_tag_name('a').click()
                sleep(2)
                browser.switch_to.window(browser.window_handles[-1])
                divtags = browser.find_element_by_css_selector('div[class="result"]').find_elements_by_tag_name('div')
                for i in range(len(divtags)):
                    divtags = browser.find_element_by_css_selector('div[class="result"]').find_elements_by_tag_name('div')
                    if 'result-list' in divtags[i].get_attribute('class'):
                        Date = re.sub('開催日：', '', divtags[i].find_element_by_css_selector("span[class='result-document-date']").text)
                        JournalTitle = divtags[i].find_element_by_tag_name('a').text
                    elif 'result-voice-list' in divtags[i].get_attribute('class'):
                        Speaker = divtags[i].find_element_by_tag_name('a').text
                        if divtags[i-1].get_attribute('class') == 'result-list':
                            SpeakOrder = 1
                            Name = BookMarkName
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_sg.columns)
                            df_sg = df_sg.append(record,ignore_index=True)
                        elif divtags[i-1].get_attribute('class') == 'result-voice-text':
                            num = 1
                            for j in range(1,i):
                                if divtags[i-j].get_attribute('class') == 'result-voice-list':
                                    num += 1
                                elif divtags[i-j].get_attribute('class') == 'result-list':
                                    break
                            SpeakOrder = num
                            Name = BookMarkName
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_sg.columns)
                            df_sg = df_sg.append(record,ignore_index=True)

                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_elements_by_tag_name('a')

            browser.quit()

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_sg.columns)
        df_sg = df_sg.append(record,ignore_index=True)
        browser.quit()
        
    return df_sg


# In[ ]:


if __name__ == '__main__':
    sg_s()

