#!/usr/bin/env python
# coding: utf-8

#正規表現
import re
#処理測定
from tqdm import tqdm
#データ処理
import pandas as pd
import glob
import numpy as np

#自然言語処理
import MeCab
import mojimoji


def text_to_words(text, stop_word_pass='D:/jupyter notebook/LocalCouncilWebscraping/stopwords/Japanese.txt'):
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


def q_cate(df):
    """DataFrameを渡すと、質問の種別を質問種別欄に、ID欄に固有の値を入力して返す関数
    ●質問種別(Q_category)凡例
    　pa_eff_q：これまでの取組に関する質問、 fu_eff_q：今後の取組に関する質問、 gov_reco：行政の認識に関する質問
    　sug：今後の取組に関する提案、 req：行政への要望、 no_cate：上記以外のもの(質問文ではない討論等を抽出)
      several：複数問から成る質問
    ●同一文に複数の質問種別が当てはまった場合の優先順位
    　sug > req > fu_eff_q > pa_eff_q > gov_reco > no_cate
    ●ID入力規則
    　都道府県番号_会議日付_発言者種別_発言番号_質問回答種別_複数単数種別_番号/総番号
    ●ID入力時の凡例
    　pa_eff_q：p、　fu_eff_q：f、　gov_reco：g、　sug：s、　req：r、　no_cate：n
    ●データフレーム使用条件
     ・re_df.pyﾌｧｲﾙのre_speaker関数の使用
     ・stype.pyﾌｧｲﾙのstype関数の使用
     ・re_df.pyﾌｧｲﾙのre_remark関数の使用
     ・pluspp.pyﾌｧｲﾙのpluspp関数の使用
     ・re_df.pyﾌｧｲﾙのdate2yymmdd関数の使用
     ・PoliticalParty列の削除
     ・Remark列の削除
     ・divide_main.pyﾌｧｲﾙのdivide_remark関数の使用"""
    
    df['QA_category'] = ''
    df['Remark_words'] = ''
    
    #判別用ﾘｽﾄ
    verb_q = ['伺', 'でしょうか', 'お聞かせください', '求めます。','お尋ねします', '求め、', '求める',
              'します。', 'お尋ねいたします', 'お尋ねをいたします',  'いるのか。', 'ですか。',
              'いただきたい', 'お聞きしたい', '聞かせてください', '示してください', 'お示しください',
              'お願いします', 'について。', 'ください。', 'おりますか。', 'あります。', '承りたい',
              'お答えいただ']
    verb_sug = ['提案です', 'すべき', 'べき', 'こと。', '提言します']
    verb_req = ['要望します', '要望いたします', '要望させていただきます', '要望をいたします']
    verb_fu = ['していく']
    con_freq = ['最初に', 'まず、', '初めに、', '次に', '続いて、', '続きまして、', '次いで',
                '最後に', 'あわせて',
                '一つ目', '二つ目', '三つ目','四つ目','五つ目', '六つ目', '七つ目', '八つ目', '九つ目',
                '一点目', '二点目', '三点目', '四点目','五点目', '六点目', '七点目', '八点目',
                '九点目',
                '一点', '二点', '三点', '四点','五点', '六点','七点', '八点', '九点',
                '１点', '２点', '３点', '４点','５点', '６点', '７点', '８点', '９点',
                '１つ目', '２つ目', '３つ目', '４つ目','５つ目', '６つ目', '７つ目', '８つ目', '９つ目',
                '１点目', '２点目', '３点目', '４点目','５点目', '６点目', '７点目', '８点目', '９点目',
                '一、', '二、', '三、', '四、', '五、','六、', '七、', '八、', '九、', '十、',
                '(一)', '(二)', '(三)', '(四)', '(五)', '(六)','(七)', '(八)', '(九)', '(十)',
                '(1)', '(2)', '(3)', '(4)', '(5)', '(6)', '(7)', '(8)', '(9)', '(10)',
                'ア、', 'イ、', 'ウ、', 'エ、', 'オ、', 'カ、', 'キ、', 'ク、', 'ケ、', 'コ、',
                'サ、', 'シ、', 'ス、', 'セ、', 'ソ、',
                '第一', '第二', '第三', '第四', '第五', '第六', '第七', '第八', '第九']
    con_freq2 = ['また、']
    con_q = ['そこで、', 'このうち']
    noun_fu = ['今後', 'していく', '検討']
    noun_rec = ['お考え', '見解', '所見', '答弁', '思い', '御説明']
    noun_eff = ['現在', '現状', '状況', '取組', '施策', '理由', '効果', '取り組み']
    noun_sug = ['提案', '提言']
    noun_req = ['要望']
    adverb_q = ['として、', 'としての', '県の', '都の', '府の', '道の', '市町村の', '区市町村の',
                '県における', '都における', '府における', '道における' , '県内における',
                '都内における', '府内における', '道内における', '知事の']
    adverb_sug = ['考慮すべき', '思いますが、', '考えますが、', 'できないか、', '考えるが']
    adverb_sel = ['について', 'において、', 'は、']
    interrogative_w = ['どの', 'どれだけ', 'どういった', 'どのように', 'どのような',
                       'いかが', 'どう', 'のか、', 'どうか。']
    interrogative_v = ['どうか。', 'いかがか']
    demonstrative = ['そこで', 'このうち', 'これ', 'このこと', 'そのうち', 'このため', 'ただ、']

    for x in tqdm(list(df.query('SpeakerType == "議"').index)):
        self = df['Remark_divide'][x]
        divisions = re.split('(?<=。)(?=.)', self)

        temp = []
        #複数項目の質問の場合
        hanbetsu = pd.DataFrame(index=[], columns=['Order', 'Sentence', 'QA_category', 'ng_factor'])
        for i in range(len(divisions)):
            if divisions[i] != '':
                pa_eff_q = 0
                fu_eff_q = 0
                gov_reco = 0
                sug = 0
                req = 0
                negative_factor1 = 0
                negative_factor2 = 0
                negative_factor3 = 0
                negative_factor4 = 0
                negative_factor5 = 0
                negative_factor6 = 0
                negative_factor7 = 0
                negative_factor8 = 0
                negative_factor9 = 0
                negative_factor10 = 0
                negative_factor11 = 0
                negative_factor12 = 0
                negative_factor13 = 0
                negative_factor14 = 0
                negative_factor15 = 0
                negative_factor16 = 0
                negative_factor17 = 0
                negative_factor18 = 0
                negative_factor19 = 0
                negative_factor20 = 0
                negative_factor21 = 0
                negative_factor22 = 0
                #複数文因子の確認 freq
                freq = 0
                for aa in con_freq:
                    if aa in divisions[i]:
                        for ng in demonstrative:
                            if ng in divisions[i]:
                                negative_factor1 += 1
                        temp.append([i, 'freq', '', aa, divisions[i]])
                        freq += 1
                        record = pd.Series([i, divisions[i], 'freq', negative_factor1], index=hanbetsu.columns)
                        hanbetsu = hanbetsu.append(record, ignore_index=True)

                #複数文因子の確認2 freq
                for ab in con_freq2:
                    if ab in divisions[i]:
                        for e in verb_q:
                            if e in divisions[i]:
                                for ng in demonstrative:
                                    if ng in divisions[i]:
                                        negative_factor2 += 1
                                temp.append([i, 'freq', '', ab, e, divisions[i]])
                                freq += 1
                                record = pd.Series([i, divisions[i], 'freq', negative_factor2], index=hanbetsu.columns)
                                hanbetsu = hanbetsu.append(record, ignore_index=True)

                        #複数文因子の確認3 freq
                        for l in verb_fu:
                            if l in divisions[i]:
                                for ng in demonstrative:
                                    if ng in divisions[i]:
                                        negative_factor3 += 1
                                temp.append([i, 'freq', '', ab, l, divisions[i]])
                                freq += 1
                                record = pd.Series([i, divisions[i], 'freq', negative_factor3], index=hanbetsu.columns)
                                hanbetsu = hanbetsu.append(record, ignore_index=True)

                #現状の取組 a
                for b in adverb_q:
                    if b in divisions[i]:
                        for c in noun_eff:
                            if c in divisions[i]:
                                for e in verb_q:
                                    if e in divisions[i]:
                                        for ng in demonstrative:
                                            if ng in divisions[i]:
                                                negative_factor4 += 1
                                        temp.append([i, 'pa_eff_q', 'a', b, c, e, divisions[i]])
                                        pa_eff_q += 1
                                        record = pd.Series([i, divisions[i], 'pa_eff_q', negative_factor4], index=hanbetsu.columns)
                                        hanbetsu = hanbetsu.append(record, ignore_index=True)
                                        break

                        #行政の認識 b
                        for e in verb_q:
                            if e in divisions[i]:
                                for ng in demonstrative:
                                    if ng in divisions[i]:
                                        negative_factor5 += 1
                                temp.append([i, 'gov_reco', 'b', b, e, divisions[i]])
                                gov_reco += 1
                                record = pd.Series([i, divisions[i], 'gov_reco', negative_factor5], index= hanbetsu.columns)
                                hanbetsu = hanbetsu.append(record, ignore_index=True)
                                break

                #行政の認識 c
                for f in noun_fu:
                    if f in divisions[i]:
                        for d in adverb_sel:
                            if d in divisions[i]:
                                for g in noun_rec:
                                    if g in divisions[i]:
                                        for e in verb_q:
                                            if e in divisions[i]:
                                                for ng in demonstrative:
                                                    if ng in divisions[i]:
                                                        negative_factor20 += 1
                                                temp.append([i, 'gov_reco', 'c', f, d, g, e, divisions[i]])
                                                gov_reco += 1
                                                record = pd.Series([i, divisions[i], 'gov_reco', negative_factor20], index=hanbetsu.columns)
                                                hanbetsu = hanbetsu.append(record, ignore_index=True)
                                                break

                        #今後の取組d
                        if '取組' in divisions[i] or '取り組み' in divisions[i]:
                            for e in verb_q:
                                if e in divisions[i]:
                                    for ng in demonstrative:
                                        if ng in divisions[i]:
                                            negative_factor6 += 1
                                    temp.append([i, 'fu_eff_q', 'd', f, '取組', e, divisions[i]])
                                    fu_eff_q += 1
                                    record = pd.Series([i, divisions[i], 'fu_eff_q', negative_factor6], index=hanbetsu.columns)
                                    hanbetsu = hanbetsu.append(record, ignore_index=True)
                                    break

                #行政の認識 e
                for g in noun_rec:
                    if g in divisions[i]:
                        for e in verb_q:
                            if e in divisions[i]:
                                for ng in demonstrative:
                                    if ng in divisions[i]:
                                        negative_factor7 += 1
                                temp.append([i, 'gov_reco', 'e', g, e, divisions[i]])
                                gov_reco += 1
                                record = pd.Series([i, divisions[i], 'gov_reco', negative_factor7], index=hanbetsu.columns)
                                hanbetsu = hanbetsu.append(record, ignore_index=True)
                                break

                #現状の取組 f
                for c in noun_eff:
                    if c in divisions[i]:
                        for h in interrogative_w:
                            if h in divisions[i]:
                                for e in verb_q:
                                    if e in divisions[i]:
                                        for ng in demonstrative:
                                            if ng in divisions[i]:
                                                negative_factor8 += 1
                                        temp.append([i, 'pa_eff_q', 'f', c, h, e, divisions[i]])
                                        pa_eff_q += 1
                                        record = pd.Series([i, divisions[i], 'pa_eff_q', negative_factor8], index=hanbetsu.columns)
                                        hanbetsu = hanbetsu.append(record, ignore_index=True)
                                        break

                        #現状の取組f2
                        for p in interrogative_v:
                            if p in divisions[i]:
                                for ng in demonstrative:
                                    if ng in divisions[i]:
                                        negative_factor9 += 1
                                temp.append([i, 'pa_eff_q', 'f2', c, p, divisions[i]])
                                record = pd.Series([i, divisions[i], 'pa_eff_q', negative_factor9], index=hanbetsu.columns)
                                hanbetsu = hanbetsu.append(record, ignore_index=True)
                                break

                        #現状の取組 f3
                        for d in adverb_sel:
                            if d in divisions[i]:
                                for e in verb_q:
                                    if e in divisions[i]:
                                        for ng in demonstrative:
                                            if ng in divisions[i]:
                                                negative_factor10 += 1
                                        temp.append([i, 'pa_eff_q', 'f3', c, d, e, divisions[i]])
                                        pa_eff_q += 1
                                        record = pd.Series([i, divisions[i], 'pa_eff_q', negative_factor10], index=hanbetsu.columns)
                                        hanbetsu = hanbetsu.append(record, ignore_index=True)
                                        break

                #提案 g
                for h in interrogative_w:
                    if h in divisions[i]:
                        for j in verb_sug:
                            if j in divisions[i]:
                                for ng in demonstrative:
                                    if ng in divisions[i]:
                                        negative_factor11 += 1
                                temp.append([i, 'sug', 'g', h, j, divisions[i]])
                                sug += 1
                                record = pd.Series([i, divisions[i], 'sug', negative_factor11], index=hanbetsu.columns)
                                hanbetsu = hanbetsu.append(record, ignore_index=True)
                                break

                        #行政の認識 h
                        for b in adverb_q:
                            if b in divisions[i]:
                                for d in adverb_sel:
                                    if d in divisions[i]:
                                        for e in verb_q:
                                            if e in divisions[i]:
                                                for ng in demonstrative:
                                                    if ng in divisions[i]:
                                                        negative_factor12 += 1
                                                temp.append([i, 'gov_reco', 'h', h, b, d, e, divisions[i]])
                                                gov_reco += 1
                                                record = pd.Series([i, divisions[i], 'gov_reco', negative_factor12], index=hanbetsu.columns)
                                                hanbetsu = hanbetsu.append(record, ignore_index=True)
                                                break

                #提案 i
                for d in adverb_sel:
                    if d in divisions[i]:
                        for k in adverb_sug:
                            if k in divisions[i]:
                                for e in verb_q:
                                    if e in divisions[i]:
                                        for ng in demonstrative:
                                            if ng in divisions[i]:
                                                negative_factor13 += 1
                                        temp.append([i, 'sug', 'i', d, k, e, divisions[i]])
                                        sug += 1
                                        record = pd.Series([i, divisions[i], 'sug', negative_factor13], index=hanbetsu.columns)
                                        hanbetsu = hanbetsu.append(record, ignore_index=True)
                                        break

                #提案 j
                for k in adverb_sug:
                    if k in divisions[i]:
                        for e in verb_q:
                            if e in divisions[i]:
                                for ng in demonstrative:
                                    if ng in divisions[i]:
                                        negative_factor14 += 1
                                temp.append([i, 'sug', 'j', k, e, divisions[i]])
                                sug += 1
                                record = pd.Series([i, divisions[i], 'sug', negative_factor14], index=hanbetsu.columns)
                                hanbetsu = hanbetsu.append(record, ignore_index=True)
                                break

                #提案 j2
                for a in adverb_sug:
                    if a in divisions[i]:
                        for b in interrogative_v:
                            if b in divisions[i]:
                                for ng in demonstrative:
                                    if ng in divisions[i]:
                                        negative_factor15 += 1
                                temp.append([i, 'sug', 'j2', a, b, divisions[i]])
                                sug += 1
                                record = pd.Series([i, divisions[i], 'sug', negative_factor15], index=hanbetsu.columns)
                                hanbetsu = hanbetsu.append(record, ignore_index=True)
                                break

                #提案 j3
                for a in verb_sug:
                    if a in divisions[i]:
                        for b in con_freq:
                            if b in divisions[i]:
                                for ng in demonstrative:
                                    if ng in divisions[i]:
                                        negative_factor16 += 1
                                temp.append([i, 'sug', 'j3', a, b, divisions[i]])
                                sug += 1
                                record = pd.Series([i, divisions[i], 'sug', negative_factor16], index=hanbetsu.columns)
                                hanbetsu = hanbetsu.append(record, ignore_index=True)
                                break
                                
                #今後の取組_k
                for a in verb_sug:
                    if a in divisions[i]:
                        for l in verb_fu:
                            if l in divisions[i]:
                                for ng in demonstrative:
                                    if ng in divisions[i]:
                                        negative_factor17 += 1
                                temp.append([i, 'fu_eff_q', 'k', h, l, divisions[i]])
                                record = pd.Series([i, divisions[i], 'sug', negative_factor17], index=hanbetsu.columns)
                                hanbetsu = hanbetsu.append(record, ignore_index=True)
                                break

                #現状の取組_l
                for m in con_q:
                    if m in divisions[i]:
                        for d in adverb_sel:
                            if d in divisions[i]:
                                for e in verb_q:
                                    if e in divisions[i]:
                                        for ng in demonstrative:
                                            if ng in divisions[i]:
                                                negative_factor18 += 1
                                        temp.append([i, 'pa_eff_q', 'l', m , d , e, divisions[i]])
                                        record = pd.Series([i, divisions[i], 'pa_eff_q', negative_factor18], index=hanbetsu.columns)
                                        hanbetsu = hanbetsu.append(record, ignore_index=True)
                                        break

                #現状の取組_m
                for h in interrogative_w:
                    if h in divisions[i]:
                        for e in verb_q:
                            if e in divisions[i]:
                                for ng in demonstrative:
                                    if ng in divisions[i]:
                                        negative_factor19 += 1
                                temp.append([i, 'pa_eff_q', 'm', h , e, divisions[i]])
                                record = pd.Series([i, divisions[i], 'pa_eff_q', negative_factor19], index=hanbetsu.columns)
                                hanbetsu = hanbetsu.append(record, ignore_index=True)
                                break
                                
                #要望_n
                for a in verb_req:
                    if a in divisions[i]:
                        for ng in demonstrative:
                            if ng in divisions[i]:
                                negative_factor21 += 1
                        temp.append([i, 'req', 'n', a, divisions[i]])
                        record = pd.Series([i, divisions[i], 'req', negative_factor21], index=hanbetsu.columns)
                        hanbetsu = hanbetsu.append(record, ignore_index=True)
                        break
                        
                #現状の取組_o
                if len(hanbetsu.query('QA_category != "freq"')) == 0:
                    for e in verb_q:
                        if e in divisions[i]:
                            for d in adverb_sel:
                                if d in divisions[i]:
                                    for ng in demonstrative:
                                        if ng in divisions[i]:
                                            negative_factor22 += 1
                                    temp.append([i, 'pa_eff_q', 'o', e, d, divisions[i]])
                                    record = pd.Series([i, divisions[i], 'pa_eff_q', negative_factor22], index=hanbetsu.columns)
                                    hanbetsu = hanbetsu.append(record, ignore_index=True)
                                    break
                                    

        #同一文に複数の判別結果がある場合の処理（優先順位をつけ、重複分を削除）
        for i in range(len(hanbetsu)):
            for j in range(i+1, len(hanbetsu)):
                if hanbetsu['QA_category'][i] != 'freq' and\
                hanbetsu['QA_category'][i] != 'invalid' and\
                hanbetsu['Order'][i] == hanbetsu['Order'][j]:
                    if hanbetsu['QA_category'][i] == 'sug':
                        hanbetsu['QA_category'][j] = 'invalid'
                    elif hanbetsu['QA_category'][i] == 'req':
                        if hanbetsu['QA_category'][j] == 'sug':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'req':
                            hanbetsu['QA_category'][j] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'fu_eff_q':
                            hanbetsu['QA_category'][j] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'pa_eff_q':
                            hanbetsu['QA_category'][j] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'gov_reco':
                            hanbetsu['QA_category'][j] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'no_cate':
                            hanbetsu['QA_category'][j] = 'invalid'

                    elif hanbetsu['QA_category'][i] == 'fu_eff_q':
                        if hanbetsu['QA_category'][j] == 'sug':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'req':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'fu_eff_q':
                            hanbetsu['QA_category'][j] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'pa_eff_q':
                            hanbetsu['QA_category'][j] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'gov_reco':
                            hanbetsu['QA_category'][j] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'no_cate':
                            hanbetsu['QA_category'][j] = 'invalid'

                    elif hanbetsu['QA_category'][i] == 'pa_eff_q':
                        if hanbetsu['QA_category'][j] == 'sug':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'req':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'fu_eff_q':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'pa_eff_q':
                            hanbetsu['QA_category'][j] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'gov_reco':
                            hanbetsu['QA_category'][j] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'no_cate':
                            hanbetsu['QA_category'][j] = 'invalid'

                    elif hanbetsu['QA_category'][i] == 'gov_reco':
                        if hanbetsu['QA_category'][j] == 'sug':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'req':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'fu_eff_q':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'pa_eff_q':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'gov_reco':
                            hanbetsu['QA_category'][j] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'no_cate':
                            hanbetsu['QA_category'][j] = 'invalid'

                    elif hanbetsu['QA_category'][i] == 'no_cate':
                        if hanbetsu['QA_category'][j] == 'sug':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'req':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'fu_eff_q':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'pa_eff_q':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'gov_reco':
                            hanbetsu['QA_category'][i] = 'invalid'
                        elif hanbetsu['QA_category'][j] == 'no_cate':
                            hanbetsu['QA_category'][j] = 'invalid'

        hanbetsu = hanbetsu.query('QA_category != "invalid"').reset_index(drop=True)

        #質問種別に該当がない場合
        if len(hanbetsu) == 0:
            df['QA_category'][x] = 'no_ca'
            df['Remark_words'][x] = list(set(text_to_words(df['Remark_divide'][x])))
            df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+\
            '_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'no'+'_'+'1/1'

        else:
            #複数問から成る質問の場合の処理1
            if len(hanbetsu.query('QA_category == "freq"')) > 1 \
            and len(list(set(hanbetsu.query('QA_category == "freq"')['Order']))) > 1:
                sum_sev = 1
                for hb_b in range(len(hanbetsu)):
                    if hanbetsu['QA_category'][hb_b] == 'freq':
                        if hb_b == 0:
                            pass
                        else:
                            hb_n = 0
                            while hanbetsu['QA_category'][hb_b-1-hb_n] != 'freq':
                                sum_sev += 1
                                if hanbetsu['QA_category'][hb_b-1-hb_n] != 'freq':
                                    break
                                hb_n += 1

                            for hb_c in range(hb_b+1, len(hanbetsu)):
                                if hanbetsu['QA_category'][hb_c] != 'freq':
                                    sum_sev += 1
                                break

                bb = sum_sev
                num_sev = 1
                divide_tex_0 = []
                Order_tex_st = 0
                for hb in range(len(hanbetsu)):
                    if hanbetsu['QA_category'][hb] == 'freq':
                        if hb_b == 0:
                            pass
                        else:
                            for hb_i in range(hb):
                                if hanbetsu['QA_category'][hb-1-hb_i] != 'freq':
                                    Order_tex_st = hb
                                    Order_tex = hanbetsu['Order'][hb-1-hb_i]
                                    q_cate = hanbetsu['QA_category'][hb-1-hb_i]
                                    for hb_j in range(Order_tex):
                                        divide_tex_0.append(divisions[hb_j])
                                    divide_tex = ''.join(divide_tex_0)
                                    q_words = list(set(text_to_words(divide_tex)))

                                    aa = num_sev
                                    ID = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+\
                                    df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+\
                                    '_'+'sev'+'_'+str(aa)+'/'+str(bb)
                                    
                                    df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+\
                                    '_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+\
                                    '_'+'sev'+'_'+'origin'
                                    
                                    record = pd.Series([ID, df['Name'][x], df['SearchWord'][x],
                                                        df['JournalTitle'][x], df['SpeakOrder'][x], df['Date'][x],
                                                        df['Speaker'][x], df['SpeakerType'][x],df['political_party'][x],
                                                        df['ID'][x]+"と同じ", divide_tex, q_cate, q_words],
                                                       index=df.columns)
                                    df = df.append(record, ignore_index=True)
                                    df['QA_category'][x] = 'several'

                                    num_sev += 1

                                break

                            divide_tex_0 = []
                            Order_tex_st = 0
                            for hb_a in range(hb+1, len(hanbetsu)):
                                if hanbetsu['QA_category'][hb_a] != 'freq':
                                    Order_tex_en = hanbetsu['Order'][hb_a]
                                    for hb_k in range(Order_tex_st, Order_tex_en+1):
                                        divide_tex_0.append(divisions[hb_k])
                                    divide_tex = ''.join(divide_tex_0)
                                    q_words = list(set(text_to_words(divide_tex)))
                                    if hanbetsu['QA_category'][hb_a] == 'pa_eff_q':
                                        q_cate = 'pa_eff_q'
                                    elif hanbetsu['QA_category'][hb_a] == 'fu_eff_q':
                                        q_cate = 'fu_eff_q'
                                    elif hanbetsu['QA_category'][hb_a] == 'sug':
                                        q_cate = 'sug'
                                    elif hanbetsu['QA_category'][hb_a] == 'gov_reco' and\
                                    hanbetsu['QA_category'][hb_a] != 'sug':
                                        q_cate = 'gov_reco'
                                    elif hanbetsu['QA_category'][hb_a] == 'req' and\
                                    hanbetsu['QA_category'][hb_a] != 'sug' and\
                                    hanbetsu['QA_category'][hb_a] != 'gov_reco' and\
                                    hanbetsu['QA_category'][hb_a] != 'fu_eff_q':
                                        q_cate = 'req'
                                    aa = num_sev
                                    ID = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+\
                                    df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+\
                                    '_'+'sev'+'_'+str(aa)+'/'+str(bb)
                                    record = pd.Series([ID, df['Name'][x], df['SearchWord'][x],
                                                        df['JournalTitle'][x], df['SpeakOrder'][x], df['Date'][x],
                                                        df['Speaker'][x], df['SpeakerType'][x],df['political_party'][x],
                                                         df['Remark_re'][x], divide_tex, q_cate, q_words],
                                                       index=df.columns)
                                    df = df.append(record, ignore_index=True)
                                    df['QA_category'][x] = 'several'
                                    df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+\
                                    '_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+\
                                    '_'+'sev'+'_'+'origin'

                                    num_sev += 1
                                    Order_tex_st = hanbetsu['Order'][hb_a]+1

                                break
                                
            #複数問から成る質問の場合の処理2                    
            elif len(hanbetsu.query('QA_category == "freq"')) < 2 \
            and len(hanbetsu.query('QA_category != "freq"')) > 1:
                list_hb = hanbetsu.query('QA_category != "freq"').index
                sum_sev = 1
                for y in list_hb:
                    sum_sev += 1
                    
                bb = sum_sev
                num_sev = 1
                Order_tex_st = 0
                for y in list_hb:
                    Order_tex_en = hanbetsu['Order'][y]
                    divide_tex_0 = []
                    for a in range(Order_tex_st, Order_tex_en+1):
                        divide_tex_0.append(divisions[a])
                    divide_tex = ''.join(divide_tex_0)
                    q_words = list(set(text_to_words(divide_tex)))
                    q_cate = hanbetsu['QA_category'][y]
                    aa = num_sev
                    ID = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+\
                    df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+\
                    '_'+'sev'+'_'+str(aa)+'/'+str(bb)
                    record = pd.Series([ID, df['Name'][x], df['SearchWord'][x],
                                        df['JournalTitle'][x], df['SpeakOrder'][x], df['Date'][x],
                                        df['Speaker'][x], df['SpeakerType'][x],df['political_party'][x],
                                         df['Remark_re'][x], divide_tex, q_cate, q_words],
                                       index=df.columns)
                    df = df.append(record, ignore_index=True)
                    df['QA_category'][x] = 'several'
                    df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+\
                    '_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+\
                    '_'+'sev'+'_'+'origin'

                    num_sev += 1
                    Order_tex_st = hanbetsu['Order'][y]+1

            else:
                #単問から成る質問の場合
                if len(list(set(hanbetsu['QA_category']))) == 1 and list(set(hanbetsu['QA_category']))[0] == 'freq':
                    df['QA_category'][x] = 'no_ca'
                    df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+\
                    df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+\
                    '_'+'1/1'
                    df['Remark_words'][x] = list(set(text_to_words(df['Remark_divide'][x])))
                else:
                    df['QA_category'][x] = hanbetsu['QA_category'][len(hanbetsu)-1]
                    df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+\
                    df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+\
                    '_'+'1/1'
                    df['Remark_words'][x] = list(set(text_to_words(df['Remark_divide'][x])))

    return df

