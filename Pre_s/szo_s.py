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


#静岡
def szo_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='H']['URL'][21]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='H']['name'][21]
    df_szo = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        if '　' in SearchWord:
            SearchWords = SearchWord.split('　')
            SearchWordInputs_temp = browser.find_elements_by_css_selector('input[name^="word"]')
            SearchWordInputs = []
            for i in range(len(SearchWords)):
                SearchWordInputs.append(SearchWordInputs_temp[i])
            for ele1,ele2 in zip(SearchWords, SearchWordInputs):
                ele2.send_keys(ele1)
        elif ' ' in SearchWord:
            SearchWords = SearchWord.split(' ')
            SearchWordInputs_temp = browser.find_elements_by_css_selector('input[name^="word"]')
            SearchWordInputs = []
            for i in range(len(SearchWords)):
                SearchWordInputs.append(SearchWordInputs_temp[i])
            for ele1,ele2 in zip(SearchWords, SearchWordInputs):
                ele2.send_keys(ele1)
        else:
            browser.find_element_by_css_selector('input[name="word11"]').send_keys(SearchWord)
        
        sleep(1)
        browser.find_element_by_css_selector('input[value="上記条件で検索を開始する"]').click()
        sleep(3)

        resultlist_temp = browser.find_element_by_id('tmp_contents').find_elements_by_tag_name('tbody')
        if resultlist_temp == []:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_szo.columns)
            df_szo = df_szo.append(record,ignore_index=True)
            browser.quit()
        else:
            resultlist = browser.find_element_by_id('tmp_contents').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
            record_temps = []
            de_records1 = []
            de_records2 = []
            de_records3 = []
            for i in range(len(resultlist)):
                resultlist = browser.find_element_by_id('tmp_contents').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
                if resultlist[i].find_elements_by_tag_name('td') != []:
                    if '一般質問' in resultlist[i].find_elements_by_tag_name('td')[1].text:
                        JournalTitle = resultlist[i].find_elements_by_tag_name('td')[3].text
                        resultlist[i].find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').click()
                        sleep(3)
                        Speaker_and_Date_and_PoliticalParty_temp = browser.find_element_by_id('tmp_contents').find_element_by_tag_name('table').find_elements_by_tag_name('tr')
                        Speaker_temp0 = Speaker_and_Date_and_PoliticalParty_temp[0].find_elements_by_tag_name('td')[2].find_elements_by_tag_name('b')[0].text
                        Speaker = re.sub('　', '', Speaker_temp0)
                        Date = Speaker_and_Date_and_PoliticalParty_temp[2].find_elements_by_tag_name('td')[2].text
                        if '議長' not in Speaker:
                            SpeakOrder = 'temp'
                            Name = BookMarkName
                            record_temp = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_szo.columns)
                            record_temps.append(record_temp)

                        browser.back()
                        sleep(3)


                    elif '代表質問' in resultlist[i].find_elements_by_tag_name('td')[1].text:
                        JournalTitle = resultlist[i].find_elements_by_tag_name('td')[3].text
                        resultlist[i].find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').click()
                        sleep(3)
                        Speaker_and_Date_and_PoliticalParty_temp = browser.find_element_by_id('tmp_contents').find_element_by_tag_name('table').find_elements_by_tag_name('tr')
                        Speaker_temp0 = Speaker_and_Date_and_PoliticalParty_temp[0].find_elements_by_tag_name('td')[2].find_elements_by_tag_name('b')[0].text
                        Speaker = re.sub('　', '', Speaker_temp0)
                        Date = Speaker_and_Date_and_PoliticalParty_temp[2].find_elements_by_tag_name('td')[2].text
                        PoliticalParty = Speaker_and_Date_and_PoliticalParty_temp[3].find_elements_by_tag_name('td')[2].text
                        if '議長' not in Speaker:
                            SpeakOrder = 'temp'
                            Name = BookMarkName
                            record_temp = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_szo.columns)
                            record_temps.append(record_temp)

                        browser.back()
                        sleep(3)

                    elif '答弁' in resultlist[i].find_elements_by_tag_name('td')[1].text:
                        JournalTitle = resultlist[i].find_elements_by_tag_name('td')[3].text
                        resultlist[i].find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').click()
                        sleep(3)
                        Speaker_temp = browser.find_element_by_id('tmp_contents').find_element_by_tag_name('tbody').find_element_by_css_selector('tr[valign="top"]').find_elements_by_tag_name('td')[3].text
                        if '（再質問）' in Speaker_temp:
                            Speaker_temp = re.sub('（再質問）', '', Speaker_temp)
                        Date = browser.find_element_by_id('tmp_contents').find_element_by_css_selector('div[align="right"]').find_elements_by_tag_name('b')[1].text
                        Remark_temp9 = browser.find_element_by_id('tmp_contents').find_elements_by_tag_name('font')
                        Remark_temp10 = []
                        for ele5 in Remark_temp9:
                            Remark_temp10.append(ele5.text)
                        Remark_temp11 = ''.join(Remark_temp10)    
                        Remark_temp12 = re.split("(?=○)", Remark_temp11)
                        for ele6 in Remark_temp12:
                            if Speaker_temp in ele6:
                                if '議長' not in ele6:
                                    if SearchWord in ele6:
                                        Speaker = ele6.split('　')[0]
                                        SpeakOrder = 'temp'
                                        Name = BookMarkName
                                        record_temp = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_szo.columns)
                                        record_temps.append(record_temp)

                        browser.back()
                        sleep(3)

                    else:
                        pass

                else:
                    pass

            browser.quit()    
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
                        record_temps[k]['SpeakOrder'] = 1

            for record in record_temps:            
                df_szo = df_szo.append(record,ignore_index=True)

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_szo.columns)
        df_szo = df_szo.append(record,ignore_index=True)
        browser.quit()

    return df_szo


if __name__ == '__main__':
    szo_s()

