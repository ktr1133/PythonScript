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
from bs4 import BeautifulSoup
import requests
#正規表現
import re

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')

#山梨
def yamanashi(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='B']['URL'][18]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='B']['name'][18]
    df_ymn = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)

        browser.find_element_by_css_selector("a[class='lnavlink lnavlink--phrase']").click()
        sleep(1)
        browser.find_element_by_class_name("search-form__textarea").send_keys(SearchWord) 
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
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_ymn.columns)
            df_ymn = df_ymn.append(record,ignore_index=True)
            browser.quit()

        else:
            step1_temp2 = []
            JURLs = []
            SpeakOrder_temp = []
            Speakers_temp = []
            RemarkNumbers = []
            #発言者、発言URL、発言順序取得
            for ele1 in JURLList1_step1:
                step1_temp1 = ele1.find_elements_by_class_name('result-voice__name')
                step1_temp1_2 = ele1.find_elements_by_class_name('result-voice__number')
                num = 1
                for ele2,ele3 in zip(step1_temp1,step1_temp1_2):
                    Speaker_temp = ele2.text
                    if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                        Speaker = ele2.text
                        Speakers_temp.append(Speaker)
                        RemarkNumber = ele3.text
                        RemarkNumbers.append(RemarkNumber)
                        actions = ActionChains(browser)
                        actions.key_down(keys.SHIFT)
                        actions.click(ele2)
                        actions.perform()
                        sleep(1)
                        browser.switch_to.window(browser.window_handles[-1])
                        JURL = browser.current_url
                        JURLs.append(JURL)
                        SpeakOrder_temp.append(num)
                        num = num +1
                        browser.close()
                        browser.switch_to_window(org_window)

            while browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-2].find_elements_by_tag_name('a') != []:
                browser.find_element_by_class_name("pagination").find_elements_by_tag_name('li')[-2].find_element_by_tag_name('a').click()
                sleep(2)
                browser.switch_to.window(browser.window_handles[-1])
                org_window = browser.current_window_handle
                JURLList1_step2 = browser.find_elements_by_class_name("result-doc")
                #発言者、発言URL、発言順序取得
                for ele1 in JURLList1_step1:
                    step1_temp1 = ele1.find_elements_by_class_name('result-voice__name')
                    step1_temp1_2 = ele1.find_elements_by_class_name('result-voice__number')
                    num = 1
                    for ele2,ele3 in zip(step1_temp1,step1_temp1_2):
                        Speaker_temp = ele2.text
                        if '議長' not in Speaker_temp and '委員長' not in Speaker_temp:
                            Speaker = ele2.text
                            Speakers_temp.append(Speaker)
                            RemarkNumber = ele3.text
                            RemarkNumbers.append(RemarkNumber)
                            actions = ActionChains(browser)
                            actions.key_down(keys.SHIFT)
                            actions.click(ele2)
                            actions.perform()
                            sleep(1)
                            browser.switch_to.window(browser.window_handles[-1])
                            JURL = browser.current_url
                            JURLs.append(JURL)
                            SpeakOrder_temp.append(num)
                            num = num +1
                            browser.close()
                            browser.switch_to_window(org_window)

            browser.quit()

            #発言、会議名、議会日時取得
            for JURL,order,Speaker,RemarkNumber in zip(JURLs,SpeakOrder_temp,Speakers_temp,RemarkNumbers):
                with requests.Session() as session: 
                    response = session.get(JURL) 
                    soup = BeautifulSoup(response.content, 'html.parser') 
                    frames = soup.select("frameset frame") #ﾌﾚｰﾑ分割対応
                    if frames != []:
                        for frame in frames:
                            if frame["name"] == 'Page':
                                frame_url = urljoin(BookMarkURL, frame["src"]) 
                                response = session.get(frame_url) 
                                frame_soup_remark = BeautifulSoup(response.content, 'html.parser') 

                                remark_temp = frame_soup_remark.find_all('p', class_='page-text__text border textwrap')
                                if remark_temp != []:
                                    for temp in remark_temp:
                                        if temp.find('span').text+':' == RemarkNumber:
                                            Remark = temp.text
                                else:
                                    Remark = frame_soup_remark.find("p").text

                            elif frame["name"] == 'Command':
                                frame_url = urljoin(BookMarkURL, frame["src"]) 
                                response = session.get(frame_url) 
                                frame_soup_title = BeautifulSoup(response.content, 'html.parser') 
                                JournalTitle_and_Date = frame_soup_title.find("h2").text
                                JournalTitle = JournalTitle_and_Date.split(" ")[0]
                                Date = JournalTitle_and_Date.split(" ")[-1]

                    else:
                        JournalTitle_and_Date = soup.find(class_="command__title").text
                        JournalTitle = JournalTitle_and_Date.split(" ")[0]
                        if '年' not in JournalTitle:
                            a = JournalTitle_and_Date.split(" ")
                            b = []
                            for ele in a:
                                if ele != '':
                                    b.append(ele)
                            JournalTitle = b[1]
                        else:
                            JournalTitle = JournalTitle
                        Date = JournalTitle_and_Date.split(" ")[-1]
                        remark_temp = soup.find_all('p', class_='page-text__text textwrap')
                        if remark_temp != []:
                            for temp in remark_temp:
                                if re.sub(':','',temp.find('span').text) == re.sub(':','',RemarkNumber):
                                    Remark = temp.text

                        else:
                            Remark = soup.find("p").text

                    #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
                    Name = BookMarkName
                    SearchWord = SearchWord
                    SpeakOrder = order
                    Speaker = Speaker
                    #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                    record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_ymn.columns)
                    df_ymn = df_ymn.append(record,ignore_index=True)

    except:
        error = 'error'
        Name = BookMarkName
        SearchWord = SearchWord
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_ymn.columns)
        df_ymn = df_ymn.append(record,ignore_index=True)
        browser.quit()
        
    return df_ymn


if __name__ == '__main__':
    yamanashi()
