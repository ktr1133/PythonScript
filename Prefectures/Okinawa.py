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

df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')


#沖縄
def okinawa(self):
    df_BookMarks = pd.read_csv('D://jupyter notebook/source/BookMarksCategorize.csv')
    SearchWord = self
    BookMarkURL = df_BookMarks[df_BookMarks['category']=='M']['URL'][46]
    BookMarkName = df_BookMarks[df_BookMarks['category']=='M']['name'][46]
    df_okn = pd.DataFrame(index=[], columns=['ID', 'Name', 'SearchWord', 'JournalTitle', 'SpeakOrder', 'Date', 'Speaker', 'PoliticalParty', 'Remark'])
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install())
        sleep(3)
        browser.get(BookMarkURL)
        wait = WebDriverWait(browser, 10)

        #ﾌﾚｰﾑ移動
        iframe = browser.find_element_by_css_selector('frame[scrolling="no"]')
        browser.switch_to_frame(iframe)

        #「キーワード検索」タグ選択
        browser.find_element_by_tag_name('form').find_element_by_css_selector('map[name="m_Sh"]').find_element_by_tag_name('area').click()

        #ﾌﾚｰﾑ移動
        browser.switch_to_default_content()
        browser.switch_to_frame('Main')

        #検索ワード入力
        browser.find_element_by_css_selector('input[name="QueryIn"]').send_keys(SearchWord)
        #検索実行
        sleep(2)
        browser.find_element_by_css_selector('button[type="submit"]').click()
        sleep(1)

        browser.switch_to_default_content()
        browser.switch_to_frame('View')

        tables = browser.find_element_by_tag_name('body').find_element_by_css_selector('form[name="_DominoForm"]').find_elements_by_tag_name('table')
        if len(tables) != 3:
            not_applicable = '該当する文書はありません。'
            #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
            Name = BookMarkName
            SearchWord = SearchWord
            #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
            record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_okn.columns)
            df_okn = df_okn.append(record,ignore_index=True) 
            browser.quit()

        else:
            trtags = browser.find_element_by_tag_name('body').find_element_by_css_selector('form[name="_DominoForm"]').find_elements_by_tag_name('table')[1].find_elements_by_tag_name('tr')
            num = 1
            for i in range(len(trtags)):
                trtags = browser.find_element_by_tag_name('body').find_element_by_css_selector('form[name="_DominoForm"]').find_elements_by_tag_name('table')[1].find_elements_by_css_selector('tr[valign="top"]')
                atag = trtags[i].find_elements_by_tag_name('td')[1].find_element_by_tag_name('a')
                if '年' in atag.text:
                    Speaker = atag.text.split('日')[1]
                    if '議長' not in Speaker and '委員長' not in Speaker:
                        if i>0:
                            if trtags[i].find_elements_by_tag_name('td')[1].find_element_by_tag_name('a').text.split('日')[0] != trtags[i-1].find_elements_by_tag_name('td')[1].find_element_by_tag_name('a').text.split('日')[0]:
                                num = 1
                            elif trtags[i].find_elements_by_tag_name('td')[1].find_element_by_tag_name('a').text.split('日')[0] == trtags[i-1].find_elements_by_tag_name('td')[1].find_element_by_tag_name('a').text.split('日')[0]:
                                num = num+1

                        atag.click()
                        sleep(3)
                        browser.switch_to_default_content()
                        browser.switch_to_frame('Main')
                        JDstep1 = browser.find_element_by_id('dochead')
                        JDstep2 = JDstep1.find_element_by_tag_name('table')
                        JDstep3 = JDstep2.find_element_by_tag_name('tr')
                        JDstep4 = JDstep3.find_elements_by_tag_name('td')[1]
                        JDstep5 = JDstep4.find_element_by_tag_name('table')
                        JDstep6 = JDstep5.find_element_by_tag_name('tr')
                        JDstep7 = JDstep6.find_elements_by_tag_name('td')
                        JournalTitle = JDstep7[0].text
                        Date = JournalTitle.split('年(')[0]+'年'+JDstep7[1].text.split('号')[1]
                        Rstep1 = browser.find_element_by_css_selector('div[class="allbody"]')
                        SpeakOrder = num
                        Remark = Rstep1.text
                        Name = BookMarkName
                        record = pd.Series(['', Name, SearchWord, JournalTitle, SpeakOrder, Date, Speaker, '', Remark], index=df_okn.columns)
                        df_okn = df_okn.append(record,ignore_index=True)
                    browser.switch_to_default_content()
                    browser.switch_to_frame('View')

                else:
                    if i == 0:
                        not_applicable = '該当する文書は存在しません。'
                        #ﾃﾞｰﾀﾌﾚｰﾑ入力用ﾚｺｰﾄﾞの要素
                        Name = BookMarkName
                        SearchWord = SearchWord
                        #ﾚｺｰﾄﾞ作成とﾃﾞｰﾀﾌﾚｰﾑに追加
                        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', not_applicable], index=df_okn.columns)
                        df_okn = df_okn.append(record,ignore_index=True) 
                        browser.quit()
                    break

    except:
        error = 'error'
        Name = BookMarkName
        record = pd.Series(['', Name, SearchWord, '', '', '', '', '', error], index=df_okn.columns)
        df_okn = df_okn.append(record,ignore_index=True)
        browser.quit()
                    
    return df_okn

if __name__ == '__main__':
    okinawa()
