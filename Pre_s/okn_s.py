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


#沖縄
def okn_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='M']['URL'][46]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='M']['name'][46]
    df_okn = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        #ﾌﾚｰﾑ移動
        iframe = browser.find_element_by_css_selector('frame[scrolling="no"]')
        browser.switch_to_frame(iframe)

        #「キーワード検索」タグ選択
        browser.find_element_by_tag_name('form').find_element_by_css_selector('map[name="m_Sh"]').find_element_by_tag_name('area').click()

        #ﾌﾚｰﾑ移動
        browser.switch_to_default_content()
        browser.switch_to_frame('Main')

        #検索ワード入力
        browser.find_element_by_css_selector('input[name="QueryIn"]').send_keys(SearchWord)
        #検索実行
        sleep(2)
        browser.find_element_by_css_selector('button[type="submit"]').click()
        sleep(1)

        browser.switch_to_default_content()
        browser.switch_to_frame('View')

        tables = browser.find_element_by_tag_name('body').find_element_by_css_selector('form[name="_DominoForm"]').find_elements_by_tag_name('table')
        if len(tables) != 3:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_okn.columns)
            df_okn = df_okn.append(record,ignore_index=True) 
            browser.quit()

        else:
            trtags = browser.find_element_by_tag_name('body').find_element_by_css_selector('form[name="_DominoForm"]').find_elements_by_tag_name('table')[1].find_elements_by_css_selector('tr[valign="top"]')
            for i in range(len(trtags)):
                trtags = browser.find_element_by_tag_name('body').find_element_by_css_selector('form[name="_DominoForm"]').find_elements_by_tag_name('table')[1].find_elements_by_css_selector('tr[valign="top"]')
                atag = trtags[i].find_elements_by_tag_name('td')[1].find_element_by_tag_name('a')
                if '年' in atag.text:
                    Speaker = atag.text.split('日')[1]
                    if '委員長' not in Speaker:
                        if i == 0:
                            num = 1
                        else:
                            if trtags[i].find_elements_by_tag_name('td')[1].find_element_by_tag_name('a').text.split('日')[0] != trtags[i-1].find_elements_by_tag_name('td')[1].find_element_by_tag_name('a').text.split('日')[0]:
                                num = 1
                            elif trtags[i].find_elements_by_tag_name('td')[1].find_element_by_tag_name('a').text.split('日')[0] == trtags[i-1].find_elements_by_tag_name('td')[1].find_element_by_tag_name('a').text.split('日')[0]:
                                num = num+1

                        atag.click()
                        sleep(3)
                        browser.switch_to_default_content()
                        browser.switch_to_frame('Main')
                        JDstep1 = browser.find_element_by_id('dochead')
                        JDstep2 = JDstep1.find_element_by_tag_name('table')
                        JDstep3 = JDstep2.find_element_by_tag_name('tr')
                        JDstep4 = JDstep3.find_elements_by_tag_name('td')[1]
                        JDstep5 = JDstep4.find_element_by_tag_name('table')
                        JDstep6 = JDstep5.find_element_by_tag_name('tr')
                        JDstep7 = JDstep6.find_elements_by_tag_name('td')
                        JournalTitle = JDstep7[0].text
                        Date = JournalTitle.split('年(')[0]+'年'+JDstep7[1].text.split('号')[1]
                        Rstep1 = browser.find_element_by_css_selector('div[class="allbody"]')
                        SpeakOrder = num
                        Name = BookMarkName
                        record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_okn.columns)
                        df_okn = df_okn.append(record,ignore_index=True)
                        browser.switch_to_default_content()
                        browser.switch_to_frame('View')

                else:
                    if i == 0:
                        not_applicable = '該当する文書は存在しません。'
                        #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
                        Name = BookMarkName
                        SearchWord = SearchWord
                        #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                        record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_okn.columns)
                        df_okn = df_okn.append(record,ignore_index=True) 
                        browser.quit()
                    break

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_okn.columns)
        df_okn = df_okn.append(record,ignore_index=True)
        browser.quit()
                    
    return df_okn


# In[ ]:


if __name__ == '__main__':
    okn_s()

