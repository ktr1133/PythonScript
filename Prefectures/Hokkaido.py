#!/usr/bin/env python
# coding: utf-8

# In[ ]:
#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import sqlite3
import pandas as pd
#ｳｪﾌﾞｽｸﾚｲﾋﾟﾝｸﾞ用ﾗｲﾌﾞﾗﾘ
from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

from time import sleep

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')

#北海
def hokkai(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='A']['URL'][0]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='A']['name'][0]
    df_hki = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        browser.switch_to.frame('RIGHT')
        browser.switch_to.frame('TOP')

        SearchWordInput = browser.find_element_by_id('qzs_suggest_start')
        SearchWordInput.send_keys(SearchWord)
        #発言種別選択
        browser.find_element_by_id('ktyp4').click()

        #会議種類の選択

        #検索実行SearchExecution
        browser.find_element_by_css_selector("input[value='検索実行']").click()

        sleep(3)
        browser.switch_to_default_content()
        browser.switch_to.frame('RIGHT')
        browser.switch_to.frame('BOTTOM')

        #【最新年度】議事録のURL保存
        JURLs_temp1 = browser.find_elements_by_tag_name('table')
        if JURLs_temp1 == []:
            not_applicable = '該当する発言は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_hki.columns)
            df_hki = df_hki.append(record,ignore_index=True)
            browser.quit()

        else:
            JURLs_temp2 = JURLs_temp1[1].find_elements_by_css_selector('a[target="HLD_WIN"]')
            org_window = browser.current_window_handle
            for ele1 in JURLs_temp2:
                JURLs_temp2 = browser.find_elements_by_tag_name('table')[1].find_elements_by_css_selector('a[target="HLD_WIN"]')
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
                    Speaker_temp = ele.text
                    if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                        Speaker = Speaker_temp
                        ele.click()
                        browser.switch_to_default_content()
                        browser.switch_to.frame('hat')
                        Remark = browser.find_element_by_tag_name('body').text
                        SpeakOrder = num
                        Name = BookMarkName
                        record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_hki.columns)
                        df_hki = df_hki.append(record,ignore_index=True)
                        num = num+1
                        browser.switch_to_default_content()
                        browser.switch_to.frame('sidebar')
                    
                browser.switch_to.window(browser.window_handles[0]) #元いたｳｨﾝﾄﾞｳに戻る
                browser.switch_to.frame('RIGHT')
                browser.switch_to.frame('BOTTOM')

            #次ﾍﾟｰｼﾞの有無確認
            nextlink_candidates = browser.find_element_by_tag_name('tbody').find_element_by_css_selector('td[align="RIGHT"]').find_elements_by_tag_name('a')
            if nextlink_candidates == []:
                pass
            else:
                nextlink = []
                for ele in nextlink_candidates:
                    if '次ページ' in ele.text:
                        nextlink.append(ele)
                while nextlink != []:
                    nextlink.click()
                    iframe = browser.find_element_by_css_selector('frameset')
                    browser.switch_to.frame(iframe)
                    browser.switch_to.frame('RIGHT')
                    browser.switch_to.frame('BOTTOM')

                    JURLs_temp2 = JURLs_temp1[1].find_elements_by_css_selector('a[target="HLD_WIN"]')
                    org_window = browser.current_window_handle
                    for ele1 in JURLs_temp2:
                        JURLs_temp2 = browser.find_elements_by_tag_name('table')[1].find_elements_by_css_selector('a[target="HLD_WIN"]')
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
                            if '議長' not in Speaker and '委員長' not in Speaker:
                                ele.click()
                                sleep(2)
                                browser.switch_to_default_content()
                                browser.switch_to.frame('hat')
                                Remark = browser.find_element_by_tag_name('body').text
                                SpeakOrder = num
                                Name = BookMarkName
                                record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_hki.columns)
                                df_hki = df_hki.append(record,ignore_index=True)
                                num = num+1
                                browser.switch_to_default_content()
                                browser.switch_to.frame('sidebar')
                                
                        browser.switch_to.window(browser.window_handles[0]) #元いたｳｨﾝﾄﾞｳに戻る
                        browser.switch_to.frame('RIGHT')
                        browser.switch_to.frame('BOTTOM')

                        nextlink_candidates = browser.find_element_by_tag_name('tbody').find_element_by_css_selector('td[align="RIGHT"]').find_elements_by_tag_name('a')
                        nextlink = []
                        for ele in nextlink_candidates:
                            if '次ページ' in ele.text:
                                nextlink.append(ele)

            browser.quit()

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_hki.columns)
        df_hki = df_hki.append(record,ignore_index=True)
        browser.quit()

    return df_hki


# In[ ]:


if __name__ == '__main__':
    hokkai()
