#!/usr/bin/env python
# coding: utf-8

#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import pandas as pd
#ｳｪﾌﾞｽｸﾚｲﾋﾟﾝｸﾞ用ﾗｲﾌﾞﾗﾘ
from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

from time import sleep

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')


#岩手
def iwate(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='C']['URL'][2]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='C']['name'][2]
    df_iwt = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)
        Name = BookMarkName

        browser.switch_to.frame('SearchFrame')

        if '　' in SearchWord:
            SearchWords = SearchWord.split('　')
            SearchWordInputs_temp = browser.find_elements_by_css_selector('input[name^="keyword"]')
            SearchWordInputs = []
            for i in range(len(SearchWords)):
                SearchWordInputs.append(SearchWordInputs_temp[i])
            for ele1,ele2 in zip(SearchWords, SearchWordInputs):
                ele2.send_keys(ele1)
        elif ' ' in SearchWord:
            SearchWords = SearchWord.split(' ')
            SearchWordInputs_temp = browser.find_elements_by_css_selector('input[name^="keyword"]')
            SearchWordInputs = []
            for i in range(len(SearchWords)):
                SearchWordInputs.append(SearchWordInputs_temp[i])
            for ele1,ele2 in zip(SearchWords, SearchWordInputs):
                ele2.send_keys(ele1)
        else:
            SearchWordInput = browser.find_element_by_css_selector('input[name="keyword1"]')
            SearchWordInput.send_keys(SearchWord)

        #会議選択
        browser.find_element_by_css_selector('input[name="honkaigiAllCheckButton"]').click()
        #検索実行
        sleep(1)
        browser.find_element_by_css_selector("input[value='検　索']").click()

        browser.switch_to_default_content()
        browser.switch_to.frame('ResultFrame')

        if '条件を満たすデータが見つかりません。' in browser.find_element_by_tag_name('body').text:
            not_applicable = '該当する文書は存在しません。'
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_iwt.columns)
            df_iwt = df_iwt.append(record,ignore_index=True) 
            browser.quit()

        else:    
            hits = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[1].find_elements_by_tag_name('tr')
            records_temp = []
            for i in range(len(hits)):
                hits = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[1].find_elements_by_tag_name('tr')
                JournalTitle = hits[i].find_element_by_tag_name('a').text.split('(')[0]
                Date = hits[i].find_element_by_tag_name('a').text.split('年')[0] + "年" + hits[i].find_element_by_tag_name('a').text.split('(')[1].split(')')[0]
                Speaker_temp = hits[i].find_element_by_tag_name('a').text.split('　')[2]
                if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                    if '議事日程' not in Speaker_temp:
                        Speaker = Speaker_temp
                        speakerCandidate = hits[i].find_element_by_tag_name('a').text.split(')　')[1]
                        org_window = browser.current_window_handle
                        hits[i].click()
                        browser.switch_to.window(browser.window_handles[-1])
                        browser.switch_to.frame('leftFrame')

                        speakerTable = browser.find_element_by_tag_name('table')
                        trtags = speakerTable.find_elements_by_tag_name('tr')
                        atags= []
                        for ele in trtags:
                            tdtags = ele.find_elements_by_tag_name('td')
                            for l in range(len(tdtags)):
                                tdtags = ele.find_elements_by_tag_name('td')
                                if tdtags[l].find_elements_by_tag_name('a')!=[]:
                                    atags.append(tdtags[l].find_element_by_tag_name('a'))

                        speakerCandidate_temp = []    
                        for ele3 in atags:
                            try:
                                if '#hit' in ele3.get_attribute('href'):
                                    speakerCandidate_temp.append(ele3)
                            except:
                                pass

                        for j in range(len(speakerCandidate_temp)):
                            if speakerCandidate_temp[j].text.split('（')[1].split('君')[0] in speakerCandidate:
                                frame_target = speakerCandidate_temp[j].get_attribute('target')
                                speakerCandidate_temp[j].click()
                                sleep(2)
                                browser.switch_to_default_content()
                                browser.switch_to.frame(frame_target)
                                Remark = browser.find_element_by_tag_name('p').text
                                SpeakOrder = 'temp'
                                record_temp = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_iwt.columns)
                                records_temp.append(record_temp)
                                browser.switch_to_default_content()
                                browser.switch_to.frame('leftFrame')

                        browser.close()
                        browser.switch_to.window(org_window)
                        browser.switch_to.frame('ResultFrame')

            nextlink_candidate = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[2].find_elements_by_tag_name('td')[2]            
            while browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[2].find_elements_by_tag_name('td')[2].find_elements_by_tag_name('a') != []:
                nextlink_candidate = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[2].find_elements_by_tag_name('td')[2]
                nextlink_candidate.find_element_by_tag_name('a').click()
                sleep(3)

                browser.switch_to_default_content()
                browser.switch_to.frame('ResultFrame')

                hits = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[1].find_elements_by_tag_name('tr')
                for i in range(len(hits)):
                    hits = browser.find_element_by_tag_name('center').find_elements_by_tag_name('table')[1].find_elements_by_tag_name('tr')
                    JournalTitle = hits[i].find_element_by_tag_name('a').text.split('(')[0]
                    Date = hits[i].find_element_by_tag_name('a').text.split('年')[0] + "年" + hits[i].find_element_by_tag_name('a').text.split('(')[1].split(')')[0]
                    Speaker_temp = hits[i].find_element_by_tag_name('a').text.split('　')[2]
                    if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                        if '議事日程' not in Speaker_temp:
                            Speaker = Speaker_temp
                            speakerCandidate = hits[i].find_element_by_tag_name('a').text.split(')　')[1]

                            org_window = browser.current_window_handle
                            hits[i].click()
                            browser.switch_to.window(browser.window_handles[-1])
                            browser.switch_to.frame('leftFrame')

                            speakerTable = browser.find_element_by_tag_name('table')
                            trtags = speakerTable.find_elements_by_tag_name('tr')
                            atags= []
                            for ele in trtags:
                                tdtags = ele.find_elements_by_tag_name('td')
                                for l in range(len(tdtags)):
                                    tdtags = ele.find_elements_by_tag_name('td')
                                    if tdtags[l].find_elements_by_tag_name('a')!=[]:
                                        atags.append(tdtags[l].find_element_by_tag_name('a'))

                            speakerCandidate_temp = []    
                            for ele3 in atags:
                                try:
                                    if '#hit' in ele3.get_attribute('href'):
                                        speakerCandidate_temp.append(ele3)
                                except:
                                    pass

                            for j in range(len(speakerCandidate_temp)):
                                if speakerCandidate_temp[j].text.split('（')[1].split('君')[0] in speakerCandidate:
                                    frame_target = speakerCandidate_temp[j].get_attribute('target')
                                    speakerCandidate_temp[j].click()
                                    sleep(2)
                                    browser.switch_to_default_content()
                                    browser.switch_to.frame(frame_target)
                                    Remark = browser.find_element_by_tag_name('p').text
                                    SpeakOrder = 'temp'
                                    record_temp = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_iwt.columns)
                                    records_temp.append(record_temp)
                                    browser.switch_to_default_content()
                                    browser.switch_to.frame('leftFrame')

                            browser.close()
                            browser.switch_to.window(org_window)
                            browser.switch_to.frame('ResultFrame')  

            browser.quit()

        for k in range(len(records_temp)):
            if k -1 == -1:
                SpeakOrder = 1
                records_temp[k]['SpeakOrder'] = SpeakOrder
            else:
                if records_temp[k]['JournalTitle'] == records_temp[k-1]['JournalTitle']:
                    if records_temp[k]['Date'] == records_temp[k-1]['Date']:
                        records_temp[k]['SpeakOrder'] = records_temp[k-1]['SpeakOrder'] +1
                    else:
                        records_temp[k]['SpeakOrder'] = 1
                else:
                    records_temp[k]['SpeakOrder'] = 1

        for record in records_temp:            
            df_iwt = df_iwt.append(record,ignore_index=True)


    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_iwt.columns)
        df_iwt = df_iwt.append(record,ignore_index=True)
        browser.quit()
            
    return df_iwt

if __name__ == '__main__':
    iwate()
