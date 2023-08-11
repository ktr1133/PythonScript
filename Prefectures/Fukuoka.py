#!/usr/bin/env python
# coding: utf-8

#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import sqlite3
import pandas as pd
#ｳｪﾌﾞｽｸﾚｲﾋﾟﾝｸﾞ用ﾗｲﾌﾞﾗﾘ
from selenium import webdriver
from selenium.webdriver.common.keys import Keys as keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

from webdriver_manager.chrome import ChromeDriverManager

from time import sleep

#正規表現
import re

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')


#福岡
def fukuoka(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='B']['URL'][39]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='B']['name'][39]
    df_fko = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        browser.find_element_by_class_name('start').find_element_by_tag_name('a').click()
        sleep(1)
        for ele in browser.find_elements_by_class_name('glink__item'):
            try:
                if 'search-meeting' in ele.get_attribute('href'):
                    link = ele
            except TypeError:
                pass
        link.click()
        sleep(1)
        MTList = browser.find_element_by_id('cabinet1').find_elements_by_tag_name('option')
        actions = ActionChains(browser)
        actions.key_down(keys.SHIFT)
        for mt_ele in MTList:
            if '本会議' in mt_ele.text:
                actions.click(mt_ele)
                actions.perform()
        #分類選択肢がないルートの設定
        #分類名の選別
        classList = browser.find_element_by_id('class1').find_elements_by_tag_name('option')
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

        if browser.find_element_by_css_selector("div[class='result-doc--nohit']") != "":
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_fko.columns)
            df_fko = df_fko.append(record,ignore_index=True)
            browser.quit()
        
        #検索結果の全ての文書のaタグ情報を取得
        org_window = browser.current_window_handle
        JURLList1_step1 = browser.find_elements_by_class_name("result-doc") #青森、茨城、東京、福井、富山、山梨、愛知、京都、島根、福岡
        #発言、会議名、議会日時取得
        for ele1 in JURLList1_step1:
            ele2 = ele1.find_element_by_tag_name('a')
            JournalTitle = ele1.find_element_by_css_selector("a[class='result-title__name']").text
            Date = re.sub('開催日: ', '', ele1.find_element_by_css_selector("span[class='result-title__date']").text)
            actions = ActionChains(browser)
            actions.key_down(keys.SHIFT)
            actions.click(ele2)
            actions.perform()
            sleep(1)
            browser.switch_to.window(browser.window_handles[-1])
            browser.switch_to_frame("Voicelist")
            AllSpeakers = browser.find_elements_by_css_selector("a[target='Page']")
            Name = BookMarkName
            SearchWord = SearchWord
            num = 1
            for ele in AllSpeakers:
                if 'HitVoice' in ele.get_attribute('class'):
                    ele.click()
                    sleep(2)
                    SpeakOrder_temp = num
                    browser.switch_to_default_content()
                    browser.switch_to_frame("Page")
                    Speaker_temp = browser.find_element_by_tag_name("h1").text
                    if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                        Speaker = Speaker_temp
                        SpeakOrder = SpeakOrder_temp
                        Remark = browser.find_element_by_tag_name("p").text
                        #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                        record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_fko.columns)
                        df_fko = df_fko.append(record,ignore_index=True)
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
            JURLList1_step2 = browser.find_elements_by_class_name("result-doc")

            #発言者、発言URL、発言順序取得
            for ele1 in JURLList1_step2:
                ele2 = ele1.find_element_by_tag_name('a')
                JournalTitle = ele1.find_element_by_css_selector("a[class='result-title__name']").text
                Date = re.sub('開催日: ', '', ele1.find_element_by_css_selector("span[class='result-title__date']").text)
                actions = ActionChains(browser)
                actions.key_down(keys.SHIFT)
                actions.click(ele2)
                actions.perform()
                sleep(1)
                browser.switch_to.window(browser.window_handles[-1])
                browser.switch_to_frame("Voicelist")
                AllSpeakers = browser.find_elements_by_css_selector("a[target='Page']")
                Name = BookMarkName
                SearchWord = SearchWord
                num = 1
                for ele in AllSpeakers:
                    if 'HitVoice' in ele.get_attribute('class'):
                        ele.click()
                        sleep(2)
                        SpeakOrder_temp = num
                        browser.switch_to_default_content()
                        browser.switch_to_frame("Page")
                        Speaker_temp = browser.find_element_by_tag_name("h1").text
                        if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                            Speaker = Speaker_temp
                            SpeakOrder = SpeakOrder_temp
                            Remark = browser.find_element_by_tag_name("p").text
                            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                            record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_fko.columns)
                            df_fko = df_fko.append(record,ignore_index=True)
                            num = num+1
                            browser.switch_to_default_content()
                            browser.switch_to_frame("Voicelist")

                browser.close()
                browser.switch_to.window(org_window)

        browser.quit()
        
    except:
        error = 'error'
        msg = traceback.format_exc()
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error+' '+msg], index=df_fko.columns)
        df_fko = df_fko.append(record,ignore_index=True)
        browser.quit()
        
    return df_fko

if __name__ == '__main__':
    fukuoka()
