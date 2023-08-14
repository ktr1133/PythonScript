#!/usr/bin/env python
# coding: utf-8

#ﾃﾞｰﾀﾍﾞｰｽ操作用ﾗｲﾌﾞﾗﾘ
import sqlite3

import MeCab
import mojimoji
import pandas as pd
#正規表現
import re
import unicodedata
#ﾌｧｲﾙ操作
import os
import glob

#自身作成
from re_self import re_df #speakerの正規化、
import text_divide#文章分割

import pattern_kanji#正規表現パタンメソッド
import stype#発言者を議員か行政か判別
import pluspp #データフレームに政党追加し、不要なﾚｺｰﾄﾞを削除

#日付取得
import datetime as dt

#処理測定
from tqdm import tqdm

def text_to_words(text, stop_word_pass='D:/jupyter notebook/LocalCouncilWebscraping/stopwords/Japanese_textdivide.txt'):
    # stopword listをつくる
    stopword_list = []
    with open(stop_word_pass, 'r', encoding="utf-8") as f:
        stopword_list = f.readlines()
        
    stopword_list = [x.strip() for x in stopword_list if x.strip()] 
    #形態素解析を始める
    m = MeCab.Tagger('-d "C:/Program Files/MeCab/dic/ipadic"')
    m.parse('')
    #text = normalize_text(text)
    text = mojimoji.zen_to_han(text, kana=False)
    m_text = m.parse(text)
    basic_words = []
    #mecabの出力結果を単語ごとにリスト化
    m_text = m_text.split('\n')
    for row in m_text:
        #Tab区切りで形態素、その品詞等の内容と分かれているので単語部のみ取得
        word = row.split("\t")[0]
        #最終行はEOS
        if word == 'EOS':
            break
        else:
            pos = row.split('\t')[1]
            slice_ = pos.split(',')
            #品詞を取得する
            parts = slice_[0]
            if parts == '記号':
                continue

            #活用しない語についてはそのままの語を取得する
            elif slice_[0] =='名詞' and word not in stopword_list:
                basic_words.append(word)

    #basic_words = ' '.join(basic_words)
    
    return basic_words



def divide_remark(df):
    #議員の発言部を分割して抽出
    df['Remark_divide'] = ''
    for i in tqdm(range(len(df))):
        if df['SpeakerType'][i] == '議':
            temp_c = text_divide.divide_Qtex(df['Remark_re'][i])
            temp_c2 = []
            temp_c2_0 = []
            temp_c3 = []
            for j in range(len(temp_c)):
                if '\u3000' in df['SearchWord'][i]:
                    searchwords = re.split(r'\u3000', df['SearchWord'][i])
                    if (searchwords[0] in temp_c[j]) and (searchwords[1] in temp_c[j]):
                        temp_c2_0.append(j)
                    if len(temp_c2_0) > 0:
                        if (searchwords[0] in temp_c[j]) or (searchwords[1] in temp_c[j]):
                            searchwords = re.split(r' ', df['SearchWord'][i])
                            
                elif ' ' in df['SearchWord'][i]:
                    searchwords = re.split(r' ', df['SearchWord'][i])
                    if (searchwords[0] in temp_c[j]) and (searchwords[1] in temp_c[j]):
                        temp_c2_0.append(j)
                    if len(temp_c2_0) > 0:
                        if (searchwords[0] in temp_c[j]) or (searchwords[1] in temp_c[j]):
                            searchwords = re.split(r' ', df['SearchWord'][i])
                else:
                    if df['SearchWord'][i] in temp_c[j]:
                        temp_c2.append(j)

            if len(temp_c2) == 0:
                temp_c3 = ['No SearchWord in Remark']
            elif len(temp_c2) > 1:
                for k in temp_c2:
                    temp_c3.append(temp_c[k])
            else:
                temp_c3 = temp_c[temp_c2[0]]

            if len(temp_c3) == 1:
                df['Remark_divide'][i] = temp_c3[0]
            else:
                df['Remark_divide'][i] = ''.join(temp_c3)
                            
        elif df['SpeakerType'][i] == '行':
            temp_g = text_divide.divide_Atex(df['Remark_re'][i])
            temp_g2 = []
            temp_g2_0 = []
            temp_g3 = []
            for j in range(len(temp_g)):
                if '\u3000' in df['SearchWord'][i]:
                    searchwords = re.split(r'\u3000', df['SearchWord'][i])
                    if (searchwords[0] in temp_g[j]) and (searchwords[1] in temp_g[j]):
                        temp_g2_0.append(j)
                    if len(temp_g2_0) > 0:
                        if (searchwords[0] in temp_g[j]) or (searchwords[1] in temp_g[j]):
                            temp_g2.append(j)
                else:
                    if df['SearchWord'][i] in temp_g[j]:
                        temp_g2.append(j)
            if len(temp_g2) == 0:
                temp_g3 = ['No SearchWord in Remark']
            elif len(temp_g2) > 1:
                for k in temp_g2:
                    temp_g3.append(temp_g[k])
            else:
                temp_g3 = temp_g[temp_g2[0]]

            if len(temp_g3) == 1:
                df['Remark_divide'][i] = temp_g3[0]
            else:
                df['Remark_divide'][i] = ''.join(temp_g3)


    return df
