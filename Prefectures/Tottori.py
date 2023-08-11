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

import traceback

#鳥取
def tottori(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='K']['URL'][30]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='K']['name'][30]
    df_ttr = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        #frameに移動
        browser.switch_to_frame('search')

        #検索ワード入力
        browser.find_element_by_id('search').find_element_by_css_selector('input[name="Phrase[]"]').send_keys(SearchWord)
        #検索実行
        browser.find_element_by_css_selector('input[value="  検　索  "]').click()
        browser.implicitly_wait(5)

        browser.switch_to.window(browser.window_handles[-1])

        #該当なしの場合
        nohit_tex = browser.find_element_by_css_selector('div[class="result"]').text
        if '該当する文書がありません。' in nohit_tex:
            not_applicable = '該当する文書は存在しません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_ttr.columns)
            df_ttr = df_ttr.append(record,ignore_index=True) 
            browser.quit()

        #該当ありの場合
        else:
            dttags = browser.find_element_by_id('list').find_element_by_css_selector('div[class="result"]').find_elements_by_tag_name('dt')
            for i in range(len(dttags)):
                dttags = browser.find_element_by_id('list').find_element_by_css_selector('div[class="result"]').find_elements_by_tag_name('dt')
                Date = dttags[i].find_elements_by_tag_name('span')[1].text
                JournalTitle = dttags[i].find_element_by_tag_name('a').text
                dttags[i].find_element_by_tag_name('a').click()
                browser.implicitly_wait(10)
                #ﾌﾚｰﾑ移動
                browser.switch_to_frame('Voicelist')
                allSpeakers = browser.find_element_by_id('doc-speaker').find_element_by_tag_name('ul').find_elements_by_tag_name('li')
                num = 1
                for j in range(len(allSpeakers)):
                    allSpeakers = browser.find_element_by_id('doc-speaker').find_element_by_tag_name('ul').find_elements_by_tag_name('li')
                    if allSpeakers[j].find_element_by_tag_name('a').get_attribute('class') == 'Hit':
                        Speaker = allSpeakers[j].find_elements_by_tag_name('span')[1].text
                        if '議長' not in Speaker and '委員長' not in Speaker:
                            SpeakOrder = num
                            allSpeakers[j].click()
                            browser.implicitly_wait(10)
                            #ﾌﾚｰﾑ移動
                            browser.switch_to_default_content()
                            browser.switch_to_frame('Page')
                            #発言部探索
                            Remark = browser.find_element_by_css_selector('div[class="textcol"]').find_element_by_tag_name('p').text
                            Name = BookMarkName
                            record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_ttr.columns)
                            df_ttr = df_ttr.append(record,ignore_index=True)
                            num = num+1
                        browser.switch_to_default_content()
                        browser.switch_to.frame('Voicelist')
                browser.switch_to_default_content()
                browser.switch_to.frame('Command')
                browser.find_element_by_css_selector('input[value="一覧に戻る"]').click()
                browser.implicitly_wait(10)

            nextlinks = browser.find_element_by_css_selector('div[class="pagination"]').find_element_by_tag_name('ul').find_elements_by_tag_name('li')
            while nextlinks[-1].get_attribute('class') !='disabled':
                nextlinks = browser.find_element_by_css_selector('div[class="pagination"]').find_element_by_tag_name('ul').find_elements_by_tag_name('li')
                nextlinks[-1].click()

                dttags = browser.find_element_by_id('list').find_element_by_css_selector('div[class="result"]').find_elements_by_tag_name('dt')
                for i in range(len(dttags)):
                    dttags = browser.find_element_by_id('list').find_element_by_css_selector('div[class="result"]').find_elements_by_tag_name('dt')
                    Date = dttags[i].find_elements_by_tag_name('span')[1].text
                    JournalTitle = dttags[i].find_element_by_tag_name('a').text
                    dttags[i].find_element_by_tag_name('a').click()
                    browser.implicitly_wait(10)
                    #ﾌﾚｰﾑ移動
                    browser.switch_to_frame('Voicelist')
                    allSpeakers = browser.find_element_by_id('doc-speaker').find_element_by_tag_name('ul').find_elements_by_tag_name('li')
                    num = 1
                    for j in range(len(allSpeakers)):
                        allSpeakers = browser.find_element_by_id('doc-speaker').find_element_by_tag_name('ul').find_elements_by_tag_name('li')
                        if allSpeakers[j].find_element_by_tag_name('a').get_attribute('class') == 'Hit':
                            Speaker = allSpeakers[j].find_elements_by_tag_name('span')[1].text
                            if '議長' not in Speaker and '委員長' not in Speaker:
                                SpeakOrder = num
                                allSpeakers[j].click()
                                browser.implicitly_wait(10)
                                #ﾌﾚｰﾑ移動
                                browser.switch_to_default_content()
                                browser.switch_to_frame('Page')
                                #発言部探索
                                Remark = browser.find_element_by_css_selector('div[class="textcol"]').find_element_by_tag_name('p').text
                                Name = BookMarkName
                                record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_ttr.columns)
                                df_ttr = df_ttr.append(record,ignore_index=True)
                                num = num+1
                            browser.switch_to_default_content()
                            browser.switch_to.frame('Voicelist')
                    browser.switch_to_default_content()
                    browser.switch_to.frame('Command')
                    browser.find_element_by_css_selector('input[value="一覧に戻る"]').click()
                    browser.implicitly_wait(10)
                nextlinks = browser.find_element_by_css_selector('div[class="pagination"]').find_element_by_tag_name('ul').find_elements_by_tag_name('li')

            browser.quit()

    except:
        error = 'error'
        msg = traceback.format_exc()
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error+" "+msg], index=df_ttr.columns)
        df_ttr = df_ttr.append(record,ignore_index=True)
        browser.quit()
    
    return df_ttr


if __name__ == '__main__':
    tottori()
