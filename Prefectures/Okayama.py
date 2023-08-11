#!/usr/bin/env python
# coding: utf-8

#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import pandas as pd
#ｳｪﾌﾞｽｸﾚｲﾋﾟﾝｸﾞ用ﾗｲﾌﾞﾗﾘ
from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support.select import Select

from time import sleep

import traceback

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')


#岡山
def okayama(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='L']['URL'][32]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='L']['name'][32]
    df_oky = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        #検索ワード入力
        browser.find_element_by_id('tab-detail').click()
        browser.find_element_by_id('se-detail-keywords').send_keys(SearchWord)

        #検索実行
        browser.find_element_by_id('btn-search').click()

        sleep(3)

        temp = browser.find_element_by_css_selector('span[id="v-hit-count"]').text
        if temp == '0':
            not_applicable = '該当する文書はありません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_oky.columns)
            df_oky = df_oky.append(record,ignore_index=True) 
            browser.quit()

        else:
            dropdown = browser.find_element_by_id('slt-hit-year')
            select = Select(dropdown)
            options = select.options
            for i in range(len(options)):
                sleep(2)
                browser.find_element_by_id('slt-hit-year').click()
                sleep(2)
                dropdown = browser.find_element_by_id('slt-hit-year')
                select = Select(dropdown)
                options = select.options
                options[i].click()
                sleep(2)

                parentlist_temp = browser.find_element_by_id('v-hit-list').find_elements_by_tag_name('tr')
                for i in range(len(parentlist_temp)):
                    parentlist_temp = browser.find_element_by_id('v-hit-list').find_elements_by_tag_name('tr')
                    if 'schedule' in parentlist_temp[i].get_attribute('class'):
                        items = parentlist_temp[i].find_elements_by_tag_name('td')
                        Date = items[0].text+items[2].text.split('－')[0]

                        items[2].find_element_by_tag_name('a').click()
                        sleep(2)
                        browser.find_element_by_id('tab-minute-plain').click()
                        sleep(2)
                        remark_temp1 = browser.find_element_by_id('plain-minute')
                        remark_temp2 = remark_temp1.find_elements_by_tag_name('pre')
                        num = 1
                        for ele3 in remark_temp2:
                            if SearchWord in ele3.text:
                                Remark = ele3.text
                                Speaker = Remark.split('　')[0]
                                if '議長' not in Speaker and '委員長' not in Speaker:
                                    SpeakOrder = num
                                    JournalTitle = browser.find_element_by_id('council-title').text.split('  ')[1]
                                    Name = BookMarkName
                                    record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_oky.columns)
                                    df_oky = df_oky.append(record,ignore_index=True)
                                    num = num+1

                        sleep(2)
                        browser.find_element_by_id('btn-search-result').click()
                        sleep(2)

            browser.quit()

    except:
        error = 'error'
        msg = traceback.format_exc()
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error+" "+msg], index=df_oky.columns)
        df_oky = df_oky.append(record,ignore_index=True)
        browser.quit()
    
    return df_oky


if __name__ == '__main__':
    okayama()
