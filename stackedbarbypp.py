#!/usr/bin/env python
# coding: utf-8

# In[35]:


#ﾃﾞｰﾀ編集
import pandas as pd
import numpy as np
import glob

#ﾌｧｲﾙ移動等
import shutil
import os

#正規表現
import re
from re_self import re_df #作成

#図形描画用
get_ipython().run_line_magic('matplotlib', 'inline')
# グラフ化に必要なものの準備
import matplotlib
import matplotlib.pyplot as plt

#日付取得
import datetime as dt

#政党追加
import pluspp


def new_dir(df):
    """作成したグラフを保存するためのﾌｫﾙﾀﾞを作成する関数。グラフ作成の前に実行する必要あり"""
    #グラフ画像保存先フォルダ作成
    new_dir_path = './sim_fig/{}_prefectures'.format(df['SearchWord'][0])
    try:
        os.mkdir(new_dir_path)
    except:
        pass


if __name__ == '__main__':
    new_dir()


#積み上げ棒グラフ作成
def stackedbarbypp(df, self):
    """正規化したﾃﾞｰﾀﾌﾚｰﾑと都道府県名※を渡すと、積み上げ棒グラフを作成する関数
    ※都道府県名
    01Hokkaido 02Aomori    03Iwate     04Miyagi    05Akita    06Yamagata  07Fukushima 08Ibaraki
    09Tochigi  10Gunma     11Saitama   12Chiba     13Tokyo    14Kanagawa  15Nigata    16Toyama
    17Ishikawa 18Fukui     19Yamanashi 20Nagano    21Gifu     22Shizuoka  23Aichi     24Mie
    25Shiga    26Kyoto     27Osaka     28Hyogo     29Nara     30Wakayama  31Tottori   32Shimane
    33Okayama  34Hiroshima 35Yamaguchi 36Tokushima 37Kagawa   38Ehime     39Kochi     40Fukuoka
    41Saga     42Nagasaki  43Kumamoto  44Oita      45Miyazaki 46Kagoshima 47Okinawa"""
    year = list(set(df['Date']))#dfから日付を集合として抽出してリスト化
    year = sorted(year)#上記でﾘｽﾄを昇順に並べ替え①
    table_columns = sorted(list(set(df['Date']))) # dfから日付を集合として抽出してリスト化して昇順に並べ替え
    table_columns.insert(0, 'political_party') #上記作成のﾘｽﾄの先頭にpolitical_partyを挿入②
    
    pp = list(set(df.query("Name == @self")['political_party'])) #指定した都道府県議会にける発言者の政党を集合として抽出し、リスト化③
    if pp == []:
        table = pd.DataFrame(index=[], columns= table_columns)
        list1 = []
        for ele2 in year:
            a = 0
            list1.append(a)
        list1.insert(0, '発言数0')
        record = pd.Series(list1, index=table.columns)
        table = table.append(record,ignore_index=True)
        table = table.set_index('political_party')
    else:
        table = pd.DataFrame(index=[], columns= table_columns) #②で作成したﾘｽﾄを列名として設定し、空のﾃｰﾌﾞﾙを作成
        for ele1 in pp: #③で作成した政党ﾘｽﾄの要素をｲﾝﾃﾞｯｸｽとして、①で作成した年別ﾘｽﾄを要素としたﾚｺｰﾄﾞを作成し、繰り返し処理にてﾃｰﾌﾞﾙを作成
            list1 = []
            for ele2 in year:
                if ele2 != "":
                    a = len(df.query("Name == @self & political_party == @ele1 & Date == @ele2"))
                    list1.append(a)
            list1.insert(0, ele1)
            record = pd.Series(list1, index=table.columns)
            table = table.append(record,ignore_index=True)
            
        for i in range(len(table['political_party'])): #政党未入力欄を行政答弁等に修正
            if table['political_party'][i] == '':
                table['political_party'][i] = "行政答弁等"
        table = table.set_index('political_party')
    
    #グラフ画像保存先フォルダ作成
    new_dir_path = './sim_fig/{}_prefectures'.format(df['SearchWord'][0])
    try:
        os.mkdir(new_dir_path)
    except:
        pass
    
    parameters = {'axes.labelsize': 15,'axes.titlesize': 20}
    plt.rcParams.update(parameters)
    fig, ax = plt.subplots(figsize=(20, 8))
    for i in range(len(table)):
        ax.bar(table.columns, table.iloc[i], bottom=table.iloc[:i].sum())
    for ele in table.columns:
        plt.text(x=ele, 
                 y=table[ele].sum()+0.5, 
                 s=table[ele].sum(), 
                 ha='center', 
                 fontsize=15)    
    ax.set(xlabel='year', ylabel='remarks')
    plt.title('政党等別年別発言数_{}_{}_{}'.format(df['SearchWord'][0], self, dt.datetime.now().strftime('%Y%m%d')), fontname="Meiryo")
    plt.xticks(fontsize=13 ,rotation=90)
    plt.yticks(fontsize=13)
    ylist = []
    for ele in table.columns:
        ylist.append(table[ele].sum())
    plt.ylim(0, max(ylist)+2)
    ax.legend(table.index, prop={'family':'Meiryo', 'size':'large'})
    figPath1 = '{}/政党等別年別発言数_{}_bar_{}_{}.png'.format(new_dir_path, self, df['SearchWord'][0], dt.datetime.now().strftime('%Y%m%d%H%M'))
    save = plt.savefig(figPath1)

    show = plt.show()
    
    return save, show 


if __name__ == '__main__':
    stackedbarbypp()

