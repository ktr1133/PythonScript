#!/usr/bin/env python
# coding: utf-8

# In[ ]:
#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import sqlite3
import pandas as pd
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
#処理測定
from tqdm import tqdm
import time

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')


#千葉
def chiba(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='G']['URL'][11]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='G']['name'][11]
    df_chb = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
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

        resultTable = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol')
        documents = resultTable.find_elements_by_class_name('title')
        if documents == []:
            not_applicable = '該当する文書がありません'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_chb.columns)
            df_chb = df_chb.append(record,ignore_index=True)
        else:
            for i in range(len(documents)):
                documents = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol').find_elements_by_class_name('title')
                Date = documents[i].find_element_by_tag_name('span').text
                JournalTitle = documents[i].find_element_by_tag_name('a').text
                documents[i].find_element_by_tag_name('a').click()
                sleep(3)
                iframe = browser.find_element_by_css_selector('frameset')
                browser.switch_to.frame('Voicelist')
                browser.find_element_by_id('list')
                speakerCandidates_temp = browser.find_element_by_id('list').find_elements_by_tag_name('li')
                num = 1
                for j in range(len(speakerCandidates_temp)):
                    speakerCandidates_temp = browser.find_element_by_id('list').find_elements_by_css_selector('li')
                    speakerCandidates_temp2 = speakerCandidates_temp[j].find_elements_by_tag_name('strong')
                    if speakerCandidates_temp2 != []:
                        Speaker = speakerCandidates_temp[j].find_element_by_tag_name('strong').text
                        if '議長' not in Speaker and '委員長' not in Speaker:
                            SpeakOrder = num
                            speakerCandidates_temp[j].find_element_by_tag_name('a').click()
                            sleep(3)
                            browser.switch_to_default_content()
                            browser.switch_to.frame('Page')
                            Remark = browser.find_element_by_id('textcol').find_element_by_tag_name('p').text
                            Name = BookMarkName
                            record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_chb.columns)
                            df_chb = df_chb.append(record,ignore_index=True)
                            num = num+1
                            browser.switch_to_default_content()
                            browser.switch_to.frame('Voicelist')
                browser.switch_to_default_content()
                browser.switch_to.frame('Command')
                browser.find_element_by_css_selector('li[class="list"]').find_element_by_tag_name('a').click()
                sleep(3)

            nextlinkCandidate = browser.find_element_by_css_selector('div[class="movelist-bottom"]').find_elements_by_tag_name('a')
            if nextlinkCandidate ==[]:
                browser.quit()
            else:
                nextlinkCandidate = browser.find_element_by_css_selector('div[class="movelist-bottom"]').find_elements_by_tag_name('a')
                while "次へ" in nextlinkCandidate[-1].text:
                    nextlinkCandidate = browser.find_element_by_css_selector('div[class="movelist-bottom"]').find_elements_by_tag_name('a')
                    nextlinkCandidate[-1].click()
                    sleep(3)

                    resultTable = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol')
                    documents = resultTable.find_elements_by_class_name('title')
                    for i in range(len(documents)):
                        documents = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol').find_elements_by_class_name('title')
                        Date = documents[i].find_element_by_tag_name('span').text
                        JournalTitle = documents[i].find_element_by_tag_name('a').text
                        documents[i].find_element_by_tag_name('a').click()
                        sleep(3)
                        iframe = browser.find_element_by_css_selector('frameset')
                        browser.switch_to.frame('Voicelist')
                        browser.find_element_by_id('list')
                        speakerCandidates_temp = browser.find_element_by_id('list').find_elements_by_tag_name('li')
                        num = 1
                        for j in range(len(speakerCandidates_temp)):
                            speakerCandidates_temp = browser.find_element_by_id('list').find_elements_by_css_selector('li')
                            speakerCandidates_temp2 = speakerCandidates_temp[j].find_elements_by_tag_name('strong')
                            if speakerCandidates_temp2 != []:
                                Speaker = speakerCandidates_temp[j].find_element_by_tag_name('strong').text
                                if '議長' not in Speaker and '委員長' not in Speaker:
                                    SpeakOrder = num
                                    speakerCandidates_temp[j].find_element_by_tag_name('a').click()
                                    sleep(3)
                                    browser.switch_to_default_content()
                                    browser.switch_to.frame('Page')
                                    Remark = browser.find_element_by_id('textcol').find_element_by_tag_name('p').text
                                    Name = BookMarkName
                                    record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_chb.columns)
                                    df_chb = df_chb.append(record,ignore_index=True)
                                    num = num+1
                                    browser.switch_to_default_content()
                                    browser.switch_to.frame('Voicelist')
                        browser.switch_to_default_content()
                        browser.switch_to.frame('Command')
                        browser.find_element_by_css_selector('li[class="list"]').find_element_by_tag_name('a').click()
                        sleep(3)

                    nextlinkCandidate = browser.find_element_by_css_selector('div[class="movelist-bottom"]').find_elements_by_tag_name('a')

                else:
                    browser.quit()
    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_chb.columns)
        df_chb = df_chb.append(record,ignore_index=True)
        browser.quit()

    return df_chb


if __name__ == '__main__':
    chiba()
