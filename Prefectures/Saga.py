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
#正規表現
import re

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')


#佐賀
def saga(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='B']['URL'][40]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='B']['name'][40]
    df_sg = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        browser.find_element_by_tag_name('textarea').send_keys(SearchWord) 
        #会議種類の選択
        MTList = browser.find_element_by_name('Cabinet[]').find_elements_by_tag_name('option')
        actions = ActionChains(browser)
        actions.key_down(keys.SHIFT)
        for mt_ele in MTList:
            if '本会議' in mt_ele.text:
                actions.click(mt_ele)
                actions.perform()
        #文書種類の選別
        classList = browser.find_element_by_name('Class[]').find_elements_by_tag_name('option')
        for class_ele in classList:
            if '本文' in class_ele.text:
                class_ele.click()
        browser.find_element_by_css_selector("input[type='submit']").click()

        sleep(3)
        #新しく開いたｳｨﾝﾄﾞｳに移動
        browser.switch_to.window(browser.window_handles[-1])

        #検索結果の全ての文書のaタグ情報を取得
        org_window = browser.current_window_handle
        JURLList2_step1 = browser.find_elements_by_class_name("result-list") #広島、佐賀

        if browser.find_elements_by_css_selector('div[class="result-list-nohit"]') != []:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_sg.columns)
            df_sg = df_sg.append(record,ignore_index=True)
            browser.quit()

        else:
            Speakers_temp = []
            journal_titles = []
            SpeakOrder_temp = []
            nextlinks = []
            RemarkNumbers = []
            JURLs_temp = []
            for ele in JURLList2_step1:
                journal_title_and_date = ele.find_element_by_tag_name('a').text
                JournalTitle = journal_title_and_date.split(' ')[0]
                Date = re.sub('開催日：', '', ele.find_element_by_css_selector("span[class='result-document-date']").text)
                num = 1
                ele2 = ele.find_element_by_tag_name('a')
                actions = ActionChains(browser)
                actions.key_down(keys.SHIFT)
                actions.click(ele2)
                actions.perform()
                sleep(1)
                browser.switch_to.window(browser.window_handles[-1])
                browser.switch_to_frame("Voicelist")
                Speakers_temp = browser.find_elements_by_class_name("HitVoice")
                Name = BookMarkName
                SearchWord = SearchWord
                num = 1
                for ele in Speakers_temp:
                    ele.click()
                    sleep(2)
                    browser.switch_to_default_content()
                    browser.switch_to_frame("Page")
                    Speaker = browser.find_element_by_tag_name("h2").text
                    if '議長' not in Speaker and '委員長' not in Speaker:
                        if '◎' in Speaker:
                            ptags = browser.find_elements_by_tag_name("p")
                            Remark = ptags[1].text
                            SpeakOrder = num
                            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                            record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_sg.columns)
                            df_sg = df_sg.append(record,ignore_index=True)
                            num = num+1
                    browser.switch_to_default_content()
                    browser.switch_to_frame("Voicelist")

                browser.close()
                browser.switch_to.window(org_window)

            while browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-2].find_elements_by_tag_name('a') != []:
                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-2].find_element_by_tag_name('a').click()
                sleep(2)
                browser.switch_to.window(browser.window_handles[-1])
                org_window = browser.current_window_handle
                JURLList2_step2 = browser.find_elements_by_class_name("result-list")

                for ele in JURLList2_step2:
                    journal_title_and_date = ele.find_element_by_tag_name('a').text
                    JournalTitle = journal_title_and_date.split(' ')[0]
                    Date = re.sub('開催日：', '', ele.find_element_by_css_selector("span[class='result-document-date']").text)
                    num = 1
                    ele2 = ele.find_element_by_tag_name('a')
                    actions = ActionChains(browser)
                    actions.key_down(keys.SHIFT)
                    actions.click(ele2)
                    actions.perform()
                    sleep(1)
                    browser.switch_to.window(browser.window_handles[-1])
                    browser.switch_to_frame("Voicelist")
                    Speakers_temp = browser.find_elements_by_class_name("HitVoice")
                    Name = BookMarkName
                    SearchWord = SearchWord
                    num = 1
                    for ele in Speakers_temp:
                        ele.click()
                        sleep(2)
                        browser.switch_to_default_content()
                        browser.switch_to_frame("Page")
                        Speaker = browser.find_element_by_tag_name("h2").text
                        if '議長' not in Speaker and '委員長' not in Speaker:
                            if '◎' in Speaker:
                                ptags = browser.find_elements_by_tag_name("p")
                                Remark = ptags[1].text
                                SpeakOrder = num
                                #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                                record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_sg.columns)
                                df_sg = df_sg.append(record,ignore_index=True)
                                num = num+1
                        browser.switch_to_default_content()
                        browser.switch_to_frame("Voicelist")

                    browser.close()
                    browser.switch_to.window(org_window)

            browser.quit()

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_sg.columns)
        df_sg = df_sg.append(record,ignore_index=True)
        browser.quit()
        
    return df_sg

if __name__ == '__main__':
    saga()
