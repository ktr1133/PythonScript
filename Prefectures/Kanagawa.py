#!/usr/bin/env python
# coding: utf-8
#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import sqlite3
import pandas as pd
#ｳｪﾌﾞｽｸﾚｲﾋﾟﾝｸﾞ用ﾗｲﾌﾞﾗﾘ
from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager

from time import sleep

#正規表現
import re

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')


#神奈川
def kanagawa(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='D']['URL'][13]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='D']['name'][13]
    df_kng = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.implicitly_wait(20)
        browser.get(BookMarkURL)
        Name = BookMarkName

        #検索ワード入力
        browser.find_element_by_id('in-detail-keywords').send_keys(SearchWord)
        #会議内容選択
        checkboxes = browser.find_elements_by_css_selector('label[class="checkbox"]')
        checkboxes[0].click()
        checkboxes[1].click()
        checkboxes[2].click()
        checkboxes[3].click()
        checkboxes[6].click()
        checkboxes[7].click()
        checkboxes[8].click()
        checkboxes[12].click()


        #検索実行
        browser.find_element_by_id('v-search').click()

        browser.implicitly_wait(20)

        org_window = browser.current_window_handle
        slideList_temp = browser.find_elements_by_class_name('slick-track')
        if slideList_temp == []:
            not_applicable = '該当する文書は存在しません。'
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_kng.columns)
            df_kng = df_kng.append(record,ignore_index=True) 
            browser.quit()
        else:
            slideList = browser.find_element_by_class_name('slick-track').find_elements_by_tag_name("div")

            for i in range(len(slideList)):
                slideList = browser.find_element_by_class_name('slick-track').find_elements_by_tag_name("div")
                try:
                    browser.implicitly_wait(5)
                    slideList[i].click()
                    sleep(3)
                except:
                    slickbutton = browser.find_element_by_css_selector('div[id="hit-year-slick"] > button[class="slick-next slick-arrow"]')
                    browser.execute_script('arguments[0].click();', slickbutton)
                    try:
                        browser.implicitly_wait(5)
                        slideList[i].click()
                        sleep(3)
                    except:
                        slickbutton = browser.find_element_by_css_selector('div[id="hit-year-slick"] > button[class="slick-next slick-arrow"]')
                        browser.execute_script('arguments[0].click();', slickbutton)
                        try:
                            browser.implicitly_wait(5)
                            slideList[i].click()
                            sleep(3)
                        except:
                            slickbutton = browser.find_element_by_css_selector('div[id="hit-year-slick"] > button[class="slick-next slick-arrow"]')
                            browser.execute_script('arguments[0].click();', slickbutton)
                            try:
                                browser.implicitly_wait(5)
                                slideList[i].click()
                                sleep(3)
                            except:
                                slickbutton = browser.find_element_by_css_selector('div[id="hit-year-slick"] > button[class="slick-next slick-arrow"]')
                                browser.execute_script('arguments[0].click();', slickbutton)
                                browser.implicitly_wait(5)
                                slideList[i].click()
                                sleep(3)

                parentlist = browser.find_elements_by_css_selector('li[class="schedule"]')
                if parentlist != []:
                    for j in range(len(parentlist)):
                        sleep(2)
                        parentlist = browser.find_elements_by_css_selector('li[class="schedule"]')
                        JournalTitle = parentlist[j].find_element_by_tag_name('span').text.split(' ')[0]
                        Date = JournalTitle.split('年')[0]+"年"+parentlist[j].find_element_by_tag_name('span').text.split(' ')[-2].split('－')[0]

                        if parentlist[j].find_element_by_tag_name('img').get_attribute('class') != 'rotate':
                            parentlist[j].click()
                            browser.implicitly_wait(20)

                        childlist = parentlist[j].find_elements_by_class_name('minute ')
                        num = 1
                        browser.execute_script('arguments[0].click();', childlist[0])
                        browser.implicitly_wait(20)
                        Remark_temp = browser.find_elements_by_tag_name('pre')

                        num = 1
                        for ele in Remark_temp:
                            if '\u3000' in SearchWord:
                                SearchWords = SearchWord.split('\u3000')
                                if (SearchWords[0] in ele.text) and (SearchWords[1] in ele.text) and ('△' not in ele.text):
                                    Remark = re.sub(r"[\n]", "",ele.text,count=0,flags=0)
                                    if "◆" in Remark.split('　')[0]:
                                        Speaker = Remark.split('◆')[1].split('　')[0]
                                        SpeakOrder = num
                                    elif "◎" in Remark.split('　')[0]:
                                        Speaker = Remark.split('◎')[1].split('　')[0]
                                        SpeakOrder = num

                                    #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                                    record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_kng.columns)
                                    df_kng = df_kng.append(record,ignore_index=True)

                                    #繰り返し後の準備
                                    num = num+1

                            else:
                                if (SearchWord in ele.text) and ('△' not in ele.text):
                                    Remark = re.sub(r"[\n]", "",ele.text,count=0,flags=0)
                                    if "◆" in Remark.split('　')[0]:
                                        Speaker = Remark.split('◆')[1].split('　')[0]
                                        SpeakOrder = num
                                    elif "◎" in Remark.split('　')[0]:
                                        Speaker = Remark.split('◎')[1].split('　')[0]
                                        SpeakOrder = num

                                    #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                                    record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_kng.columns)
                                    df_kng = df_kng.append(record,ignore_index=True)

                                    #繰り返し後の準備
                                    num = num+1

                        browser.find_element_by_id('exit_icon').click()
                        browser.implicitly_wait(20)
                        browser.switch_to_window(org_window)
            browser.quit()
    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_kng.columns)
        df_kng = df_kng.append(record,ignore_index=True)
        browser.quit()
            
    return df_kng
    

if __name__ == '__main__':
    kanagawa()
