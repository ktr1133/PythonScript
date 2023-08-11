#!/usr/bin/env python
# coding: utf-8

# In[ ]:
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


#福島
def fukushima(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='D']['URL'][6]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='D']['name'][6]
    df_fksm = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        Name = BookMarkName
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        #検索ワード入力
        browser.find_element_by_id('in-detail-keywords').send_keys(SearchWord)
        #会議内容選択
        checkboxes = browser.find_elements_by_class_name('checkbox')
        checkboxes[0].click()
        checkboxes[1].click()
        checkboxes[2].click()
        checkboxes[3].click()
        checkboxes[6].click()
        checkboxes[7].click()
        checkboxes[8].click()
        #会議種類選択
        checkboxes[-1].click()

        #検索実行
        browser.find_element_by_id('v-search').click()

        sleep(3)

        org_window = browser.current_window_handle
        slideList_temp = browser.find_elements_by_class_name('slick-track')
        if slideList_temp == []:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_fksm.columns)
            df_fksm = df_fksm.append(record,ignore_index=True) 
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
                parentlist = browser.find_element_by_id('tbl-hit-result').find_elements_by_class_name('schedule')
                if parentlist != []:
                    for i in range(len(parentlist)):
                        parentlist = browser.find_element_by_id('tbl-hit-result').find_elements_by_class_name('schedule')
                        JournalTitle = parentlist[i].find_element_by_tag_name('span').text.split(' ')[0]
                        Date = JournalTitle.split('年')[0]+"年"+parentlist[i].find_element_by_tag_name('span').text.split(' ')[-2].split('－')[0]
                        if parentlist[i].find_element_by_tag_name('img').get_attribute('class') != 'rotate':
                            parentlist[i].click()
                            sleep(2)
                        childlist = parentlist[i].find_elements_by_class_name('minute ')
                        num = 1
                        browser.execute_script('arguments[0].click();', childlist[0])
                        sleep(3)
                        Remark_step1 = browser.find_elements_by_tag_name('pre')
                        Remark_step2 = []
                        for ele in Remark_step1:
                            Remark_step2.append(ele.text)
                        num = 1
                        for ele in Remark_step2:
                            if '\u3000' in SearchWord:
                                SearchWords = SearchWord.split('\u3000')
                                if SearchWords[0] in ele.text and SearchWords[1] in ele.text:
                                    Remark = re.sub(r"[\n]", "",ele.text,count=0,flags=0)
                                    if "◆" in Remark.split('　')[0]:
                                        Speaker = Remark.split('◆')[1].split('　')[0]
                                        SpeakOrder = num
                                    elif "◎" in Remark.split('　')[0]:
                                        Speaker = Remark.split('◎')[1].split('　')[0]
                                        SpeakOrder = num

                                    #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                                    record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_fksm.columns)
                                    df_fksm = df_fksm.append(record,ignore_index=True)

                                    #繰り返し後の準備
                                    num = num+1

                            else:
                                if SearchWord in ele.text:
                                    Remark = re.sub(r"[\n]", "",ele.text,count=0,flags=0)
                                    if "◆" in Remark.split('　')[0]:
                                        Speaker = Remark.split('◆')[1].split('　')[0]
                                        SpeakOrder = num
                                    elif "◎" in Remark.split('　')[0]:
                                        Speaker = Remark.split('◎')[1].split('　')[0]
                                        SpeakOrder = num

                                    #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                                    record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_fksm.columns)
                                    df_fksm = df_fksm.append(record,ignore_index=True)

                                    #繰り返し後の準備
                                    num = num+1

                        browser.find_element_by_id('exit_icon').click()
                        sleep(5)
                        browser.switch_to_window(org_window)
            browser.quit()
            
    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_fksm.columns)
        df_fksm = df_fksm.append(record,ignore_index=True)
        browser.quit()

    return df_fksm


# In[ ]:


if __name__ == '__main__':
    fukushima()
