#!/usr/bin/env python
# coding: utf-8

# In[ ]:
#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import sqlite3
import pandas as pd
#ｳｪﾌﾞｽｸﾚｲﾋﾟﾝｸﾞ用ﾗｲﾌﾞﾗﾘ
from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

from time import sleep

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')


#香川
def kagawa(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='G']['URL'][36]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='G']['name'][36]
    df_kgw = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        #検索ワード入力
        browser.find_element_by_id('content').find_element_by_css_selector('input[name="Phrase[]"]').send_keys(SearchWord)
        #文書の選択
        browser.find_element_by_id('cabinet1').click()
        browser.find_element_by_id('cabinet2').click()
        #分類の選択
        browser.find_element_by_id('classes1').click()
        #検索の実行
        sleep(1)
        browser.find_element_by_css_selector('li[class="submit"]').find_element_by_tag_name('a').click()

        #開いたﾍﾟｰｼﾞに移動
        browser.switch_to.window(browser.window_handles[-1])

        if browser.find_element_by_css_selector('div[class="nohit"]') != "":
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = self
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_kgw.columns)
            df_kgw = df_kgw.append(record,ignore_index=True)
            
        else:
            resultTable = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol')
            documents = resultTable.find_elements_by_class_name('title')
            for i in range(len(documents)):
                documents = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol').find_elements_by_class_name('title')
                Date = documents[i].find_element_by_tag_name('span').text.split('：')[1]
                JournalTitle = documents[i].find_element_by_tag_name('a').text
                documents[i].find_element_by_tag_name('a').click()
                sleep(3)
                iframe = browser.find_element_by_css_selector('frameset')
                browser.switch_to.frame('Voicelist')
                browser.find_element_by_id('list')
                speakerCandidates_temp = browser.find_element_by_id('list').find_elements_by_tag_name('li')
                num = 1
                for j in range(len(speakerCandidates_temp)):
                    speakerCandidates_temp = browser.find_element_by_id('list').find_elements_by_css_selector('li')
                    if 'Hit' in speakerCandidates_temp[j].find_element_by_tag_name('a').get_attribute('class'):
                        Speaker = speakerCandidates_temp[j].find_element_by_css_selector('span[class="voicename"]').text
                        if '議長' not in Speaker and '委員長' not in Speaker:
                            SpeakOrder = num
                            speakerCandidates_temp[j].find_element_by_tag_name('a').click()
                            sleep(3)
                            browser.switch_to_default_content()
                            browser.switch_to.frame('Page')
                            Remark = browser.find_element_by_tag_name('p').text
                            Name = BookMarkName
                            record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_kgw.columns)
                            df_kgw = df_kgw.append(record,ignore_index=True)
                            num = num+1
                            browser.switch_to_default_content()
                            browser.switch_to.frame('Voicelist')

                browser.switch_to_default_content()
                browser.switch_to.frame('Command')
                browser.find_element_by_css_selector('li[class="list"]').find_element_by_tag_name('a').click()
                sleep(3)

            nextlinkCandidate = browser.find_element_by_css_selector('div[class="pagination"]').find_elements_by_tag_name('a')
            if nextlinkCandidate ==[]:
                browser.quit()
            else:
                nextlinkCandidate = browser.find_element_by_css_selector('div[class="pagination"]').find_elements_by_tag_name('a')
                while "次" in nextlinkCandidate[-1].text:
                    nextlinkCandidate = browser.find_element_by_css_selector('div[class="pagination"]').find_elements_by_tag_name('a')
                    nextlinkCandidate[-1].click()
                    sleep(3)

                    resultTable = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol')
                    documents = resultTable.find_elements_by_class_name('title')
                    for i in range(len(documents)):
                        documents = browser.find_element_by_id('resultbox').find_element_by_class_name('recordcol').find_elements_by_class_name('title')
                        Date = documents[i].find_element_by_tag_name('span').text.split('：')[1]
                        JournalTitle = documents[i].find_element_by_tag_name('a').text
                        documents[i].find_element_by_tag_name('a').click()
                        sleep(3)
                        iframe = browser.find_element_by_css_selector('frameset')
                        browser.switch_to.frame('Voicelist')
                        browser.find_element_by_id('list')
                        speakerCandidates_temp = browser.find_element_by_id('list').find_elements_by_tag_name('li')
                        num = 1
                        for j in range(len(speakerCandidates_temp)):
                            speakerCandidates_temp = browser.find_element_by_id('list').find_elements_by_css_selector('li')
                            if 'Hit' in speakerCandidates_temp[j].find_element_by_tag_name('a').get_attribute('class'):
                                Speaker = speakerCandidates_temp[j].find_element_by_css_selector('span[class="voicename"]').text
                                if '議長' not in Speaker and '委員長' not in Speaker:
                                    SpeakOrder = num
                                    speakerCandidates_temp[j].find_element_by_tag_name('a').click()
                                    sleep(3)
                                    browser.switch_to_default_content()
                                    browser.switch_to.frame('Page')
                                    Remark = browser.find_element_by_tag_name('p').text
                                    Name = BookMarkName
                                    record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_kgw.columns)
                                    df_kgw = df_kgw.append(record,ignore_index=True)
                                    num = num+1
                                    browser.switch_to_default_content()
                                    browser.switch_to.frame('Voicelist')

                        browser.switch_to_default_content()
                        browser.switch_to.frame('Command')
                        browser.find_element_by_css_selector('li[class="list"]').find_element_by_tag_name('a').click()
                        sleep(3)

                    nextlinkCandidate = browser.find_element_by_css_selector('div[class="pagination"]').find_elements_by_tag_name('a')

                else:
                    browser.quit()

    except:
        error = 'error'
        msg = traceback.format_exc()
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error+' '+msg], index=df_kgw.columns)
        df_kgw = df_kgw.append(record,ignore_index=True)
        browser.quit()
                    
    return df_kgw


if __name__ == '__main__':
    kagawa()
