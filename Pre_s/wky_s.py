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


#和歌山
def wky_s(self):
    df_BookMarks = pd.read_csv('../..//source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='J']['URL'][29]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='J']['name'][29]
    df_wky = pd.DataFrame(index=[], columns=['Name', 'SearchWord', 'JournalTitle', 'Date', 'Speaker', 'SpeakOrder'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        #検索ワード入力
        browser.find_element_by_id('gs_tti50').find_element_by_tag_name('input').send_keys(SearchWord)
        #検索実行
        browser.find_element_by_class_name('gsc-search-button').find_element_by_tag_name('button').click()
        sleep(3)

        check1 = browser.find_elements_by_css_selector('div[class="gsc-cursor-box gs-bidi-start-align"]')
        org_window = browser.current_window_handle

        result_temp = browser.find_element_by_css_selector('div[class="gsc-webResult gsc-result"]')
        result_temp2 = result_temp.find_elements_by_css_selector('div[class="gs-webResult gs-result gs-no-results-result"]')
        if result_temp2 != []:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_wky.columns)
            df_wky = df_wky.append(record,ignore_index=True) 
            browser.quit()
        else:
            #前処理part1 ﾃﾞｰﾀﾍﾞｰｽから和歌山県議事録データ集を呼び出し
            db_name = '../LocalJournal.db'
            conn = sqlite3.connect(db_name)
            c = conn.cursor()
            c
            sql_read = 'select * from wakayama_pages2'
            DateCandidates = pd.read_sql(sql_read,conn)
            #前処理part2 検索結果から、会議開催年、月、号ﾃﾞｰﾀを取得し、ﾃﾞｰﾀﾌﾚｰﾑに格納
             #検索結果のタイトル所属要素(div)取得
            result_temp1 = browser.find_elements_by_css_selector('div[class="gsc-webResult gsc-result"]')
             #要素内部を参照し、ﾘﾝｸが付属している要素を取得し、ﾘｽﾄ化
            resultList = []
            df_dateKey = pd.DataFrame(index=[], columns=['year', 'month', 'councilCategory', 'number'])
            for ele1 in result_temp1:
                resultList.append(ele1.find_element_by_css_selector('div[class="gsc-thumbnail-inside"]').find_element_by_css_selector('a[class="gs-title"]'))
            #ﾘﾝｸが付属している要素(a)から、開催年、月、号を取得し、ﾃﾞｰﾀﾌﾚｰﾑに格納
            for i in range(len(resultList)) :
                if '目次' not in resultList[i].text.split(' ')[2].split('号')[0]:
                    record1 = pd.Series([resultList[i].text.split(' ')[0].split('年')[0]+"年", resultList[i].text.split(' ')[0].split('年')[1], resultList[i].text.split('県議会')[1].split('会議録')[0], resultList[i].text.split(' ')[2].split('号')[0]+"号"], index=df_dateKey.columns)
                    df_dateKey = df_dateKey.append(record1, ignore_index=True)
            #次ﾍﾟｰｼﾞ確認
            if check1 !=[]:
                check2 = check1[0].find_element_by_css_selector('div[class="gsc-cursor"]')
                nextlinks = check2.find_elements_by_css_selector('div[role="link"]')
                for n in range(len(nextlinks)):
                    nextlinks = browser.find_elements_by_css_selector('div[class="gsc-cursor-box gs-bidi-start-align"]')[0].find_element_by_css_selector('div[class="gsc-cursor"]').find_elements_by_css_selector('div[role="link"]')
                    sleep(1)
                    try:
                        nextlinks[n].click()
                    except:
                        browser.close()
                        break
                    sleep(3)
                    result_temp1 = browser.find_elements_by_css_selector('div[class="gsc-webResult gsc-result"]')
                    resultList2 = []
                    for ele1 in result_temp1:
                        resultList2.append(ele1.find_element_by_css_selector('div[class="gsc-thumbnail-inside"]').find_element_by_css_selector('a[class="gs-title"]'))
                    #ﾘﾝｸが付属している要素(a)から、開催年、月、号を取得し、ﾃﾞｰﾀﾌﾚｰﾑに格納
                    for i in range(len(resultList2)):
                        if '目次' not in resultList2[i].text.split(' ')[2].split('号')[0]:
                            record1 = pd.Series([resultList2[i].text.split(' ')[0].split('年')[0]+"年", resultList2[i].text.split(' ')[0].split('年')[1], resultList2[i].text.split('県議会')[1].split('会議録')[0], resultList2[i].text.split(' ')[2].split('号')[0]+"号"], index=df_dateKey.columns)
                            df_dateKey = df_dateKey.append(record1, ignore_index=True)

            #↑ここまで前処理part2
            #数字の正規化
            for i in range(len(df_dateKey['number'])):
                df_dateKey['number'][i] = unicodedata.normalize("NFKC", df_dateKey['number'][i])

            #日付、会議名、発言者、発言の順番、発言内容 取得
            temp_join = []

            for j in range(len(df_dateKey)):
                #日付取得part1 議事録全体のﾃﾞｰﾀﾌﾚｰﾑから検索結果のﾃﾞｰﾀﾌﾚｰﾑを使用して検索結果の該当月議会を絞り込むまで
                key1 = df_dateKey['year'][j]
                key2 = df_dateKey['month'][j]
                key3 = df_dateKey['councilCategory'][j]
                key4 = df_dateKey['number'][j]
                DC_temp = DateCandidates.query("year in @key1 & month == @key2 & councilCategory == @key3 & number == @key4")
                DC_temp.reset_index(inplace=True, drop=True)
                PageKey = DC_temp['URL'][0]
                #data取得ここまでpart1
                #data取得part2 検索結果該当月の議会議事録ﾍﾟｰｼﾞに遷移するまで
                browser = webdriver.Chrome(ChromeDriverManager().install())#新規ﾌﾞﾗｳｻﾞ立ち上げ
                sleep(3)        
                browser.get(PageKey)#日付取得part1で取得した結果を利用し、該当月の議会議事録ﾍﾟｰｼﾞに遷移
                browser.switch_to.window(browser.window_handles[-1])
                #ここまでdata取得part2
                #data取得part3
                ptags = browser.find_element_by_id('content').find_element_by_class_name('article').find_elements_by_tag_name('p')
                alltext = []
                for ele in ptags:
                    alltext.append(ele.text)
                jointext = ''.join(alltext)
                temp_join.append(jointext)

                #日付Date取得
                if len(ptags) < 20:
                    for i in range(len(jointext.split('\n'))):
                        if '日（' in jointext.split('\n')[i]:
                            if '号' in jointext.split('\n')[i]:
                                Date = jointext.split('\n')[i].split('（')[0].split('号')[1]
                            else:
                                Date = jointext.split('\n')[i].split('日')[0]+'日'
                else:
                    for i in range(len(ptags)):
                        if '日（' in ptags[i].text and '年' in ptags[i].text and '曜日' in ptags[i].text:
                            Date = ptags[i].text.split('日')[0]+'日'
                #会議名、発言者、発言の順番、発言内容取得
                RemarksBySpeaker = re.split("(?=[○〇])", jointext)
                num = 1
                for ele in RemarksBySpeaker:
                    if SearchWord in ele:
                        Speaker_temp =re.split("(?<=君)", ele)[0]
                        if '議長' not in Speaker_temp or '委員長' not in Speaker_temp:
                            Speaker = Speaker_temp
                            SpeakOrder = num
                            Name = BookMarkName
                            JournalTitle = browser.find_elements_by_tag_name('h1')[1].text.split('会議録')[0]
                            record = pd.Series([Name, SearchWord, JournalTitle, Date, Speaker, SpeakOrder], index=df_wky.columns)
                            df_wky = df_wky.append(record,ignore_index=True)
                            num += 1
                browser.close()
                if len(df_wky) == 0:
                    not_applicable = '該当する文書は存在しません。'
                    #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
                    Name = BookMarkName
                    SearchWord = SearchWord
                    #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                    record = pd.Series([Name, SearchWord, not_applicable, '', '', ''], index=df_wky.columns)
                    df_wky = df_wky.append(record,ignore_index=True) 
                
            else:
                browser.quit()

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series([Name, SearchWord, error, '', '', ''], index=df_wky.columns)
        df_wky = df_wky.append(record,ignore_index=True)
        browser.quit()
                 
    return df_wky

if __name__ == '__main__':
    wky_s()

