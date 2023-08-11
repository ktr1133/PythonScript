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

from webdriver_manager.chrome import ChromeDriverManager

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')

#広島
def hiroshima(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='B']['URL'][33]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='B']['name'][33]
    df_hrs = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.implicitly_wait(5)
        browser.get(BookMarkURL)

        links_atag = browser.find_elements_by_tag_name('a')
        for link in links_atag:
            if 'search-meeting' in link.get_attribute('href'):
                search_step =link
        search_step.click()                
        browser.implicitly_wait(5)

        #会議種類の選択
        MTList = browser.find_element_by_id('cabinet-is-here').find_elements_by_tag_name('option')
        actions = ActionChains(browser)
        actions.key_down(keys.SHIFT)
        for mt_ele in MTList:
            if '本会議' in mt_ele.text:
                actions.click(mt_ele)
                actions.perform()

        #分類名の選別
        classList = browser.find_element_by_id('class-is-here').find_elements_by_tag_name('option')
        for class_ele in classList:
            if '本文' in class_ele.text:
                class_ele.click()

        browser.find_element_by_css_selector("input[type='submit']").click()
        browser.implicitly_wait(5)
        #新しいページに移動
        browser.switch_to.window(browser.window_handles[-1])
        #検索ワード入力
        browser.find_element_by_css_selector("input[type='text']").send_keys(SearchWord) 
        browser.find_element_by_css_selector("input[type='submit']").click()

        browser.implicitly_wait(5)
        #新しく開いたｳｨﾝﾄﾞｳに移動
        browser.switch_to.window(browser.window_handles[-1])

        if browser.find_elements_by_css_selector('div[class="result-list-nohit"]') != []:
            not_applicable = '該当する発言は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_hrs.columns)
            df_hrs = df_hrs.append(record,ignore_index=True)
            browser.quit()
        else:
            Name = BookMarkName
            #検索結果の全ての文書のaタグ情報を取得
            org_window = browser.current_window_handle
            JURLList2_step1 = browser.find_elements_by_class_name("result-list") #広島、佐賀

            for i in range(len(JURLList2_step1)):
                JURLList2_step1 = browser.find_elements_by_class_name("result-list")
                result_document = JURLList2_step1[i].find_element_by_css_selector('div[class="result-document"]')
                Date = result_document.find_element_by_css_selector('span[class="result-document-date"]').text
                JournalTitle = result_document.find_element_by_css_selector('a').text
                result_document.find_element_by_css_selector('a').click()
                browser.implicitly_wait(5)
                voicelist_candidates = browser.find_element_by_id('voiceList').find_elements_by_tag_name('li')
                voicelist = []
                for ele in voicelist_candidates:
                    if 'HitVoice' in ele.get_attribute('class') :
                        voicelist.append(ele)
                num = 1
                for j in range(len(voicelist)):
                    Speaker_temp = voicelist[j].find_element_by_css_selector('span[class="voice__name voice__hit"]').text
                    if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                        Speaker = Speaker_temp
                        SpeakOrder = num
                        voicenum = voicelist[j].find_element_by_css_selector('span[class="voice__number"]').text
                        voicelist[j].click()
                        browser.implicitly_wait(5)
                        temp = browser.find_element_by_css_selector('div[id="Page"]')
                        temp2 = temp.find_element_by_css_selector('div[id="page-top"]')
                        temp3 = temp2.find_element_by_css_selector('section[class="page-text page-text-one"]')
                        temp4 = temp3.find_element_by_css_selector('form[id="formVoiceSelect"]')
                        temp5 = temp4.find_element_by_css_selector('ul[class="page-list"]')
                        temp6 = temp.find_elements_by_tag_name('li')
                        for ele in temp6:
                            if ele.get_attribute('data-voice-no') == voicenum:
                                 Remark = ele.find_element_by_tag_name('p').text
                        record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_hrs.columns)
                        df_hrs = df_hrs.append(record,ignore_index=True)
                        num += 1

                browser.back()
                browser.implicitly_wait(5)

            while browser.find_element_by_class_name("pagination").find_elements_by_tag_name('span')[-1].find_elements_by_tag_name('a') != []:
                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('span')[-1].find_element_by_tag_name('a').click()
                browser.implicitly_wait(5)
                browser.switch_to.window(browser.window_handles[-1])
                org_window = browser.current_window_handle

                JURLList2_step1 = browser.find_elements_by_class_name("result-list") #広島、佐賀

                for i in range(len(JURLList2_step1)):
                    JURLList2_step1 = browser.find_elements_by_class_name("result-list")
                    result_document = JURLList2_step1[i].find_element_by_css_selector('div[class="result-document"]')
                    Date = result_document.find_element_by_css_selector('span[class="result-document-date"]').text
                    JournalTitle = result_document.find_element_by_css_selector('a').text
                    result_document.find_element_by_css_selector('a').click()
                    browser.implicitly_wait(5)
                    voicelist_candidates = browser.find_element_by_id('voiceList').find_elements_by_tag_name('li')
                    voicelist = []
                    for ele in voicelist_candidates:
                        if 'HitVoice' in ele.get_attribute('class') :
                            voicelist.append(ele)
                    num = 1
                    for j in range(len(voicelist)):
                        Speaker_temp = voicelist[j].find_element_by_css_selector('span[class="voice__name voice__hit"]').text
                        if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                            Speaker = Speaker_temp
                            SpeakOrder = num
                            voicenum = voicelist[j].find_element_by_css_selector('span[class="voice__number"]').text
                            voicelist[j].click()
                            browser.implicitly_wait(5)
                            temp = browser.find_element_by_css_selector('div[id="Page"]')
                            temp2 = temp.find_element_by_css_selector('div[id="page-top"]')
                            temp3 = temp2.find_element_by_css_selector('section[class="page-text page-text-one"]')
                            temp4 = temp3.find_element_by_css_selector('form[id="formVoiceSelect"]')
                            temp5 = temp4.find_element_by_css_selector('ul[class="page-list"]')
                            temp6 = temp.find_elements_by_tag_name('li')
                            for ele in temp6:
                                if ele.get_attribute('data-voice-no') == voicenum:
                                     Remark = ele.find_element_by_tag_name('p').text
                            record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_hrs.columns)
                            df_hrs = df_hrs.append(record,ignore_index=True)
                            num += 1

                    browser.back()
                    browser.implicitly_wait(5)
            
    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_hrs.columns)
        df_hrs = df_hrs.append(record,ignore_index=True)
        browser.quit()
        
    return df_hrs


if __name__ == '__main__':
    hiroshima()
