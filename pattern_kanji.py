#!/usr/bin/env python
# coding: utf-8

# In[3]:


#正規表現
import re
# データの扱いに必要なライブラリ
import pandas as pd


# In[ ]:


#常用漢字　https://raw.githubusercontent.com/cjkvi/cjkvi-tables/master/joyo2010.txt
#url = 'https://raw.githubusercontent.com/cjkvi/cjkvi-tables/15569eaae99daef9f99f0383e9d8efbec64a7c5a/joyo2010.txt'
#kanji_df = pd.read_csv(url, header=None, skiprows=1, delimiter='\t')

#kanji = ''.join(kanji_df.iloc[:, 0])
#pattern = re.compile(r'[{}]+（[{}]+君）'.format(kanji, kanji))


# In[9]:


def pattern_h():
    """対象：大阪、山口"""
    pattern = re.compile(r'.+?（.+?君）')

    return pattern

if __name__ == '__main__':
    pattern_h()

    
def pattern_hh():
    """対象：石川"""
    pattern = re.compile(r'.+?\(.+?\)')

    return pattern

if __name__ == '__main__':
    pattern_hh()
    

def pattern_i():
    """対象：静岡"""
    pattern = re.compile(r'○.+?（.+?')

    return pattern

if __name__ == '__main__':
    pattern_i()

    

def pattern_j():
    """対象：和歌山、京都、広島"""
    pattern = re.compile(r'[○|〇|◯].+?（.+?君')

    return pattern

if __name__ == '__main__':
    pattern_j()