if __name__ == '__main__':
    q_cate()


def a_judge(self):
    """ﾃｷｽﾄを渡すと、回答の種別値を返す関数
    ●回答の種別
    posi：これまでの取組をさらに向上させる可能性を示唆する答弁 positive　
    neut：これまでの取組を向上させる可能性を示唆していない答弁 neutral
    ●データフレーム使用条件
     ・re_df.pyﾌｧｲﾙのre_speaker関数の使用
     ・stype.pyﾌｧｲﾙのstype関数の使用
     ・re_df.pyﾌｧｲﾙのre_remark関数の使用
     ・pluspp.pyﾌｧｲﾙのpluspp関数の使用
     ・re_df.pyﾌｧｲﾙのdate2yymmdd関数の使用
     ・PoliticalParty列の削除
     ・Remark列の削除
     ・divide_main.pyﾌｧｲﾙのdivide_remark関数の使用
     ・qa_cate.pyﾌｧｲﾙのq_cate関数の使用"""
    
    #判断素材
    verb_pa = ['まいりました', 'られる', 'しております', 'いるところであります', '行っております'
               , 'されています', 'いるところ', 'したところ', '始めたところ', 'まいりたい']
    verb_reco = ['考えており', '考えであります', '考えでございます', '考えております']
    verb_fu = ['する', 'させる', 'まいります', 'まいる', '行います', 'まいりたい']
    con_freq = ['最初に', 'まず、', '初めに、', '次に', '続いて、', '続きまして、', '次いで',
                '最後に', 'あわせて',
                '一つ目', '二つ目', '三つ目','四つ目','五つ目', '六つ目', '七つ目', '八つ目', '九つ目',
                '一点目', '二点目', '三点目', '四点目','五点目', '六点目', '七点目', '八点目',
                '九点目',
                '一点', '二点', '三点', '四点','五点', '六点','七点', '八点', '九点',
                '１点', '２点', '３点', '４点','５点', '６点', '７点', '８点', '９点',
                '１つ目', '２つ目', '３つ目', '４つ目','５つ目', '６つ目', '７つ目', '８つ目', '９つ目',
                '１点目', '２点目', '３点目', '４点目','５点目', '６点目', '７点目', '８点目', '９点目',
                '一、', '二、', '三、', '四、', '五、','六、', '七、', '八、', '九、', '十、',
                '(一)', '(二)', '(三)', '(四)', '(五)', '(六)','(七)', '(八)', '(九)', '(十)',
                '(1)', '(2)', '(3)', '(4)', '(5)', '(6)', '(7)', '(8)', '(9)', '(10)',
                'ア、', 'イ、', 'ウ、', 'エ、', 'オ、', 'カ、', 'キ、', 'ク、', 'ケ、', 'コ、',
                'サ、', 'シ、', 'ス、', 'セ、', 'ソ、',
                '第一', '第二', '第三', '第四', '第五', '第六', '第七', '第八', '第九']
    con_fu = ['このため', '今後、', 'おりますが']
    con_sev = ['とともに']
    con_posi = ['さらに', '一層']
    con_neut = ['引き続き', '今後とも']
    noun_reco = ['課題', '程度']
    nouns_posi = ['拡大', '充実', '強力', '積極', 'に加え、', '広く', '加えて、']

    divisions = re.split('(?<=。)(?=.)', self)

    tex = []

    posi = 0
    neut = 0
    no_ca = 0
    for i in tqdm(range(len(divisions))):
        temp1 = 0
        temp2 = 0
        temp3 = 0
        temp4 = 0
        if divisions[i] != '':
            for a in verb_pa:
                if a in divisions[i]:
                    temp1 += 1
                    tex.append([i, 'temp1', a, divisions[i]])

            if temp1 > 0:
                neut += 1
            else:
                for b in con_neut:
                    if b in divisions[i]:
                        temp2 += 1
                        tex.append([i, 'temp2', b, divisions[i]])

                if temp2 > 0:
                    neut += 1
                else:
                    for c in nouns_posi:
                        if c in divisions[i]:
                            for d in verb_fu:
                                if d in divisions[i]:
                                    temp3 += 1
                                    tex.append([i, 'temp3', c, d, divisions[i]])

                    if temp3 > 0:
                        posi += 1
                    else:
                        for d in verb_fu:
                            if d in divisions[i]:
                                temp4 += 1
                                tex.append([i, 'temp4', d, divisions[i]])

                        if temp4 > 0:
                            neut += 1
                        else:
                            no_ca += 1
                            tex.append([i, 'no_ca', divisions[i]])             

    if posi > 0:
        answer = 'posi'
    else:
        if neut > 0:
            answer = 'neut'
        else:
            if no_ca > 0:
                answer = 'no_ca'

    return answer
                
