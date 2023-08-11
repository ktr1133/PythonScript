#!/usr/bin/env python
# coding: utf-8

#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import pandas as pd
#ｳｪﾌﾞｽｸﾚｲﾋﾟﾝｸﾞ用ﾗｲﾌﾞﾗﾘ
from selenium import webdriver
from selenium.webdriver.common.keys import Keys as keys
from selenium.webdriver.common.action_chains import ActionChains

from webdriver_manager.chrome import ChromeDriverManager

from time import sleep

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')


#島根
def shimane(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='B']['URL'][31]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='B']['name'][31]
    df_smn = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        links = browser.find_elements_by_class_name('nav-global-link')
        for link in links:
            try:
                if 'search-detail' in link.get_attribute('href'):
                    truelink = link
            except TypeError:
                pass
        try:
            truelink.click()
        except:
            pass
        MTList = browser.find_element_by_id('meeting').find_elements_by_tag_name('option')
        actions = ActionChains(browser)
        actions.key_down(keys.SHIFT)
        for mt_ele in MTList:
            if '本会議' in mt_ele.text:
                actions.click(mt_ele)
                actions.perform()

        #分類選択肢がないルートの設定
        #分類名の選別
        classList = browser.find_element_by_id('class').find_elements_by_tag_name('option')
        for class_ele in classList:
            if '本文' in class_ele.text:
                class_ele.click()
        #検索ワード入力
        browser.find_element_by_id("textaria").send_keys(SearchWord) 

        browser.find_element_by_css_selector("button[type='submit']").click()

        sleep(3)
        #新しく開いたｳｨﾝﾄﾞｳに移動
        browser.switch_to.window(browser.window_handles[-1])

        #検索結果の全ての文書のaタグ情報を取得
        org_window = browser.current_window_handle
        JURLList1_step1 = browser.find_elements_by_class_name("result-doc") #青森、茨城、東京、福井、富山、山梨、愛知、京都、島根、福岡
        if JURLList1_step1 == []:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_smn.columns)
            df_smn = df_smn.append(record,ignore_index=True)
            browser.quit()

        else:
            Name = BookMarkName
            JournalTitles_div = browser.find_elements_by_css_selector('div[class="result-title"]')
            for i in range(len(JournalTitles_div)):
                JournalTitles_div = browser.find_elements_by_css_selector('div[class="result-title"]')
                JournalTitle = JournalTitles_div[i].find_element_by_tag_name('a').text
                actions = ActionChains(browser)
                actions.key_down(keys.SHIFT)
                actions.click(JournalTitles_div[i].find_element_by_tag_name('a'))
                actions.perform()
                browser.implicitly_wait(5)
                browser.switch_to.window(browser.window_handles[-1])
                Date = browser.find_element_by_css_selector('section[class="command"] > h1 > date[class="command__date"]').text
                temp1 = browser.find_element_by_css_selector('main[class="document__voice"]')
                temp2 = temp1.find_element_by_css_selector('div[id="speaker-top"]')
                temp3 = temp2.find_element_by_css_selector('ul[id="voiceList"]')
                voicelist_candidates = temp3.find_elements_by_tag_name('li')
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
                        temp1 = browser.find_element_by_css_selector('div[id="Page"]')
                        temp2 = temp1.find_element_by_css_selector('div[id="page-top"]')
                        temp3 = temp2.find_element_by_css_selector('section[class="page-text page-text-one"]')
                        temp4 = temp3.find_element_by_css_selector('form[id="formVoiceSelect"]')
                        temp5 = temp4.find_element_by_css_selector('ul')
                        temp6 = temp5.find_elements_by_tag_name('li')
                        for ele in temp6:
                            if ele.get_attribute('data-voice-no') == voicenum:
                                 Remark = ele.find_element_by_tag_name('p').text
                        record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_smn.columns)
                        df_smn = df_smn.append(record,ignore_index=True)
                        num += 1

                browser.close()
                browser.switch_to_window(org_window)

            nextlink = browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_elements_by_tag_name('a')
            while nextlink != []:
                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_element_by_tag_name('a').click()
                browser.implicitly_wait(5)
                browser.switch_to.window(browser.window_handles[-1])
                org_window = browser.current_window_handle

                JournalTitles_div = browser.find_elements_by_css_selector('div[class="result-title"]')
                for i in range(len(JournalTitles_div)):
                    JournalTitles_div = browser.find_elements_by_css_selector('div[class="result-title"]')
                    JournalTitle = JournalTitles_div[i].find_element_by_tag_name('a').text
                    actions = ActionChains(browser)
                    actions.key_down(keys.SHIFT)
                    actions.click(JournalTitles_div[i].find_element_by_tag_name('a'))
                    actions.perform()
                    browser.implicitly_wait(5)
                    browser.switch_to.window(browser.window_handles[-1])
                    Date = browser.find_element_by_css_selector('section[class="command"] > h1 > date[class="command__date"]').text
                    temp1 = browser.find_element_by_css_selector('main[class="document__voice"]')
                    temp2 = temp1.find_element_by_css_selector('div[id="speaker-top"]')
                    temp3 = temp2.find_element_by_css_selector('ul[id="voiceList"]')
                    voicelist_candidates = temp3.find_elements_by_tag_name('li')
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
                            temp1 = browser.find_element_by_css_selector('div[id="Page"]')
                            temp2 = temp1.find_element_by_css_selector('div[id="page-top"]')
                            temp3 = temp2.find_element_by_css_selector('section[class="page-text page-text-one"]')
                            temp4 = temp3.find_element_by_css_selector('form[id="formVoiceSelect"]')
                            temp5 = temp4.find_element_by_css_selector('ul')
                            temp6 = temp5.find_elements_by_tag_name('li')
                            for ele in temp6:
                                if ele.get_attribute('data-voice-no') == voicenum:
                                     Remark = ele.find_element_by_tag_name('p').text
                            record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_smn.columns)
                            df_smn = df_smn.append(record,ignore_index=True)
                            num += 1

                    browser.close()
                    browser.switch_to_window(org_window)

                nextlink = browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_elements_by_tag_name('a')

            browser.quit()
                
    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_smn.columns)
        df_smn = df_smn.append(record,ignore_index=True)
        browser.quit()
        
    return df_smn

if __name__ == '__main__':
    shimane()
