#!/usr/bin/env python
# coding: utf-8

# In[ ]:
#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import pandas as pd
#ｳｪﾌﾞｽｸﾚｲﾋﾟﾝｸﾞ用ﾗｲﾌﾞﾗﾘ
from selenium import webdriver
from selenium.webdriver.common.keys import Keys as keys
from selenium.webdriver.common.action_chains import ActionChains

from webdriver_manager.chrome import ChromeDriverManager

from time import sleep

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')


#東京(seleniumのみ)
def tokyo(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='B']['URL'][12]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='B']['name'][12]
    df_tky = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        links_atag = browser.find_elements_by_tag_name('a')
        for link in links_atag:
            if 'search-meeting' in link.get_attribute('href'):
                search_step =link
        search_step.click()                
        sleep(1)

        #検索対象の会議の選別CouncilClassifcation
        MTList = browser.find_element_by_id('meeting').find_elements_by_tag_name('option')
        actions = ActionChains(browser)
        actions.key_down(keys.SHIFT)
        for mt_ele in MTList:
            if '本会議' in mt_ele.text:
                actions.click(mt_ele)
                actions.perform()

        #分類名の選別
        classList = browser.find_element_by_id('class').find_elements_by_tag_name('option')
        for class_ele in classList:
            if '本文' in class_ele.text:
                class_ele.click()

        browser.find_element_by_css_selector("button[type='submit']").click()
        sleep(1)
        #新しいページに移動
        browser.switch_to.window(browser.window_handles[-1])
        #検索ワード入力
        browser.find_element_by_css_selector("input[class='refinesearch__text']").send_keys(SearchWord) 
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
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_tky.columns)
            df_tky = df_tky.append(record,ignore_index=True)
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
                sleep(2)
                browser.switch_to.window(browser.window_handles[-1])
                browser.switch_to.frame('Command')
                Date = browser.find_element_by_css_selector('span[class="command__date"]').text
                browser.switch_to_default_content()
                browser.switch_to.frame('Voicelist')
                voicelist_candidates = browser.find_element_by_id('voiceList').find_elements_by_tag_name('li')
                voicelist = []
                for ele in voicelist_candidates:
                    if 'HitVoice' in ele.find_element_by_tag_name('a').get_attribute('class') :
                        voicelist.append(ele)
                num = 1
                for j in range(len(voicelist)):
                    Speaker_temp = voicelist[j].find_element_by_tag_name('a').text
                    if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                        Speaker = Speaker_temp
                        SpeakOrder = num
                        voicenum = voicelist[j].text
                        voicelist[j].click()
                        sleep(1)
                        browser.switch_to_default_content()
                        browser.switch_to.frame('Page')
                        Remark = browser.find_element_by_tag_name('p').text
                        Name = BookMarkName
                        record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_tky.columns)
                        df_tky = df_tky.append(record,ignore_index=True)
                        num += 1
                        browser.switch_to_default_content()
                        browser.switch_to.frame('Voicelist')

                browser.close()
                browser.switch_to_window(org_window)
                
            nextlink = browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-2].find_elements_by_tag_name('a')
            while nextlink != []:
                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-2].find_element_by_tag_name('a').click()
                sleep(2)
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
                    sleep(2)
                    browser.switch_to.window(browser.window_handles[-1])
                    browser.switch_to.frame('Command')
                    Date = browser.find_element_by_css_selector('span[class="command__date"]').text
                    browser.switch_to_default_content()
                    browser.switch_to.frame('Voicelist')
                    voicelist_candidates = browser.find_element_by_id('voiceList').find_elements_by_tag_name('li')
                    voicelist = []
                    for ele in voicelist_candidates:
                        if 'HitVoice' in ele.find_element_by_tag_name('a').get_attribute('class') :
                            voicelist.append(ele)
                    num = 1
                    for j in range(len(voicelist)):
                        Speaker_temp = voicelist[j].find_element_by_tag_name('a').text
                        if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                            Speaker = Speaker_temp
                            SpeakOrder = num
                            voicenum = voicelist[j].text
                            voicelist[j].click()
                            sleep(1)
                            browser.switch_to_default_content()
                            browser.switch_to.frame('Page')
                            Remark = browser.find_element_by_tag_name('p').text
                            Name = BookMarkName
                            record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_tky.columns)
                            df_tky = df_tky.append(record,ignore_index=True)
                            num += 1
                            browser.switch_to_default_content()
                            browser.switch_to.frame('Voicelist')

                    browser.close()
                    browser.switch_to_window(org_window)
                nextlink = browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-2].find_elements_by_tag_name('a')
                
            browser.quit()
    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_tky.columns)
        df_tky = df_tky.append(record,ignore_index=True)
        browser.quit()
        
    return df_tky


if __name__ == '__main__':
    tokyo()