if __name__ == '__main__':
    a_judge()


def a_cate(df):
    """ﾃﾞｰﾀﾌﾚｰﾑを渡すと、発言者種別が行政のﾚｺｰﾄﾞを対象に、回答の対象となる質問を特定してkey値を入力し、
    特定した質問の種別に応じて回答の種別値を返す関数
    ●回答種別値凡例
     posi：これまでの取組をさらに向上させる可能性を示唆する回答、
     neut：これまでの取組を向上させる可能性を示唆していない回答、
     no_q：ﾃﾞｰﾀﾌﾚｰﾑ内に存在しない質問に対する回答、
     error：種別値no_caの質問に対する回答
     max_hits < 3：関連する質問が存在しない回答
    ●key値の入力規則
    　特定した質問のID値とする
    ●データフレーム使用条件
     ・re_df.pyﾌｧｲﾙのre_speaker関数の使用
     ・stype.pyﾌｧｲﾙのstype関数の使用
     ・re_df.pyﾌｧｲﾙのre_remark関数の使用
     ・pluspp.pyﾌｧｲﾙのpluspp関数の使用
     ・re_df.pyﾌｧｲﾙのdate2yymmdd関数の使用
     ・PoliticalParty列の削除
     ・Remark列の削除
     ・divide_main.pyﾌｧｲﾙのdivide_remark関数の使用
     ・qa_cate.pyﾌｧｲﾙのq_cate関数の使用
     ・qa_cate.pyﾌｧｲﾙのa_judge関数の使用"""
    
    df['key'] = ''
    for x in tqdm(list(df.query('SpeakerType == "行"').index)):
        if df['SpeakOrder'][x] == 1:
            df['QA_category'][x] = 'gov_speakorder_1'
            df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'1/1'
            df['Remark_words'][x] = 'invalid'
            df['key'] = 'invalid'
        else:
            key1 = df['Name'][x]
            key2 = df['JournalTitle'][x]
            key3 = df['Date'][x]
            q_list = list(df.query('Name == @key1 and JournalTitle == @key2 and Date == @key3 and SpeakerType == "議"').index)
            if q_list == []:
                df['key'][x] = 'invalid'
                df['Remark_words'][x] = text_to_words(df['Remark_divide'][x])
                df['QA_category'][x] = 'no_q'
                df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'answer'
            else:
                temp = []
                for a in q_list:
                    if (df['QA_category'][a] != 'several') and (df['QA_category'][a] != 'no_ca'):
                        if df['SpeakOrder'][x] > df['SpeakOrder'][a]:
                            temp.append(a)

                if len(temp) == 1:
                    df['key'][x] = df['ID'][temp[0]]
                    df['Remark_words'][x] = text_to_words(df['Remark_divide'][x])
                    if df['QA_category'][temp[0]] == 'pa_eff_q':
                        df['QA_category'][x] = 'neut'
                        df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'1/1'

                    elif df['QA_category'][temp[0]] == 'fu_eff_q':
                        df['QA_category'][x] = a_judge(df['Remark_divide'][x])
                        df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'1/1'

                    elif df['QA_category'][temp[0]] == 'gov_reco':
                        df['QA_category'][x] = a_judge(df['Remark_divide'][x])
                        df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'1/1'

                    elif df['QA_category'][temp[0]] == 'sug':
                        df['QA_category'][x] = a_judge(df['Remark_divide'][x])
                        df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'1/1'

                    elif df['QA_category'][temp[0]] == 'req':
                        df['QA_category'][x] = a_judge(df['Remark_divide'][x])
                        df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'1/1'

                    elif df['QA_category'][temp[0]] == 'no_ca':
                        df['QA_category'][x] = 'error'
                        df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'1/1'

                    elif df['QA_category'][temp[0]] == 'exclusion':
                        df['QA_category'][x] = 'error'
                        df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'1/1'

                    df['key'][temp[0]] = df['ID'][x]

                elif len(temp) > 1:
                    a_words = list(set(text_to_words(df['Remark_divide'][x])))
                    hit_list = {}
                    for y in temp:
                        hit = 0
                        for z in range(len(df['Remark_words'][y])):
                            for ele in a_words:
                                if ele == df['Remark_words'][y][z]:
                                    hit += 1
                        hit_list[y] = hit
                    max_hits = max(hit_list, key=hit_list.get)

                    if hit_list[max_hits] < 3:
                        df['key'][x] = df['ID'][max_hits]
                        df['Remark_words'][x] = text_to_words(df['Remark_divide'][x])
                        df['QA_category'][x] = 'max_hits < 3'
                        df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'answer'

                    else:
                        df['key'][x] = df['ID'][max_hits]
                        df['Remark_words'][x] = text_to_words(df['Remark_divide'][x])
                        if df['QA_category'][max_hits] == 'pa_eff_q':
                            df['QA_category'][x] = 'neut'
                            df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'answer'
                        elif df['QA_category'][max_hits] == 'fu_eff_q':
                            df['QA_category'][x] = a_judge(df['Remark_divide'][x])
                            df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'answer'
                        elif df['QA_category'][max_hits] == 'gov_reco':
                            df['QA_category'][x] = a_judge(df['Remark_divide'][x])
                            df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'answer'
                        elif df['QA_category'][max_hits] == 'sug':
                            df['QA_category'][x] = a_judge(df['Remark_divide'][x])
                            df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'answer'
                        elif df['QA_category'][max_hits] == 'req':
                            df['QA_category'][x] = a_judge(df['Remark_divide'][x])
                            df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'answer'
                        elif df['QA_category'][max_hits] == 'no_ca':
                            df['QA_category'][x] = 'error'
                            df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'answer'
                        elif df['QA_category'][max_hits] == 'exclusion':
                            df['QA_category'][x] = 'error'
                            df['ID'][x] = str(re.sub(r"\D", "", df['Name'][x]))+'_'+str(df['Date'][x])+'_'+df['Speaker'][x]+'_'+str(df['SpeakOrder'][x])+'_'+df['QA_category'][x]+'_'+'sin'+'_'+'answer'

                        df['key'][max_hits] = df['ID'][x]



    return df

if __name__ == '__main__':
    a_cate()

