#!/usr/bin/env python
# coding: utf-8

# In[ ]:
#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import pandas as pd
#ｳｪﾌﾞｽｸﾚｲﾋﾟﾝｸﾞ用ﾗｲﾌﾞﾗﾘ
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

from time import sleep

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')


#栃木
def tochigi(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='E']['URL'][8]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='E']['name'][8]
    df_tcg = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
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

        #検索実行SearchExecution
        browser.find_element_by_css_selector("input[type='submit']").click()                    

        sleep(3)

        iframe = browser.find_element_by_css_selector('iframe')
        browser.switch_to.frame(iframe)

        #【最新年度】議事録のURL保存
        JURLs_temp1 = browser.find_elements_by_tag_name('table')
        if JURLs_temp1 == []:
            not_applicable = '該当する発言は存在しませんでした。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_tcg.columns)
            df_tcg = df_tcg.append(record,ignore_index=True)
            browser.quit()

        else:
            JURLs_temp1 = JURLs_temp1[1].find_elements_by_css_selector('a[target="HLD_WIN"]')
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
                    if '議長' not in Speaker and '委員長' not in Speaker:
                        SpeakerID = ele.find_element_by_tag_name('a').get_attribute('href').split('#')[1]
                        ele.click()
                        browser.switch_to_default_content()
                        browser.switch_to.frame('hat')
                        Remark_candidates = browser.find_element_by_tag_name('body').find_elements_by_tag_name('p')
                        atags = []
                        for ele in Remark_candidates:
                            try:
                                if SpeakerID in ele.find_element_by_tag_name('a').get_attribute('name'):
                                    Remark = ele.text
                            except NoSuchElementException:
                                pass
                        SpeakOrder = num
                        Name = BookMarkName
                        record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_tcg.columns)
                        df_tcg = df_tcg.append(record,ignore_index=True)
                        num = num+1
                    browser.switch_to_default_content()
                    browser.switch_to.frame('sidebar')
                browser.switch_to.window(browser.window_handles[0]) #元いたｳｨﾝﾄﾞｳに戻る
                browser.switch_to.frame(iframe)

            #【過年度】
            JURLs_temp1 = browser.find_element_by_css_selector("td[valign='TOP']").find_elements_by_tag_name("a")
            JURLs_temp2 = []
            for ele1 in JURLs_temp1:
                JURLs_temp2.append(ele1.get_attribute("href"))
            for ele2 in JURLs_temp2:
                browser.get(ele2)
                JURLs_temp3 = browser.find_elements_by_css_selector("a[target='HLD_WIN']")

                sleep(2)
                for ele3 in JURLs_temp3:
                    ele3.click()
                    sleep(3)
                    browser.switch_to.window(browser.window_handles[-1]) #新しく開いたｳｨﾝﾄﾞｳに移動
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
                            SpeakerID = ele.find_element_by_tag_name('a').get_attribute('href').split('#')[1]
                            ele.click()
                            browser.switch_to_default_content()
                            browser.switch_to.frame('hat')
                            Remark_candidates = browser.find_elements_by_tag_name('p')
                            for ele in Remark_candidates:
                                try:
                                    if SpeakerID in ele.find_element_by_tag_name('a').get_attribute('name'):
                                        Remark = ele.text
                                except NoSuchElementException:
                                    pass
                            SpeakOrder = num
                            Name = BookMarkName
                            record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_tcg.columns)
                            df_tcg = df_tcg.append(record,ignore_index=True)
                            num = num+1
                        browser.switch_to_default_content()
                        browser.switch_to.frame('sidebar')
                    browser.switch_to.window(browser.window_handles[0]) #元いたｳｨﾝﾄﾞｳに戻る

            browser.quit()

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_tcg.columns)
        df_tcg = df_tcg.append(record,ignore_index=True)
        browser.quit()
            
    return df_tcg

if __name__ == '__main__':
    tochigi()
