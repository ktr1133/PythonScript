#!/usr/bin/env python
# coding: utf-8

# In[ ]:
#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import pandas as pd
#ｳｪﾌﾞｽｸﾚｲﾋﾟﾝｸﾞ用ﾗｲﾌﾞﾗﾘ
from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

from time import sleep
#正規表現
import re

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')


#静岡
def shizuoka(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='H']['URL'][21]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='H']['name'][21]
    df_szo = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        if '　' in SearchWord:
            SearchWords = SearchWord.split('　')
            SearchWordInputs_temp = browser.find_elements_by_css_selector('input[name^="word"]')
            SearchWordInputs = []
            for i in range(len(SearchWords)):
                SearchWordInputs.append(SearchWordInputs_temp[i])
            for ele1,ele2 in zip(SearchWords, SearchWordInputs):
                ele2.send_keys(ele1)
        elif ' ' in SearchWord:
            SearchWords = SearchWord.split(' ')
            SearchWordInputs_temp = browser.find_elements_by_css_selector('input[name^="word"]')
            SearchWordInputs = []
            for i in range(len(SearchWords)):
                SearchWordInputs.append(SearchWordInputs_temp[i])
            for ele1,ele2 in zip(SearchWords, SearchWordInputs):
                ele2.send_keys(ele1)
        else:
            browser.find_element_by_css_selector('input[name="word11"]').send_keys(SearchWord)
        
        sleep(1)
        browser.find_element_by_css_selector('input[value="上記条件で検索を開始する"]').click()
        sleep(3)

        resultlist_temp = browser.find_element_by_id('tmp_contents').find_elements_by_tag_name('tbody')
        if resultlist_temp == []:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_szo.columns)
            df_szo = df_szo.append(record,ignore_index=True)
            browser.quit()
        else:
            resultlist = browser.find_element_by_id('tmp_contents').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')

            record_temps = []
            de_records1 = []
            de_records2 = []
            de_records3 = []
            for i in range(len(resultlist)):
                resultlist = browser.find_element_by_id('tmp_contents').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
                if resultlist[i].find_elements_by_tag_name('td') != []:
                    if '一般質問' in resultlist[i].find_elements_by_tag_name('td')[1].text:
                        JournalTitle = resultlist[i].find_elements_by_tag_name('td')[3].text
                        resultlist[i].find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').click()
                        sleep(3)
                        Speaker_and_Date_and_PoliticalParty_temp = browser.find_element_by_id('tmp_contents').find_element_by_tag_name('table').find_elements_by_tag_name('tr')
                        Speaker_temp0 = Speaker_and_Date_and_PoliticalParty_temp[0].find_elements_by_tag_name('td')[2].find_elements_by_tag_name('b')[0].text
                        Speaker = re.sub('　', '', Speaker_temp0)
                        if '議長' not in Speaker and '委員長' not in Speaker:
                            Date = Speaker_and_Date_and_PoliticalParty_temp[2].find_elements_by_tag_name('td')[2].text
                            PoliticalParty = Speaker_and_Date_and_PoliticalParty_temp[3].find_elements_by_tag_name('td')[2].text
                            if browser.find_element_by_id('tmp_contents').find_elements_by_tag_name('ul') != []:
                                Remark_temp1 = browser.find_element_by_id('tmp_contents').find_element_by_tag_name('ul').text
                                Remark_temp2 = re.split("(?=○)", Remark_temp1)
                                for ele1 in Remark_temp2:
                                    if Speaker in ele1:
                                        if SearchWord in ele1:
                                            Remark = ele1
                                            SpeakOrder = 'temp'
                                            Name = BookMarkName
                                            record_temp = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, PoliticalParty, Remark], index=df_szo.columns)
                                            record_temps.append(record_temp)

                                browser.back()
                                sleep(3)

                            else:
                                Remark_temp3 = browser.find_element_by_id('tmp_contents').find_elements_by_tag_name('p')[2].text
                                Remark_temp4 = re.split("(?=○)", Remark_temp3)
                                for ele2 in Remark_temp4:
                                    if Speaker in ele2:
                                        if SearchWord in ele2:
                                            Remark = ele2
                                            SpeakOrder = 'temp'
                                            Name = BookMarkName
                                            record_temp = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, PoliticalParty, Remark], index=df_szo.columns)
                                            record_temps.append(record_temp)

                                browser.back()
                                sleep(3)
                        else:
                            browser.back()
                            sleep(3)
                                
                    elif '代表質問' in resultlist[i].find_elements_by_tag_name('td')[1].text:
                        JournalTitle = resultlist[i].find_elements_by_tag_name('td')[3].text
                        resultlist[i].find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').click()
                        sleep(3)
                        Speaker_and_Date_and_PoliticalParty_temp = browser.find_element_by_id('tmp_contents').find_element_by_tag_name('table').find_elements_by_tag_name('tr')
                        Speaker_temp0 = Speaker_and_Date_and_PoliticalParty_temp[0].find_elements_by_tag_name('td')[2].find_elements_by_tag_name('b')[0].text
                        Speaker = re.sub('　', '', Speaker_temp0)
                        if '議長' not in Speaker and '委員長' not in Speaker:
                            Date = Speaker_and_Date_and_PoliticalParty_temp[2].find_elements_by_tag_name('td')[2].text
                            PoliticalParty = Speaker_and_Date_and_PoliticalParty_temp[3].find_elements_by_tag_name('td')[2].text
                            if browser.find_element_by_id('tmp_contents').find_elements_by_tag_name('ul') != []:
                                Remark_temp5 = browser.find_element_by_id('tmp_contents').find_element_by_tag_name('ul').text
                                Remark_temp6 = re.split("(?=○)", Remark_temp5)
                                for ele3 in Remark_temp6:
                                    if Speaker in ele3:
                                        if SearchWord in ele3:
                                            Remark = ele3
                                            SpeakOrder = 'temp'
                                            Name = BookMarkName
                                            record_temp = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, PoliticalParty, Remark], index=df_szo.columns)
                                            record_temps.append(record_temp)

                                browser.back()
                                sleep(3)

                            else:
                                Remark_temp7 = browser.find_element_by_id('tmp_contents').find_elements_by_tag_name('p')[2].text
                                Remark_temp8 = re.split("(?=○)", Remark_temp7)
                                for ele4 in Remark_temp8:
                                    if Speaker in ele4:
                                        if '議長' not in Speaker and '委員長' not in Speaker:
                                            if SearchWord in ele4:
                                                Remark = ele4
                                                SpeakOrder = 'temp'
                                                Name = BookMarkName
                                                record_temp = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, PoliticalParty, Remark], index=df_szo.columns)
                                                record_temps.append(record_temp)

                                browser.back()
                                sleep(3)

                        else:
                            browser.back()
                            sleep(3)
                                
                    elif '答弁' in resultlist[i].find_elements_by_tag_name('td')[1].text:
                        JournalTitle = resultlist[i].find_elements_by_tag_name('td')[3].text
                        resultlist[i].find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').click()
                        sleep(3)
                        Speaker_temp = browser.find_element_by_id('tmp_contents').find_element_by_tag_name('tbody').find_element_by_css_selector('tr[valign="top"]').find_elements_by_tag_name('td')[3].text
                        if '（再質問）' in Speaker_temp:
                            Speaker_temp = re.sub('（再質問）', '', Speaker_temp)
                        if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                            Date = browser.find_element_by_id('tmp_contents').find_element_by_css_selector('div[align="right"]').find_elements_by_tag_name('b')[1].text
                            Remark_temp9 = browser.find_element_by_id('tmp_contents').find_elements_by_tag_name('font')
                            Remark_temp10 = []
                            for ele5 in Remark_temp9:
                                Remark_temp10.append(ele5.text)
                            Remark_temp11 = ''.join(Remark_temp10)    
                            Remark_temp12 = re.split("(?=○)", Remark_temp11)
                            for ele6 in Remark_temp12:
                                if Speaker_temp in ele6:
                                    if SearchWord in ele6:
                                        Remark = ele6
                                        Speaker = ele6.split('　')[0]
                                        SpeakOrder = 'temp'
                                        Name = BookMarkName
                                        PoliticalParty = ''
                                        record_temp = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, PoliticalParty, Remark], index=df_szo.columns)
                                        record_temps.append(record_temp)
                            browser.back()
                            sleep(3)
                        else:
                            browser.back()
                            sleep(3)

                    else:
                        pass

                else:
                    pass

            browser.quit()    
            for k in range(len(record_temps)):
                if k -1 == -1:
                    SpeakOrder = 1
                    record_temps[k]['SpeakOrder'] = SpeakOrder
                else:
                    if record_temps[k]['JournalTitle'] == record_temps[k-1]['JournalTitle']:
                        if record_temps[k]['Date'] == record_temps[k-1]['Date']:
                            record_temps[k]['SpeakOrder'] = record_temps[k-1]['SpeakOrder'] +1
                        else:
                            record_temps[k]['SpeakOrder'] = 1
                    else:
                        record_temps[k]['SpeakOrder'] = 1

            for record in record_temps:            
                df_szo = df_szo.append(record,ignore_index=True)

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_szo.columns)
        df_szo = df_szo.append(record,ignore_index=True)
        browser.quit()
            
    return df_szo


if __name__ == '__main__':
    shizuoka()
