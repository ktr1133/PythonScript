#!/usr/bin/env python
# coding: utf-8

#ﾃﾞｰﾀ読込
import glob

#正規表現
import re
import unicodedata
from re_self import re_df #作成

#和暦を西暦に変換
from jeraconv import jeraconv

#漢数字をアラビア数字に変換
from re_self import japanese2arabic

#処理測定
from tqdm import tqdm
import time

#日付取得
import datetime as dt

#ﾌｧｲﾙ移動等
import shutil
import os

# データの扱いに必要なライブラリ
import pandas as pd
import sqlite3
import numpy as np
import datetime as dt


def pluspp(df):
    """simple_search等で取得したデータフレームに政党又は非現職議員の属性を追加する関数
    注）データフレームの条件
    　①日付(Date)列は、年月日を含む　②SpeakerType列を含む"""
    #ﾃﾞｰﾀﾍﾞｰｽに接続して名簿ﾃﾞｰﾀをﾌﾚｰﾑとして読込
    db_name = 'D://jupyter notebook/LocalCouncilWebscraping/LocalJournal.db'
    conn = sqlite3.connect(db_name)
    sql_read = 'select * from councilors'
    df_list = pd.read_sql(sql_read,conn)
    df_list = df_list.drop('index', axis = 1)

    #検索結果のﾃﾞｰﾀﾌﾚｰﾑに政党の列を新規追加
    #ﾚｺｰﾄﾞに記載のある発言者名が、議員名簿ﾃﾞｰﾀに該当する場合、議員名簿ﾃﾞｰﾀから政党名を参照して検索結果のﾃﾞｰﾀﾌﾚｰﾑの政党名欄に値を入力
    df['political_party'] = ''
    for i in tqdm(list(df.query('SpeakerType == "議"').index)):
        for j in range(len(df_list)):
            try:
                if df_list['name1'][j] in df['Speaker'][i] :
                    df['political_party'][i] = df_list['political_party'][j]
            except:
                pass
        if df['political_party'][i] == '':
            df['political_party'][i] = '非現職議員'
            
    try:
        df = df.drop('Unnamed: 0', axis =1)
    except:
        pass

    return df

if __name__ == '__main__':
    pluspp()

def extractpp(df):
    """simple_search等で取得したデータフレームに現職議員であれば政党又は非現職議員の属性を追加し、
    現職議員の質問及び当該質問に対する行政答弁を抽出する関数
    注）データフレームの条件
    　①日付(Date)列は、年月日を含む　②SpeakerType列を含む"""
    #ﾃﾞｰﾀﾍﾞｰｽに接続して名簿ﾃﾞｰﾀをﾌﾚｰﾑとして読込
    db_name = 'D://jupyter notebook/LocalCouncilWebscraping/LocalJournal.db'
    conn = sqlite3.connect(db_name)
    sql_read = 'select * from councilors'
    df_list = pd.read_sql(sql_read,conn)
    df_list = df_list.drop('index', axis = 1)

    #検索結果のﾃﾞｰﾀﾌﾚｰﾑに政党の列を新規追加
    #ﾚｺｰﾄﾞに記載のある発言者名が、議員名簿ﾃﾞｰﾀに該当する場合、議員名簿ﾃﾞｰﾀから政党名を参照して検索結果のﾃﾞｰﾀﾌﾚｰﾑの政党名欄に値を入力
    df['political_party'] = ''
    for i in tqdm(list(df.query('SpeakerType == "議"').index)):
        for j in range(len(df_list)):
            try:
                if df_list['name1'][j] in df['Speaker'][i] :
                    df['political_party'][i] = df_list['political_party'][j]
            except:
                pass
        if df['political_party'][i] == '':
            df['political_party'][i] = '非現職議員'

    #検索用語を含む発言ﾚｺｰﾄﾞのうち、議員名簿ﾃﾞｰﾀに掲載のある発言者を含むﾚｺｰﾄﾞに対し、政党名を付与
    df2 = pd.DataFrame(index=[], columns=df.columns)
    for i in tqdm(range(len(df))):
        if len(df['political_party'][i]) > 1 and df['political_party'][i] != '非現職議員':
            df2 = df2.append(df.iloc[i], ignore_index=True)
    
    #同日の議会で行われた検索用語を含む発言を追加
    df3 = pd.DataFrame(index=[], columns=df.columns)
    for i in tqdm(range(len(df2))):
        if i>0:
            if df2['Name'][i] == df2['Name'][i-1] and df2['JournalTitle'][i] == df2['JournalTitle'][i-1] and df2['Date'][i] == df2['Date'][i-1]:
                pass
            else:
                for j in range(len(df)):
                    if df2['Name'][i] == df['Name'][j] and df2['JournalTitle'][i] == df['JournalTitle'][j] and df2['Date'][i] == df['Date'][j]:
                        df3 = df3.append(df.iloc[j], ignore_index=True)
        else:
            for j in range(len(df)):
                if df2['Name'][i] == df['Name'][j] and df2['JournalTitle'][i] == df['JournalTitle'][j] and df2['Date'][i] == df['Date'][j]:
                    df3 = df3.append(df.iloc[j], ignore_index=True)
    try:
        df3 = df3.drop('Unnamed: 0', axis =1)
    except:
        pass

    return df3

if __name__ == '__main__':
    extractpp()
