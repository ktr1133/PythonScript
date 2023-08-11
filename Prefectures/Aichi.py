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
from urllib.parse import urljoin


#愛知
def aichi(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='B']['URL'][22]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='B']['name'][22]
    df_aic = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        links = browser.find_elements_by_class_name('nav-searchlink')
        hrefs = []
        for link in links:
            hrefs.append(link.get_attribute('href'))
        for href in hrefs:
            if 'search-meeting' in href:
                browser.close()
                MTurl = urljoin(BookMarkURL, href)
                browser = webdriver.Chrome(ChromeDriverManager().install())
                sleep(3)
                browser.get(MTurl)
                #会議種類の選択
                MTList = browser.find_element_by_id('cabinet').find_elements_by_tag_name('option')
                actions = ActionChains(browser)
                actions.key_down(keys.SHIFT)
                for mt_ele in MTList:
                    if '本会議' in mt_ele.text:
                        actions.click(mt_ele)
                        actions.perform()

                #文書種類の選別
                classList = browser.find_element_by_id('class').find_elements_by_tag_name('option')
                for class_ele in classList:
                    if '本文' in class_ele.text:
                        class_ele.click()

                browser.find_element_by_css_selector("button[type='submit']").click()
                sleep(1)
                #新しいページに移動
                browser.switch_to.window(browser.window_handles[-1])
                #検索ワード入力
                browser.find_element_by_css_selector("input[type='text']").send_keys(SearchWord) 
                #検索実行
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
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_aic.columns)
            df_aic = df_aic.append(record,ignore_index=True)
            browser.quit()

        else:
            Name = BookMarkName
            JournalTitles_div = browser.find_elements_by_css_selector('div[class="result-doc__title"]')
            for i in range(len(JournalTitles_div)):
                JournalTitles_div = browser.find_elements_by_css_selector('div[class="result-doc__title"]')
                JournalTitle = JournalTitles_div[i].text
                actions = ActionChains(browser)
                actions.key_down(keys.SHIFT)
                actions.click(JournalTitles_div[i].find_element_by_tag_name('a'))
                actions.perform()
                sleep(2)
                browser.switch_to.window(browser.window_handles[-1])
                Date = browser.find_element_by_css_selector('section[class="command"]').find_element_by_class_name('command__date').text
                voicelist_candidates = browser.find_element_by_id('voiceList').find_elements_by_tag_name('li')
                voicelist = []
                for ele in voicelist_candidates:
                    if len(ele.find_element_by_tag_name('button').find_elements_by_tag_name('span')) == 4:
                        voicelist.append(ele)
                num = 1
                for j in range(len(voicelist)):
                    Speaker = voicelist[j].find_element_by_tag_name('button').find_elements_by_tag_name('span')[3].text
                    if '議長' not in Speaker and '委員長' not in Speaker:
                        SpeakOrder = num
                        voicenum = voicelist[j].find_element_by_tag_name('button').find_element_by_class_name('voice__number').text
                        litag = browser.find_element_by_css_selector('ul[class="page-list"]').find_element_by_css_selector('li[data-voice-no="{}"]'.format(voicenum))
                        Remark = litag.find_element_by_tag_name('p').text
                        record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_aic.columns)
                        df_aic = df_aic.append(record,ignore_index=True)
                        num += 1
                browser.close()
                browser.switch_to_window(org_window)
                sleep(2)

            while browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_elements_by_tag_name('a') != []:
                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-1].find_element_by_tag_name('a').click()
                sleep(2)
                browser.switch_to.window(browser.window_handles[-1])
                org_window = browser.current_window_handle
                JournalTitles_div = browser.find_elements_by_css_selector('div[class="result-doc__title"]')
                for i in range(len(JournalTitles_div)):
                    JournalTitles_div = browser.find_elements_by_css_selector('div[class="result-doc__title"]')
                    JournalTitle = JournalTitles_div[i].text
                    actions = ActionChains(browser)
                    actions.key_down(keys.SHIFT)
                    actions.click(JournalTitles_div[i].find_element_by_tag_name('a'))
                    actions.perform()
                    sleep(2)
                    browser.switch_to.window(browser.window_handles[-1])
                    Date = browser.find_element_by_css_selector('section[class="command"]').find_element_by_class_name('command__date').text
                    voicelist_candidates = browser.find_element_by_id('voiceList').find_elements_by_tag_name('li')
                    voicelist = []
                    for ele in voicelist_candidates:
                        if len(ele.find_element_by_tag_name('button').find_elements_by_tag_name('span')) == 4:
                            voicelist.append(ele)
                    num = 1
                    for j in range(len(voicelist)):
                        Speaker = voicelist[j].find_element_by_tag_name('button').find_elements_by_tag_name('span')[3].text
                        if '議長' not in Speaker and '委員長' not in Speaker:
                            SpeakOrder = num
                            voicenum = voicelist[j].find_element_by_tag_name('button').find_element_by_class_name('voice__number').text
                            litag = browser.find_element_by_css_selector('ul[class="page-list"]').find_element_by_css_selector('li[data-voice-no="{}"]'.format(voicenum))
                            Remark = litag.find_element_by_tag_name('p').text
                            record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_aic.columns)
                            df_aic = df_aic.append(record,ignore_index=True)
                            num += 1
                    browser.close()
                    browser.switch_to_window(org_window)
                    sleep(2)

            browser.quit()

    except:
        error = 'error'
        Name = BookMarkName
        SearchWord = SearchWord
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_aic.columns)
        df_aic = df_aic.append(record,ignore_index=True)
        browser.quit()

    return df_aic

if __name__ == '__main__':
    aichi()
