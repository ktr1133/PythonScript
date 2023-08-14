#!/usr/bin/env python
# coding: utf-8

# In[8]:


#正規表現
import re
# データの扱いに必要なライブラリ
import pandas as pd
#漢字を含む正規表現パタンメソッド
import pattern_kanji


# In[27]:


def stype(df):
    df['SpeakerType'] = ''
    pattern_h = pattern_kanji.pattern_h()
    pattern_hh = pattern_kanji.pattern_hh()
    pattern_i = pattern_kanji.pattern_i()
    pattern_j = pattern_kanji.pattern_j()
    for i in range(len(df)):
        try:
            #pattern_a
            if 'Hokkai' in df['Name'][i] or 'Aomori' in df['Name'][i]  or 'Miyagi' in df['Name'][i] or 'Akita' in df['Name'][i] or 'Yamagata' in df['Name'][i] or 'Fukushima' in df['Name'][i] or 'Ibaraki' in df['Name'][i] or 'Tochigi' in df['Name'][i] or 'Saitama' in df['Name'][i] or 'Tokyo' in df['Name'][i] or 'Toyama' in df['Name'][i] or 'Fukui' in df['Name'][i] or 'Nagano' in df['Name'][i] or 'Gifu' in df['Name'][i] or 'Aichi' in df['Name'][i] or 'Aichi' in df['Name'][i] or 'Mie' in df['Name'][i] or 'Shiga' in df['Name'][i] or 'Nara' in df['Name'][i] or 'Tottori' in df['Name'][i] or 'Okayama' in df['Name'][i] or 'Tokushima' in df['Name'][i] or 'Kochi' in df['Name'][i] or 'Fukuoka' in df['Name'][i] or 'Nagasaki' in df['Name'][i]:
                if '番' in df['Speaker'][i]:
                    df['SpeakerType'][i] = '議'
                else:
                    df['SpeakerType'][i] = '行'
            #pattern_ab
            elif 'Akita' in df['Name'][i] or 'Yamagata' in df['Name'][i]:
                if '番' in df['Speaker'][i] or '議員' in df['Speaker'][i]:
                    df['SpeakerType'][i] = '議'
                else:
                    df['SpeakerType'][i] = '行'
            #pattern_ac
            elif 'Miyagi' in df['Name'][i]:
                if '番' in df['Speaker'][i] or '（' not in df['Speaker'][i]:
                    df['SpeakerType'][i] = '議'
                else:
                    df['SpeakerType'][i] = '行'
            #pattern_b
            elif 'Iwate' in df['Name'][i] or 'Gunma' in df['Name'][i] or 'Shimane' in df['Name'][i] or 'Oita' in df['Name'][i] or 'Miyazaki' in df['Name'][i]:
                if '議員' in df['Speaker'][i]:
                    df['SpeakerType'][i] = '議'
                else:
                    df['SpeakerType'][i] = '行'
            #pattern_c
            elif 'Kanagawa' in df['Name'][i] or 'Nigata' in df['Name'][i] or 'Yamanashi' in df['Name'][i] or 'Kagawa' in df['Name'][i] or 'Kagoshima' in df['Name'][i] or 'Okinawa' in df['Name'][i]:
                if '（' not in df['Speaker'][i]:
                    df['SpeakerType'][i] = '議'
                else:
                    df['SpeakerType'][i] = '行'
            #pattern_d
            elif 'Kumamoto' in df['Name'][i] :
                if '◎' in df['Speaker'][i]:
                    df['SpeakerType'][i] = '行'
                else:
                    df['SpeakerType'][i] = '議'        
            #pattern_e
            elif  'Saga' in df['Name'][i]:
                if '君' in df['Speaker'][i]:
                    df['SpeakerType'][i] = '議'
                else:
                    df['SpeakerType'][i] = '行'
            #pattern_f
            elif  'Hyogo' in df['Name'][i] or 'Ehime' in df['Name'][i]:
                if '議員' in df['Speaker'][i]:
                    df['SpeakerType'][i] = '議'
                elif '（' not in df['SpeakerType'][i] and '君' in df['SpeakerType'][i]:
                    df['SpeakerType'][i] = '議'
                else:
                    df['SpeakerType'][i] = '行'
            #pattern_g
            elif  'Chiba' in df['Name'][i]:
                if '説明者' in df['Speaker'][i]:
                    df['SpeakerType'][i] = '行'
                elif '知事' in df['Speaker'][i]:
                    df['SpeakerType'][i] = '行'
                else:
                    df['SpeakerType'][i] = '議'
            #pattern_h
            elif  'Osaka' in df['Name'][i] or 'Yamaguchi' in df['Name'][i]:
                if pattern_h.match(df['Speaker'][i]):
                    df['SpeakerType'][i] = '行'
                else:
                    df['SpeakerType'][i] = '議'
            #pattern_hh
            elif 'Ishikawa' in df['Name'][i]:
                if pattern_hh.match(df['Speaker'][i]):
                    df['SpeakerType'][i] = '行'
                else:
                    df['SpeakerType'][i] = '議'
            #pattern_i
            elif  'Shizuoka' in df['Name'][i]:
                if pattern_i.match(df['Speaker'][i]):
                    df['SpeakerType'][i] = '行'
                else:
                    df['SpeakerType'][i] = '議'
            #pattern_j
            elif  'Wakayama' in df['Name'][i] or 'Kyoto' in df['Name'][i] or 'Hiroshima' in df['Name'][i]:
                if pattern_j.match(df['Speaker'][i]):
                    df['SpeakerType'][i] = '行'
                else:
                    df['SpeakerType'][i] = '議'
        except:
            pass
    return df


# In[ ]:


if __name__ == '__main__':
    stype()

